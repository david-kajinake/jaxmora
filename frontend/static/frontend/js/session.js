const API_ROOT = '/api/';
const ACCESS_TOKEN_KEY = 'jaxmora_access_token';
const REFRESH_TOKEN_KEY = 'jaxmora_refresh_token';

let refreshPromise = null;

const tokenStore = {
  get access() { return localStorage.getItem(ACCESS_TOKEN_KEY); },
  get refresh() { return localStorage.getItem(REFRESH_TOKEN_KEY); },
  save({ access, refresh }) {
    if (access) localStorage.setItem(ACCESS_TOKEN_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
  },
  clear() {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },
};

const getErrorMessage = async (response) => {
  let payload;
  try { payload = await response.json(); } catch { return 'Something went wrong. Please try again.'; }
  if (typeof payload?.detail === 'string') return payload.detail;
  if (typeof payload === 'object' && payload) {
    return Object.entries(payload)
      .map(([field, messages]) => `${field.replaceAll('_', ' ')}: ${Array.isArray(messages) ? messages.join(' ') : messages}`)
      .join(' ');
  }
  return 'Something went wrong. Please try again.';
};

const setAlert = (selector, message, success = false) => {
  const alert = typeof selector === 'string' ? document.querySelector(selector) : selector;
  if (!alert) return;
  alert.textContent = message;
  alert.hidden = !message;
  alert.classList.toggle('account-alert-success', success);
  alert.classList.toggle('form-alert-success', success);
};

const refreshAccessToken = async () => {
  if (!tokenStore.refresh) return false;
  if (!refreshPromise) {
    refreshPromise = fetch(`${API_ROOT}auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: tokenStore.refresh }),
    })
      .then(async (response) => {
        if (!response.ok) throw new Error('The session has expired.');
        const tokens = await response.json();
        tokenStore.save(tokens);
        return true;
      })
      .catch(() => {
        tokenStore.clear();
        return false;
      })
      .finally(() => { refreshPromise = null; });
  }
  return refreshPromise;
};

const apiRequest = async (path, options = {}, retry = true) => {
  const headers = new Headers(options.headers || {});
  if (tokenStore.access) headers.set('Authorization', `Bearer ${tokenStore.access}`);
  const response = await fetch(`${API_ROOT}${path.replace(/^\//, '')}`, {
    ...options,
    headers,
  });
  if (response.status === 401 && retry && await refreshAccessToken()) {
    return apiRequest(path, options, false);
  }
  return response;
};

const loginUser = async (username, password) => {
  const response = await fetch(`${API_ROOT}auth/token/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!response.ok) throw new Error(await getErrorMessage(response));
  tokenStore.save(await response.json());
};

const logoutUser = async () => {
  const refresh = tokenStore.refresh;
  try {
    if (refresh) {
      await fetch(`${API_ROOT}auth/logout/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      });
    }
  } finally {
    tokenStore.clear();
  }
};

const getCurrentUser = async () => {
  if (!tokenStore.access && !tokenStore.refresh) return null;
  const response = await apiRequest('auth/me/');
  if (!response.ok) return null;
  return response.json();
};

const createLink = (href, label, className = '') => {
  const link = document.createElement('a');
  link.href = href;
  link.textContent = label;
  if (className) link.className = className;
  return link;
};

const bindAccountMenu = (menu) => {
  const trigger = menu.querySelector('.account-menu-trigger');
  const dropdown = menu.querySelector('.account-dropdown');
  trigger.addEventListener('click', (event) => {
    event.stopPropagation();
    const willOpen = dropdown.hidden;
    document.querySelectorAll('.account-dropdown').forEach((item) => { item.hidden = true; });
    document.querySelectorAll('.account-menu-trigger').forEach((item) => item.setAttribute('aria-expanded', 'false'));
    dropdown.hidden = !willOpen;
    trigger.setAttribute('aria-expanded', String(willOpen));
  });
  menu.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      dropdown.hidden = true;
      trigger.setAttribute('aria-expanded', 'false');
      trigger.focus();
    }
  });
};

