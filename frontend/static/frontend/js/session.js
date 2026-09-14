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

let dashboardData = null;

const dashboardDate = (value) => {
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? 'Recently uploaded'
    : `Uploaded ${date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}`;
};

const dashboardDetailPath = (type, id) => {
  const paths = {
    movie: 'movie', serie: 'series', music: 'music', comedy: 'comedy',
    visual: 'image-visual', episode: 'episode',
  };
  return paths[type] ? `/${paths[type]}/${encodeURIComponent(id)}/` : '#';
};

const managementEndpoint = (type, id) => ({
  movie: `movies/${id}/`,
  serie: `series/${id}/`,
  music: `music/${id}/`,
  comedy: `comedies/${id}/`,
  visual: `visual-images/${id}/`,
  episode: `episodes/${id}/`,
}[type]);

const makeDashboardElement = (tag, className = '', text) => {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
};

const closeDashboardDialog = (dialog) => {
  if (dialog?.open) dialog.close();
};

const openDashboardDialog = (dialog) => {
  if (!dialog) return;
  document.querySelectorAll('.dashboard-dialog[open]').forEach((item) => {
    if (item !== dialog) item.close();
  });
  if (!dialog.open) dialog.showModal();
};

const dashboardLibraryAlert = (message, success = false) => {
  setAlert(document.querySelector('[data-library-alert]'), message, success);
};

const dashboardManagementAlert = (message, success = false) => {
  setAlert(document.querySelector('[data-management-alert]'), message, success);
};

const copyDashboardLink = async (type, id) => {
  const value = new URL(dashboardDetailPath(type, id), window.location.origin).href;
  try {
    await navigator.clipboard.writeText(value);
  } catch {
    const input = document.createElement('textarea');
    input.value = value;
    input.setAttribute('readonly', '');
    input.style.position = 'fixed';
    input.style.opacity = '0';
    document.body.append(input);
    input.select();
    document.execCommand('copy');
    input.remove();
  }
  dashboardLibraryAlert('Link copied to your clipboard.', true);
};

const makeOptionMenu = (actions) => {
  const wrapper = makeDashboardElement('div', 'content-options');
  const trigger = makeDashboardElement('button', 'content-options-trigger', 'Options ⋯');
  trigger.type = 'button';
  trigger.setAttribute('aria-expanded', 'false');
  const menu = makeDashboardElement('div', 'content-options-menu');
  menu.hidden = true;
  actions.forEach(({ label, callback, danger = false }) => {
    const action = makeDashboardElement('button', danger ? 'is-danger' : '', label);
    action.type = 'button';
    action.addEventListener('click', async () => {
      menu.hidden = true;
      trigger.setAttribute('aria-expanded', 'false');
      await callback();
    });
    menu.append(action);
  });
  trigger.addEventListener('click', (event) => {
    event.stopPropagation();
    const willOpen = menu.hidden;
    document.querySelectorAll('.content-options-menu').forEach((item) => { item.hidden = true; });
    document.querySelectorAll('.content-options-trigger').forEach((item) => item.setAttribute('aria-expanded', 'false'));
    menu.hidden = !willOpen;
    trigger.setAttribute('aria-expanded', String(willOpen));
  });
  wrapper.append(trigger, menu);
  return wrapper;
};

const showManagementDialog = (title, builder) => {
  const dialog = document.querySelector('[data-management-dialog]');
  const body = dialog?.querySelector('[data-management-dialog-body]');
  if (!dialog || !body) return;
  body.replaceChildren();
  const heading = makeDashboardElement('h2', '', title);
  heading.id = 'management-dialog-heading';
  const alert = makeDashboardElement('div', 'account-alert');
  alert.dataset.managementAlert = '';
  alert.hidden = true;
  body.append(heading, alert);
  builder(body, dialog);
  openDashboardDialog(dialog);
};

const refreshManagedContent = async (message) => {
  await loadDashboard();
  if (message) {
    dashboardLibraryAlert(message, true);
    setAlert(document.querySelector('[data-dashboard-alert]'), message, true);
  }
};

const deleteManagedContent = async (item, endpoint, label = item.title) => {
  if (!window.confirm(`Delete “${label}”? This cannot be undone.`)) return;
  const response = await apiRequest(endpoint, { method: 'DELETE' });
  if (!response.ok) return dashboardLibraryAlert(await getErrorMessage(response));
  await refreshManagedContent(`“${label}” has been deleted.`);
};

const showRenameDialog = (item) => {
  const property = item.type === 'episode' ? 'name' : 'title';
  showManagementDialog(`Rename ${item.label || item.type}`, (body, dialog) => {
    const copy = makeDashboardElement('p', 'management-copy', 'Choose a clear title your audience will recognize.');
    const form = makeDashboardElement('form', 'account-form');
    const field = makeDashboardElement('div', 'form-field');
    const label = makeDashboardElement('label', '', 'Title');
    const input = document.createElement('input');
    input.value = item.title;
    input.maxLength = 255;
    input.required = true;
    field.append(label, input);
    const submit = makeDashboardElement('button', 'button button-primary account-submit', 'Save title');
    submit.type = 'submit';
    form.append(field, submit);
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const response = await apiRequest(managementEndpoint(item.type, item.id), {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ [property]: input.value.trim() }),
      });
      if (!response.ok) return dashboardManagementAlert(await getErrorMessage(response));
      closeDashboardDialog(dialog);
      await refreshManagedContent('Your content title has been updated.');
    });
    body.append(copy, form);
  });
};

const appendEngagementGroup = (container, label, engagement) => {
  const group = makeDashboardElement('section', 'engagement-group');
  const heading = makeDashboardElement('h3', '', `${label} (${engagement.count})`);
  group.append(heading);
  if (!engagement.people.length) {
    group.append(makeDashboardElement('p', 'management-copy', `No ${label.toLowerCase()} yet.`));
  } else {
    const people = makeDashboardElement('ul', 'engagement-people');
    engagement.people.forEach((entry) => {
      const person = entry.user || entry;
      const row = makeDashboardElement('li');
      row.append(makeDashboardElement('strong', '', person.display_name || 'JAXMORA user'));
      if (entry.comment) row.append(makeDashboardElement('span', '', entry.comment));
      people.append(row);
    });
    group.append(people);
  }
  container.append(group);
};

const showEngagementDialog = async (item) => {
  const response = await apiRequest(`dashboard/contents/${item.type}/${item.id}/engagement/`);
  if (!response.ok) return dashboardLibraryAlert(await getErrorMessage(response));
  const data = await response.json();
  showManagementDialog(`Engagement · ${item.title}`, (body) => {
    body.append(makeDashboardElement('p', 'management-copy', 'See the people responding to this upload.'));
    const groups = makeDashboardElement('div', 'engagement-groups');
    appendEngagementGroup(groups, 'Views', data.engagements.views);
    appendEngagementGroup(groups, 'Likes', data.engagements.likes);
    appendEngagementGroup(groups, 'Comments', data.engagements.comments);
    body.append(groups);
  });
};

const episodeInputRow = (number = 1, removable = true) => {
  const row = makeDashboardElement('fieldset', 'episode-upload-row');
  row.dataset.episodeRow = '';
  row.innerHTML = `
    <legend>Episode <span data-episode-label>${number}</span></legend>
    <button class="remove-episode" type="button" data-remove-episode aria-label="Remove episode">×</button>
    <div class="form-field"><label>Episode title</label><input data-episode-name maxlength="255" required></div>
    <div class="form-field"><label>Episode number</label><input data-episode-number type="number" min="1" value="${number}" required></div>
    <div class="form-field"><label>Episode video</label><input data-episode-video type="file" accept="video/*" required></div>`;
  row.querySelector('[data-remove-episode]').hidden = !removable;
  return row;
};

const setEpisodeControls = (scope) => {
  const rows = [...scope.querySelectorAll(':scope > [data-episode-row]')];
  rows.forEach((row, index) => {
    row.querySelector('[data-episode-label]').textContent = index + 1;
    row.querySelector('[data-remove-episode]').hidden = rows.length === 1;
  });
};