const renderAuthControls = (user) => {
  document.querySelectorAll('[data-auth-controls]').forEach((container) => {
    const urls = container.dataset;
    container.replaceChildren();
    if (!user) {
      container.append(
        createLink(urls.loginUrl, 'Sign in'),
        createLink(urls.signupUrl, 'Join JAXMORA', 'button button-small'),
      );
      return;
    }
    const menu = document.createElement('div');
    menu.className = 'account-menu';
    const trigger = document.createElement('button');
    trigger.className = 'button button-small account-menu-trigger';
    trigger.type = 'button';
    trigger.setAttribute('aria-haspopup', 'menu');
    trigger.setAttribute('aria-expanded', 'false');
    trigger.textContent = user.first_name || user.username;
    const chevron = document.createElement('span');
    chevron.className = 'account-menu-chevron';
    chevron.setAttribute('aria-hidden', 'true');
    chevron.textContent = '⌄';
    trigger.append(chevron);
    const dropdown = document.createElement('div');
    dropdown.className = 'account-dropdown';
    dropdown.setAttribute('role', 'menu');
    dropdown.hidden = true;
    [
      [urls.homeUrl, 'Home'],
      [urls.dashboardUrl, 'Dashboard'],
      [urls.profileUrl, 'Profile'],
      [urls.settingsUrl, 'Settings'],
      [urls.privacyUrl, 'Privacy policy'],
      [urls.termsUrl, 'Terms of service'],
    ].forEach(([href, label], index) => {
      if (index === 4) {
        const divider = document.createElement('div');
        divider.className = 'account-dropdown-divider';
        divider.setAttribute('role', 'separator');
        dropdown.append(divider);
      }
      const link = createLink(href, label);
      link.setAttribute('role', 'menuitem');
      dropdown.append(link);
    });
    const logout = document.createElement('button');
    logout.type = 'button';
    logout.textContent = 'Logout';
    logout.setAttribute('role', 'menuitem');
    logout.dataset.jwtLogout = '';
    dropdown.append(logout);
    menu.append(trigger, dropdown);
    container.append(menu);
    bindAccountMenu(menu);
  });
};

const applyPreferences = (preferences = {}) => {
  const { language = 'en', font_size: fontSize = 'medium', font_family: fontFamily = 'dm-sans' } = preferences;
  document.documentElement.lang = language;
  document.documentElement.dataset.fontSize = fontSize;
  document.body.dataset.fontFamily = fontFamily;
};

const loadDashboard = async () => {
  const dashboard = document.querySelector('[data-jwt-dashboard]');
  if (!dashboard) return;
  const response = await apiRequest('dashboard/');
  if (!response.ok) throw new Error(await getErrorMessage(response));
  const data = await response.json();
  ['total_views', 'total_likes', 'total_uploads'].forEach((key) => {
    const target = dashboard.querySelector(`[data-analytics="${key}"]`);
    if (target) target.textContent = data[key];
  });
  const list = dashboard.querySelector('[data-recent-uploads]');
  const empty = dashboard.querySelector('[data-empty-uploads]');
  list.replaceChildren();
  empty.hidden = Boolean(data.recent_uploads.length);
  data.recent_uploads.forEach((item) => {
    const article = document.createElement('article');
    const tag = document.createElement('span');
    tag.className = 'content-type-tag';
    tag.textContent = item.type;
    const copy = document.createElement('div');
    const title = document.createElement('h3');
    title.textContent = item.title;
    const date = document.createElement('p');
    date.textContent = `Uploaded ${new Date(`${item.uploaded_at}T00:00:00`).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}`;
    const status = document.createElement('span');
    status.className = 'upload-status';
    status.textContent = 'Published';
    copy.append(title, date);
    article.append(tag, copy, status);
    list.append(article);
  });
};

const setEpisodeControls = (form) => {
  const rows = [...form.querySelectorAll('[data-episode-row]')];
  rows.forEach((row, index) => {
    row.querySelector('[data-episode-label]').textContent = index + 1;
    row.querySelector('[data-remove-episode]').hidden = rows.length === 1;
  });
  const total = form.querySelector('[name$="-TOTAL_FORMS"]');
  if (total) total.value = rows.length;
};

const addEpisodeRow = (form) => {
  const list = form.querySelector('[data-episode-list]');
  const index = list.querySelectorAll('[data-episode-row]').length;
  const row = document.createElement('fieldset');
  row.className = 'episode-upload-row';
  row.dataset.episodeRow = '';
  row.innerHTML = `
    <legend>Episode <span data-episode-label>${index + 1}</span></legend>
    <button class="remove-episode" type="button" data-remove-episode aria-label="Remove episode">×</button>
    <div class="form-field"><label for="id_episodes-${index}-name">Episode title</label><input id="id_episodes-${index}-name" name="episodes-${index}-name" maxlength="255" required></div>
    <div class="form-field"><label for="id_episodes-${index}-ref_number">Episode number</label><input id="id_episodes-${index}-ref_number" name="episodes-${index}-ref_number" type="number" min="1" required></div>
    <div class="form-field"><label for="id_episodes-${index}-video">Episode video</label><input id="id_episodes-${index}-video" name="episodes-${index}-video" type="file" accept="video/*" required></div>`;
  list.append(row);
  setEpisodeControls(form);
};