const serieSeasonRow = (number = 1) => {
  const row = makeDashboardElement('fieldset', 'serie-season-upload-row');
  row.dataset.serieSeasonRow = '';
  row.innerHTML = `
    <legend>Season <span data-season-label>${number}</span></legend>
    <button class="remove-episode remove-season" type="button" data-remove-season aria-label="Remove season">×</button>
    <div class="account-form-row"><div class="form-field"><label>Season number</label><input data-season-number type="number" min="1" value="${number}" required></div><div class="form-field"><label>Season release year</label><input data-season-year type="number" min="1888" max="2100" required></div></div>
    <div class="form-field"><label>Season name <span class="optional-label">(optional)</span></label><input data-season-name maxlength="255"></div>
    <div class="season-count-control"><div class="form-field"><label>Episodes to upload now</label><input type="number" min="1" max="50" value="1" data-episode-count></div><button class="button button-small" type="button" data-apply-episode-count>Set episodes</button></div>
    <div class="episode-upload-list" data-episode-list></div>
    <button class="add-episode" type="button" data-add-episode>+ Add another episode</button>`;
  row.querySelector('[data-episode-list]').append(episodeInputRow());
  return row;
};

const setSeasonControls = (form) => {
  const rows = [...form.querySelectorAll('[data-serie-season-row]')];
  rows.forEach((row, index) => {
    row.querySelector('[data-season-label]').textContent = index + 1;
    row.querySelector('[data-remove-season]').hidden = rows.length === 1;
    setEpisodeControls(row.querySelector('[data-episode-list]'));
  });
  const count = form.querySelector('[data-season-count]');
  if (count) count.value = rows.length;
};

const applyEpisodeCount = (season, count) => {
  const list = season.querySelector('[data-episode-list]');
  const wanted = Math.min(50, Math.max(1, Number(count) || 1));
  while (list.children.length < wanted) list.append(episodeInputRow(list.children.length + 1));
  while (list.children.length > wanted) list.lastElementChild.remove();
  season.querySelector('[data-episode-count]').value = wanted;
  setEpisodeControls(list);
};

const showAddSeasonDialog = (serie) => {
  showManagementDialog(`Add a season · ${serie.title}`, (body, dialog) => {
    const form = makeDashboardElement('form', 'account-form');
    form.innerHTML = `
      <div class="account-form-row"><div class="form-field"><label>Season number</label><input name="season_number" type="number" min="1" value="${(serie.seasons?.length || 0) + 1}" required></div><div class="form-field"><label>Release year</label><input name="season_year" type="number" min="1888" max="2100" required></div></div>
      <div class="form-field"><label>Season name <span class="optional-label">(optional)</span></label><input name="season_name" maxlength="255"></div>
      <div class="episode-upload-list" data-new-season-episodes></div>
      <button class="add-episode" type="button" data-add-new-season-episode>+ Add another episode</button>
      <button class="button button-primary account-submit" type="submit">Add season</button>`;
    const episodes = form.querySelector('[data-new-season-episodes]');
    episodes.append(episodeInputRow());
    form.addEventListener('click', (event) => {
      if (event.target.closest('[data-add-new-season-episode]')) episodes.append(episodeInputRow(episodes.children.length + 1));
      const remove = event.target.closest('[data-remove-episode]');
      if (remove) remove.closest('[data-episode-row]').remove();
      setEpisodeControls(episodes);
    });
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const payload = new FormData(form);
      const episodeData = [];
      [...episodes.children].forEach((row, index) => {
        episodeData.push({
          name: row.querySelector('[data-episode-name]').value,
          ref_number: Number(row.querySelector('[data-episode-number]').value),
        });
        payload.append(`episode_file_${index}`, row.querySelector('[data-episode-video]').files[0]);
      });
      payload.append('episodes', JSON.stringify(episodeData));
      const response = await apiRequest(`series/${serie.id}/seasons/`, { method: 'POST', body: payload });
      if (!response.ok) return dashboardManagementAlert(await getErrorMessage(response));
      closeDashboardDialog(dialog);
      await refreshManagedContent(`Season ${payload.get('season_number')} has been added.`);
    });
    body.append(makeDashboardElement('p', 'management-copy', 'Add the season details and the episodes you want to publish now.'), form);
  });
};

const showAddEpisodesDialog = (serie, season) => {
  showManagementDialog(`Add episodes · Season ${season.ref_number}`, (body, dialog) => {
    const form = makeDashboardElement('form', 'account-form');
    const episodes = makeDashboardElement('div', 'episode-upload-list');
    episodes.dataset.addedEpisodes = '';
    episodes.append(episodeInputRow((season.episodes?.length || 0) + 1));
    const add = makeDashboardElement('button', 'add-episode', '+ Add another episode');
    add.type = 'button';
    const submit = makeDashboardElement('button', 'button button-primary account-submit', 'Add episodes');
    submit.type = 'submit';
    form.append(episodes, add, submit);
    add.addEventListener('click', () => {
      episodes.append(episodeInputRow((season.episodes?.length || 0) + episodes.children.length));
      setEpisodeControls(episodes);
    });
    episodes.addEventListener('click', (event) => {
      const remove = event.target.closest('[data-remove-episode]');
      if (!remove) return;
      remove.closest('[data-episode-row]').remove();
      setEpisodeControls(episodes);
    });
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      for (const row of episodes.children) {
        const payload = new FormData();
        payload.append('name', row.querySelector('[data-episode-name]').value);
        payload.append('ref_number', row.querySelector('[data-episode-number]').value);
        payload.append('video', row.querySelector('[data-episode-video]').files[0]);
        const response = await apiRequest(`series/${serie.id}/seasons/${season.id}/episodes/`, { method: 'POST', body: payload });
        if (!response.ok) return dashboardManagementAlert(await getErrorMessage(response));
      }
      closeDashboardDialog(dialog);
      await refreshManagedContent('Your new episode uploads are published.');
    });
    body.append(makeDashboardElement('p', 'management-copy', 'Add one or more episodes to this existing season.'), form);
  });
};

const renderLibrary = () => {
  const library = document.querySelector('[data-library-list]');
  const empty = document.querySelector('[data-library-empty]');
  if (!library || !empty) return;
  const contents = dashboardData?.contents || [];
  library.replaceChildren();
  empty.hidden = Boolean(contents.length);
  contents.forEach((item) => {
    const card = makeDashboardElement('article', 'managed-content-card');
    const heading = makeDashboardElement('div', 'managed-content-heading');
    const copy = document.createElement('div');
    copy.append(
      makeDashboardElement('span', 'content-type-tag', item.label),
      makeDashboardElement('h3', '', item.title),
      makeDashboardElement('p', '', dashboardDate(item.uploaded_at)),
    );
    const actions = makeDashboardElement('div', 'managed-content-actions');
    const engagement = makeDashboardElement('button', 'dashboard-secondary-button', 'Engagement');
    engagement.type = 'button';
    engagement.addEventListener('click', () => showEngagementDialog(item));
    const options = [
      { label: 'Rename', callback: () => showRenameDialog(item) },
      { label: 'Copy link', callback: () => copyDashboardLink(item.type, item.id) },
      ...(item.type === 'serie' ? [{ label: 'Add more seasons', callback: () => showAddSeasonDialog(item) }] : []),
      { label: 'Delete', danger: true, callback: () => deleteManagedContent(item, managementEndpoint(item.type, item.id)) },
    ];
    actions.append(engagement, makeOptionMenu(options));
    heading.append(copy, actions);
    const stats = makeDashboardElement('div', 'content-stat-grid');
    [['Views', item.view_count], ['Likes', item.like_count], ['Comments', item.comment_count]].forEach(([label, count]) => {
      const stat = makeDashboardElement('span');
      stat.append(makeDashboardElement('strong', '', String(count)), document.createTextNode(` ${label}`));
      stats.append(stat);
    });
    card.append(heading, stats);
    if (item.type === 'serie' && item.seasons?.length) {
      const seasons = makeDashboardElement('div', 'managed-season-list');
      item.seasons.forEach((season) => {
        const seasonCard = makeDashboardElement('section', 'managed-season-card');
        const seasonHeading = makeDashboardElement('div', 'managed-season-heading');
        const seasonCopy = makeDashboardElement('div');
        seasonCopy.append(makeDashboardElement('h4', '', `Season ${season.ref_number}${season.name ? ` · ${season.name}` : ''}`));
        seasonCopy.append(makeDashboardElement('p', '', `${season.episodes.length} episode${season.episodes.length === 1 ? '' : 's'} · ${season.year_released}`));
        const seasonOptions = makeOptionMenu([
          { label: 'Add more episodes', callback: () => showAddEpisodesDialog(item, season) },
          { label: 'Delete season', danger: true, callback: () => deleteManagedContent(
            { title: `Season ${season.ref_number}` },
            `series/${item.id}/seasons/${season.id}/`,
            `Season ${season.ref_number}`,
          ) },
        ]);
        seasonHeading.append(seasonCopy, seasonOptions);
        seasonCard.append(seasonHeading);
        const episodes = makeDashboardElement('div', 'managed-episode-list');
        season.episodes.forEach((episode) => {
          const episodeItem = {
            id: episode.id,
            type: 'episode',
            label: 'Episode',
            title: episode.name,
            view_count: episode.view_count || 0,
          };
          const episodeRow = makeDashboardElement('div', 'managed-episode-row');
          const episodeCopy = makeDashboardElement('span', '', `E${episode.ref_number} · ${episode.name} (${episode.view_count || 0} views)`);
          const episodeActions = makeDashboardElement('div', 'managed-episode-actions');
          const episodeEngagement = makeDashboardElement('button', 'dashboard-text-button', 'Engagement');
          episodeEngagement.type = 'button';
          episodeEngagement.addEventListener('click', () => showEngagementDialog(episodeItem));
          episodeActions.append(episodeEngagement, makeOptionMenu([
            { label: 'Rename', callback: () => showRenameDialog(episodeItem) },
            { label: 'Copy link', callback: () => copyDashboardLink('episode', episode.id) },
            { label: 'Delete', danger: true, callback: () => deleteManagedContent(episodeItem, managementEndpoint('episode', episode.id)) },
          ]));
          episodeRow.append(episodeCopy, episodeActions);
          episodes.append(episodeRow);
        });
        seasonCard.append(episodes);
        seasons.append(seasonCard);
      });
      card.append(seasons);
    }
    library.append(card);
  });
};