const setupDashboard = () => {
  const dashboard = document.querySelector('[data-jwt-dashboard]');
  if (!dashboard) return;
  const alert = dashboard.querySelector('[data-dashboard-alert]');
  const typePicker = dashboard.querySelector('[data-upload-type-picker]');
  const uploadPanels = [...dashboard.querySelectorAll('[data-upload-form-panel]')];
  const contentForms = [...dashboard.querySelectorAll('[data-content-upload-form]')];
  const serieForm = dashboard.querySelector('[data-serie-upload-form]');
  const showUploadForm = (type) => {
    uploadPanels.forEach((panel) => {
      panel.hidden = panel.dataset.uploadFormPanel !== type;
    });
  };
  typePicker?.addEventListener('change', (event) => {
    if (event.target.matches('[data-upload-type-control]')) {
      showUploadForm(event.target.value);
    }
  });
  const selectedType = typePicker?.querySelector('[data-upload-type-control]:checked')?.value;
  if (selectedType) showUploadForm(selectedType);
  contentForms.forEach((contentForm) => contentForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!contentForm.reportValidity()) return;
    setAlert(alert, '');
    const response = await apiRequest('content/upload/', { method: 'POST', body: new FormData(contentForm) });
    if (!response.ok) return setAlert(alert, await getErrorMessage(response));
    contentForm.reset();
    setAlert(alert, 'Your content has been uploaded and is ready to manage.', true);
    await loadDashboard();
  }));
  serieForm?.addEventListener('click', (event) => {
    if (event.target.closest('[data-add-episode]')) addEpisodeRow(serieForm);
    const remove = event.target.closest('[data-remove-episode]');
    if (remove) {
      remove.closest('[data-episode-row]').remove();
      setEpisodeControls(serieForm);
    }
  });
  serieForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!serieForm.reportValidity()) return;
    setAlert(alert, '');
    const source = new FormData(serieForm);
    const payload = new FormData();
    ['title', 'description', 'price', 'year_released', 'category', 'season_number', 'season_name', 'season_year'].forEach((field) => payload.append(field, source.get(field) || ''));
    const episodes = [];
    [...serieForm.querySelectorAll('[data-episode-row]')].forEach((row, index) => {
      const name = row.querySelector('[name$="-name"]').value;
      const refNumber = row.querySelector('[name$="-ref_number"]').value;
      const video = row.querySelector('[name$="-video"]').files[0];
      episodes.push({ name, ref_number: Number(refNumber) });
      payload.append(`episode_file_${index}`, video);
    });
    payload.append('episodes', JSON.stringify(episodes));
    const response = await apiRequest('series/upload/', { method: 'POST', body: payload });
    if (!response.ok) return setAlert(alert, await getErrorMessage(response));
    serieForm.reset();
    const list = serieForm.querySelector('[data-episode-list]');
    while (list.querySelectorAll('[data-episode-row]').length > 1) list.lastElementChild.remove();
    setEpisodeControls(serieForm);
    setAlert(alert, 'Your series, season, and episodes have been published.', true);
    await loadDashboard();
  });
  setEpisodeControls(serieForm);
};