const loadDashboard = async () => {
  const dashboard = document.querySelector('[data-jwt-dashboard]');
  if (!dashboard) return;
  const response = await apiRequest('dashboard/');
  if (!response.ok) throw new Error(await getErrorMessage(response));
  dashboardData = await response.json();
  ['total_views', 'total_likes', 'total_uploads'].forEach((key) => {
    const target = dashboard.querySelector(`[data-analytics="${key}"]`);
    if (target) target.textContent = dashboardData[key];
  });
  const list = dashboard.querySelector('[data-recent-uploads]');
  const empty = dashboard.querySelector('[data-empty-uploads]');
  list.replaceChildren();
  empty.hidden = Boolean(dashboardData.recent_uploads.length);
  dashboardData.recent_uploads.forEach((item) => {
    const article = document.createElement('article');
    const tag = makeDashboardElement('span', 'content-type-tag', item.label || item.type);
    const copy = document.createElement('div');
    copy.append(makeDashboardElement('h3', '', item.title), makeDashboardElement('p', '', dashboardDate(item.uploaded_at)));
    const manage = makeDashboardElement('button', 'dashboard-text-button', 'Manage');
    manage.type = 'button';
    manage.addEventListener('click', () => openDashboardDialog(document.querySelector('[data-library-dialog]')));
    article.append(tag, copy, manage);
    list.append(article);
  });
  renderLibrary();
};