const setupProfile = (user) => {
  const profile = document.querySelector('[data-jwt-profile]');
  if (!profile) return;
  const alert = profile.querySelector('[data-profile-alert]');
  const formPicker = profile.querySelector('[data-profile-form-picker]');
  const formPanels = [...profile.querySelectorAll('[data-profile-form-panel]')];
  const showProfileForm = (target) => {
    formPanels.forEach((panel) => {
      panel.hidden = panel.dataset.profileFormPanel !== target;
    });
    formPicker?.querySelectorAll('[data-profile-form-control]').forEach((control) => {
      const selected = control.dataset.profileFormTarget === target;
      control.classList.toggle('is-active', selected);
      control.setAttribute('aria-pressed', String(selected));
    });
  };
  formPicker?.addEventListener('click', (event) => {
    const control = event.target.closest('[data-profile-form-control]');
    if (control) showProfileForm(control.dataset.profileFormTarget);
  });
  const selectedProfileForm = formPicker?.querySelector('[data-profile-form-control][aria-pressed="true"]')?.dataset.profileFormTarget;
  if (selectedProfileForm) showProfileForm(selectedProfileForm);
  const profileForm = profile.querySelector('[data-profile-form]');
  Object.entries(user).forEach(([name, value]) => {
    const field = profileForm.elements.namedItem(name);
    if (field && typeof value === 'string') field.value = value;
  });
  profileForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!profileForm.reportValidity()) return;
    const response = await apiRequest('auth/me/', { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(Object.fromEntries(new FormData(profileForm))) });
    if (!response.ok) return setAlert(alert, await getErrorMessage(response));
    const updatedUser = await response.json();
    renderAuthControls(updatedUser);
    setAlert(alert, 'Your profile details have been updated.', true);
  });
  const passwordForm = profile.querySelector('[data-password-form]');
  passwordForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!passwordForm.reportValidity()) return;
    const response = await apiRequest('auth/me/password/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(Object.fromEntries(new FormData(passwordForm))) });
    if (!response.ok) return setAlert(alert, await getErrorMessage(response));
    passwordForm.reset();
    setAlert(alert, 'Your password has been changed.', true);
  });
  const deleteForm = profile.querySelector('[data-delete-account-form]');
  deleteForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!deleteForm.reportValidity()) return;
    if (!window.confirm('Delete your JAXMORA account permanently? This cannot be undone.')) return;
    const response = await apiRequest('auth/me/', { method: 'DELETE', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(Object.fromEntries(new FormData(deleteForm))) });
    if (!response.ok) return setAlert(alert, await getErrorMessage(response));
    tokenStore.clear();
    window.location.assign('/');
  });
};

const setupSettings = async (user) => {
  const settings = document.querySelector('[data-jwt-settings]');
  if (!settings) return;
  const alert = settings.querySelector('[data-settings-alert]');
  const form = settings.querySelector('[data-settings-form]');
  const preferences = user.preferences || {};
  Object.entries(preferences).forEach(([name, value]) => {
    const field = form.elements.namedItem(name);
    if (field) field.value = value;
  });
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const response = await apiRequest('auth/preferences/', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(Object.fromEntries(new FormData(form))) });
    if (!response.ok) return setAlert(alert, await getErrorMessage(response));
    const updated = await response.json();
    applyPreferences(updated);
    setAlert(alert, 'Your display settings have been saved.', true);
  });
};

document.addEventListener('click', async (event) => {
  if (!event.target.closest('.account-menu')) {
    document.querySelectorAll('.account-dropdown').forEach((item) => { item.hidden = true; });
    document.querySelectorAll('.account-menu-trigger').forEach((item) => item.setAttribute('aria-expanded', 'false'));
  }
  if (event.target.closest('[data-jwt-logout]')) {
    await logoutUser();
    window.location.assign('/');
  }
});

document.addEventListener('DOMContentLoaded', async () => {
  const loginForm = document.querySelector('[data-jwt-login-form]');
  loginForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!loginForm.reportValidity()) return;
    const error = loginForm.parentElement.querySelector('[data-auth-error]');
    setAlert(error, '');
    try {
      const values = new FormData(loginForm);
      await loginUser(values.get('username'), values.get('password'));
      const next = new URLSearchParams(window.location.search).get('next');
      window.location.assign(next?.startsWith('/') ? next : '/');
    } catch (errorMessage) {
      setAlert(error, errorMessage.message || 'Unable to sign in.');
    }
  });
  const signupForm = document.querySelector('[data-jwt-signup-form]');
  signupForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!signupForm.reportValidity()) return;
    const error = signupForm.parentElement.querySelector('[data-auth-error]');
    setAlert(error, '');
    const values = Object.fromEntries(new FormData(signupForm));
    try {
      const response = await fetch(`${API_ROOT}auth/register/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(values) });
      if (!response.ok) throw new Error(await getErrorMessage(response));
      await loginUser(values.username, values.password);
      window.location.assign('/');
    } catch (errorMessage) {
      setAlert(error, errorMessage.message || 'Unable to create your account.');
    }
  });

  const user = await getCurrentUser();
  renderAuthControls(user);
  if (user) applyPreferences(user.preferences);
  if (!user && document.querySelector('[data-jwt-protected]')) {
    const next = `${window.location.pathname}${window.location.search}`;
    window.location.replace(`/login/?next=${encodeURIComponent(next)}`);
    return;
  }
  if (!user) return;
  try {
    await loadDashboard();
    setupDashboard();
    setupProfile(user);
    await setupSettings(user);
  } catch (error) {
    const alert = document.querySelector('[data-dashboard-alert], [data-profile-alert], [data-settings-alert]');
    setAlert(alert, error.message || 'We could not load your account data.');
  }
});

window.JaxmoraSession = { apiRequest, loginUser, logoutUser, tokenStore };