const setupDashboard = () => {
  const dashboard = document.querySelector('[data-jwt-dashboard]');
  if (!dashboard) return;
  const alert = dashboard.querySelector('[data-dashboard-alert]');
  const uploadDialog = dashboard.querySelector('[data-upload-dialog]');
  const libraryDialog = dashboard.querySelector('[data-library-dialog]');
  const typePicker = dashboard.querySelector('[data-upload-type-picker]');
  const uploadPanels = [...dashboard.querySelectorAll('[data-upload-form-panel]')];
  const contentForms = [...dashboard.querySelectorAll('[data-content-upload-form]')];
  const serieForm = dashboard.querySelector('[data-serie-upload-form]');
  const showUploadForm = (type) => uploadPanels.forEach((panel) => {
    panel.hidden = panel.dataset.uploadFormPanel !== type;
  });
  dashboard.querySelectorAll('[data-open-upload-dialog]').forEach((button) => button.addEventListener('click', () => {
    openDashboardDialog(uploadDialog);
  }));
  dashboard.querySelectorAll('[data-open-library]').forEach((button) => button.addEventListener('click', () => {
    openDashboardDialog(libraryDialog);
  }));
  dashboard.querySelectorAll('[data-close-dialog]').forEach((button) => button.addEventListener('click', () => {
    closeDashboardDialog(button.closest('dialog'));
  }));
  dashboard.querySelectorAll('.dashboard-dialog').forEach((dialog) => {
    dialog.addEventListener('click', (event) => {
      if (event.target === dialog) closeDashboardDialog(dialog);
    });
  });
  typePicker?.addEventListener('change', (event) => {
    if (event.target.matches('[data-upload-type-control]')) showUploadForm(event.target.value);
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
    const seasonList = serieForm.querySelector('[data-serie-season-list]');
    if (event.target.closest('[data-add-season]')) seasonList.append(serieSeasonRow(seasonList.children.length + 1));
    if (event.target.closest('[data-apply-season-count]')) {
      const wanted = Math.min(20, Math.max(1, Number(serieForm.querySelector('[data-season-count]').value) || 1));
      while (seasonList.children.length < wanted) seasonList.append(serieSeasonRow(seasonList.children.length + 1));
      while (seasonList.children.length > wanted) seasonList.lastElementChild.remove();
    }
    const season = event.target.closest('[data-serie-season-row]');
    if (season && event.target.closest('[data-add-episode]')) {
      const list = season.querySelector('[data-episode-list]');
      list.append(episodeInputRow(list.children.length + 1));
    }
    if (season && event.target.closest('[data-apply-episode-count]')) {
      applyEpisodeCount(season, season.querySelector('[data-episode-count]').value);
    }
    const removeEpisode = event.target.closest('[data-remove-episode]');
    if (removeEpisode) removeEpisode.closest('[data-episode-row]').remove();
    const removeSeason = event.target.closest('[data-remove-season]');
    if (removeSeason) removeSeason.closest('[data-serie-season-row]').remove();
    setSeasonControls(serieForm);
  });
  serieForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!serieForm.reportValidity()) return;
    setAlert(alert, '');
    const source = new FormData(serieForm);
    const payload = new FormData();
    ['title', 'description', 'price', 'year_released', 'category'].forEach((field) => payload.append(field, source.get(field) || ''));
    const thumbnail = source.get('thumbnail');
    if (thumbnail?.size) payload.append('thumbnail', thumbnail);
    const seasons = [];
    [...serieForm.querySelectorAll('[data-serie-season-row]')].forEach((season, seasonIndex) => {
      const episodes = [];
      [...season.querySelectorAll('[data-episode-row]')].forEach((row, episodeIndex) => {
        episodes.push({
          name: row.querySelector('[data-episode-name]').value,
          ref_number: Number(row.querySelector('[data-episode-number]').value),
        });
        payload.append(`season_${seasonIndex}_episode_file_${episodeIndex}`, row.querySelector('[data-episode-video]').files[0]);
      });
      seasons.push({
        season_number: Number(season.querySelector('[data-season-number]').value),
        season_name: season.querySelector('[data-season-name]').value,
        season_year: Number(season.querySelector('[data-season-year]').value),
        episodes,
      });
    });
    payload.append('seasons', JSON.stringify(seasons));
    const response = await apiRequest('series/upload/', { method: 'POST', body: payload });
    if (!response.ok) return setAlert(alert, await getErrorMessage(response));
    serieForm.reset();
    const seasonList = serieForm.querySelector('[data-serie-season-list]');
    seasonList.replaceChildren(serieSeasonRow());
    setSeasonControls(serieForm);
    setAlert(alert, 'Your series, seasons, and episodes have been published.', true);
    await loadDashboard();
  });
  setSeasonControls(serieForm);
  document.addEventListener('click', (event) => {
    if (!event.target.closest('.content-options')) {
      document.querySelectorAll('.content-options-menu').forEach((menu) => { menu.hidden = true; });
      document.querySelectorAll('.content-options-trigger').forEach((trigger) => trigger.setAttribute('aria-expanded', 'false'));
    }
  });
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

export { apiRequest, getErrorMessage, tokenStore };
