import { apiRequest } from './session.js';

const DETAILS = {
  movie: { endpoint: 'movies', path: 'movie', label: 'Movie', relatedHeading: 'Related movies' },
  serie: { endpoint: 'series', path: 'series', label: 'Series', relatedHeading: 'Related series' },
  episode: { endpoint: 'episodes', path: 'episode', label: 'Episode' },
  music: { endpoint: 'music', path: 'music', label: 'Music', relatedHeading: 'Related music' },
  comedy: { endpoint: 'comedies', path: 'comedy', label: 'Comedy', relatedHeading: 'Related comedy' },
  visual: { endpoint: 'visual-images', path: 'image-visual', label: 'Visual', relatedHeading: 'Related visuals' },
};

const detailUrl = (type, id) => {
  const config = DETAILS[type];
  return config ? `/${config.path}/${encodeURIComponent(id)}/` : '#';
};

const create = (tagName, className, text) => {
  const element = document.createElement(tagName);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
};

const toList = (payload) => Array.isArray(payload) ? payload : (payload.results || []);

const formatDateTime = (value) => {
  if (!value) return 'Not available';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: value.includes('T') ? 'short' : undefined,
  }).format(date);
};

const formatPrice = (price) => {
  if (price === null || price === undefined || price === '') return 'Free';
  const number = Number(price);
  return Number.isFinite(number)
    ? `${new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(number)} RWF`
    : `${price} RWF`;
};

const contentTitle = (type, content) => type === 'episode' ? content.name : content.title;
const contentDescription = (type, content) => type === 'episode'
  ? content.serie_description
  : content.description;
const contentCategory = (type, content) => type === 'episode'
  ? content.serie_category
  : content.category;
const contentYear = (type, content) => type === 'episode'
  ? content.serie_year_released
  : content.year_released;
const contentPrice = (type, content) => type === 'episode' ? content.serie_price : content.price;

const addMetadata = (container, label, value, className = '') => {
  if (value === undefined || value === null || value === '') return;
  const item = create('div', className);
  item.append(create('dt', '', label), create('dd', '', String(value)));
  container.append(item);
};

const mediaSource = (type, content) => {
  if (type === 'visual') return content.image;
  if (type === 'serie') return content.thumbnail;
  return content.video;
};

const createDetailMedia = (type, content) => {
  const shell = create('div', `detail-media ${type === 'visual' ? 'detail-image' : ''}`);
  const source = mediaSource(type, content);
  if (!source) {
    shell.append(create('div', 'detail-placeholder', type === 'serie' ? 'Series details' : 'Media unavailable'));
    return { shell, player: null };
  }
  const isImage = type === 'visual' || type === 'serie';
  const asset = document.createElement(isImage ? 'img' : 'video');
  asset.src = source;
  if (isImage) {
    asset.alt = content.title;
  } else {
    asset.controls = true;
    asset.preload = 'metadata';
    asset.playsInline = true;
  }
  shell.append(asset);
  return { shell, player: isImage ? null : asset };
};

const appendAction = (container, label, className, callback) => {
  const action = create('button', `button ${className}`, label);
  action.type = 'button';
  action.addEventListener('click', callback);
  container.append(action);
};

const createRelatedCard = (type, content) => {
  const link = create('a', 'related-card');
  link.href = detailUrl(type, content.id);
  const media = create('div', 'related-card-media');
  const source = content.thumbnail || mediaSource(type, content);
  if (source) {
    const isImage = Boolean(content.thumbnail) || type === 'visual' || type === 'serie';
    const asset = document.createElement(isImage ? 'img' : 'video');
    asset.src = source;
    if (isImage) {
      asset.alt = contentTitle(type, content);
      asset.loading = 'lazy';
    } else {
      asset.muted = true;
      asset.preload = 'metadata';
      asset.playsInline = true;
    }
    media.append(asset);
  } else {
    media.append(create('span', '', type === 'serie' ? 'Series' : 'Content'));
  }
  const copy = create('div', 'related-card-copy');
  copy.append(create('p', '', contentCategory(type, content) || type));
  copy.append(create('h3', '', contentTitle(type, content)));
  link.append(media, copy);
  return link;
};

const renderSeasons = (section, serie) => {
  section.hidden = false;
  section.replaceChildren();
  const heading = create('div', 'detail-section-heading');
  const headingCopy = document.createElement('div');
  headingCopy.append(create('p', 'eyebrow', 'Watch by season'));
  headingCopy.append(create('h2', '', 'Seasons and episodes'));
  heading.append(headingCopy);
  section.append(heading);

  if (!serie.seasons?.length) {
    section.append(create('p', 'detail-empty', 'Episodes will appear here when this series is published.'));
    return;
  }
  const seasons = create('div', 'season-list');
  serie.seasons.forEach((season) => {
    const item = create('article', 'season-item');
    const trigger = create('button', 'season-trigger');
    trigger.type = 'button';
    trigger.setAttribute('aria-expanded', 'false');
    const label = create('span');
    label.append(create('strong', '', `Season ${season.ref_number}${season.name ? ` · ${season.name}` : ''}`));
    label.append(create('span', '', `${season.episodes.length} episode${season.episodes.length === 1 ? '' : 's'} · ${season.year_released}`));
    trigger.append(label, create('span', '', 'Show episodes +'));
    const episodeList = create('ol', 'episode-list');
    episodeList.hidden = true;
    season.episodes.forEach((episode) => {
      const row = document.createElement('li');
      const link = create('a');
      link.href = detailUrl('episode', episode.id);
      link.append(
        create('span', '', `Episode ${episode.ref_number} · ${episode.name}`),
        create('small', '', `${episode.view_count || 0} views`),
      );
      row.append(link);
      episodeList.append(row);
    });
    trigger.addEventListener('click', () => {
      const open = trigger.getAttribute('aria-expanded') === 'true';
      trigger.setAttribute('aria-expanded', String(!open));
      trigger.lastElementChild.textContent = open ? 'Show episodes +' : 'Hide episodes −';
      episodeList.hidden = open;
    });
    item.append(trigger, episodeList);
    seasons.append(item);
  });
  section.append(seasons);
};

const recordView = async (type, id, target) => {
  const response = await apiRequest(`${DETAILS[type].endpoint}/${encodeURIComponent(id)}/record-view/`, {
    method: 'POST',
  });
  if (!response.ok) return;
  const data = await response.json();
  if (target) target.textContent = `${data.view_count} viewers`;
};

const loadRelatedRecords = async (type, id, content) => {
  const config = DETAILS[type];
  const response = await apiRequest(`${config.endpoint}/${encodeURIComponent(id)}/related/`);
  if (!response.ok) throw new Error('Related content could not be loaded.');
  return toList(await response.json());
};

document.addEventListener('DOMContentLoaded', async () => {
  const page = document.querySelector('[data-detail-page]');
  if (!page) return;

  const type = page.dataset.detailPage;
  const config = DETAILS[type];
  const status = page.querySelector('[data-detail-status]');
  const contentShell = page.querySelector('[data-detail-content]');
  const main = page.querySelector('[data-detail-main]');
  const seasons = page.querySelector('[data-detail-seasons]');
  const related = page.querySelector('[data-detail-related]');
  const relatedHeading = page.querySelector('[data-related-heading]');
  const relatedList = page.querySelector('[data-related-list]');
  const relatedEmpty = page.querySelector('[data-related-empty]');
  const id = page.dataset.contentId;

  if (!config || !id) {
    status.textContent = 'This content link is incomplete.';
    status.classList.add('is-error');
    return;
  }

  try {
    const response = await apiRequest(`${config.endpoint}/${encodeURIComponent(id)}/`);
    if (!response.ok) throw new Error(response.status === 404 ? 'This content is no longer available.' : 'We could not load this content.');
    const content = await response.json();
    const { shell: media, player } = createDetailMedia(type, content);
    const copy = create('div', 'detail-copy');
    const category = contentCategory(type, content);
    const prefix = type === 'episode'
      ? `${content.serie_title} · Season ${content.season_ref_number}`
      : [config.label, category].filter(Boolean).join(' · ');
    copy.append(create('p', 'detail-kicker', prefix));
    copy.append(create('h1', '', contentTitle(type, content)));
    copy.append(create('p', 'detail-description', contentDescription(type, content) || 'No description has been provided yet.'));

    const actions = create('div', 'detail-actions');
    if (player) {
      appendAction(actions, 'Watch now', 'detail-watch', async () => {
        player.scrollIntoView({ behavior: 'smooth', block: 'center' });
        try { await player.play(); } catch { player.controls = true; }
      });
    }
    if (type === 'movie' && content.trailer_link) {
      const trailer = create('a', 'button detail-trailer', 'Watch trailer');
      trailer.href = content.trailer_link;
      trailer.target = '_blank';
      trailer.rel = 'noopener noreferrer';
      actions.append(trailer);
    }
    if (actions.childElementCount) copy.append(actions);

    const metadata = create('dl', 'detail-metadata');
    addMetadata(metadata, 'Category', category);
    addMetadata(metadata, 'Released', contentYear(type, content));
    addMetadata(metadata, 'Uploaded', formatDateTime(content.uploaded_at));
    addMetadata(metadata, 'Uploaded by', content.owner?.display_name || 'JAXMORA creator');
    addMetadata(metadata, 'Country', content.owner?.country);
    addMetadata(metadata, 'Viewers', `${content.view_count || 0} viewers`, 'detail-view-count');
    addMetadata(metadata, 'Likes', `${content.like_count || 0} likes`, 'detail-like-count');
    addMetadata(metadata, 'Comments', `${content.comment_count || 0} comments`, 'detail-comment-count');
    addMetadata(metadata, 'Price', formatPrice(contentPrice(type, content)));

// Render Engagement Bar (Like & Report buttons)
// --- ENGAGEMENT BAR (Likes & Report) ---
const engagementBar = create('div', 'detail-engagement-bar');

const likeBtn = create('button', `button detail-like-btn ${content.is_liked ? 'is-liked' : ''}`);
likeBtn.type = 'button';
likeBtn.innerHTML = `<span>♥</span> <span class="like-label">${content.is_liked ? 'Liked' : 'Like'}</span> (<strong class="like-count">${content.like_count || 0}</strong>)`;
likeBtn.addEventListener('click', async () => {
  const res = await apiRequest(`${config.endpoint}/${encodeURIComponent(id)}/like/`, { method: 'POST' });
  if (res.ok) {
    const data = await res.json();
    likeBtn.classList.toggle('is-liked', data.liked);
    likeBtn.querySelector('.like-label').textContent = data.liked ? 'Liked' : 'Like';
    likeBtn.querySelector('.like-count').textContent = data.like_count;
    const metaLike = metadata.querySelector('.detail-like-count dd');
    if (metaLike) metaLike.textContent = `${data.like_count} likes`;
  } else if (res.status === 401) {
    alert('Please sign in to like this content.');
  }
});

// Create HTML Dialog Form for Reporting
const reportDialog = create('dialog', 'report-dialog');
reportDialog.innerHTML = `
  <form class="report-form" method="dialog">
    <h3>Report Content</h3>
    <p>Why are you reporting this?</p>
    <label><input type="radio" name="reason" value="Inappropriate content" required> Inappropriate content</label>
    <label><input type="radio" name="reason" value="Copyright violation"> Copyright violation</label>
    <label><input type="radio" name="reason" value="Spam or misleading"> Spam or misleading</label>
    <label><input type="radio" name="reason" value="Other"> Other</label>
    <textarea name="details" placeholder="Additional details (optional)" rows="3"></textarea>
    <div class="report-dialog-actions">
      <button type="button" class="button close-report-btn">Cancel</button>
      <button type="submit" class="button button-primary">Submit Report</button>
    </div>
  </form>
`;
document.body.append(reportDialog);

const reportForm = reportDialog.querySelector('.report-form');
reportDialog.querySelector('.close-report-btn').addEventListener('click', () => reportDialog.close());

reportForm.addEventListener('submit', async () => {
  const formData = new FormData(reportForm);
  const reason = formData.get('reason');
  const details = formData.get('details') || '';

  const res = await apiRequest('content/report/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content_type: type, content_id: id, reason, details }),
  });
  
  if (res.ok) alert('Report submitted. Thank you.');
  else alert('Please sign in to report content.');
});

// Button to trigger the modal
const reportBtn = create('button', 'button detail-report-btn', '🚩 Report');
reportBtn.type = 'button';
reportBtn.addEventListener('click', () => {
  reportForm.reset();
  reportDialog.showModal();
});

engagementBar.append(likeBtn, reportBtn);
copy.append(engagementBar);


// --- COMMENTS SECTION ---
const commentsSection = create('section', 'detail-comments-section');
const commentsHeader = create('div', 'detail-section-heading');
commentsHeader.innerHTML = `<p class="eyebrow">Community</p><h2>Comments (<span class="comments-count">${content.comment_count || 0}</span>)</h2>`;
commentsSection.append(commentsHeader);

const commentForm = create('form', 'comment-form');
commentForm.innerHTML = `
  <textarea placeholder="Write a comment..." rows="3" required maxlength="500"></textarea>
  <button class="button button-primary button-small" type="submit">Post comment</button>
`;
const commentsList = create('div', 'comments-list');

const loadComments = async () => {
  const res = await apiRequest(`${config.endpoint}/${encodeURIComponent(id)}/comments/`);
  if (res.ok) {
    const comments = await res.json();
    commentsList.replaceChildren();
    comments.forEach((c) => {
      const item = create('div', 'comment-item');
      item.innerHTML = `<strong>${c.commenter?.display_name || 'Anonymous'}</strong><p>${c.content}</p>`;
      commentsList.append(item);
    });
  }
};

commentForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const textarea = commentForm.querySelector('textarea');
  const text = textarea.value.trim();
  if (!text) return;

  const res = await apiRequest(`${config.endpoint}/${encodeURIComponent(id)}/comments/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content: text }),
  });

  if (res.ok) {
    textarea.value = '';
    await loadComments();
    const newCount = (content.comment_count || 0) + 1;
    content.comment_count = newCount;
    commentsSection.querySelector('.comments-count').textContent = newCount;
    const metaComment = metadata.querySelector('.detail-comment-count dd');
    if (metaComment) metaComment.textContent = `${newCount} comments`;
  } else if (res.status === 401) {
    alert('Please sign in to leave a comment.');
  }
});

commentsSection.append(commentForm, commentsList);


main.append(commentsSection);

loadComments().catch(() => {});




    if (type === 'movie') addMetadata(metadata, 'Production studio', content.production_studio);
    if (type === 'episode') addMetadata(metadata, 'Season', `Season ${content.season_ref_number}${content.season_name ? ` · ${content.season_name}` : ''}`);
    copy.append(metadata);
    main.append(media, copy);

    if (type === 'serie') renderSeasons(seasons, content);
    contentShell.hidden = false;
    status.hidden = true;

        /* Record view for Movie, Music, Comedy, and Serie's Episode
       only when it's played and record it for Visual on page load */
    const viewCountNode = metadata.querySelector('.detail-view-count dd');
    if( type == 'visual' ){
      recordView( type, content.id, viewCountNode).catch(()=>{});
    } else if(player){
      let viewRecorded = false;
      player.addEventListener('play',()=>{
        if(!viewRecorded){
          viewRecorded = true;
          recordView( type, content.id, viewCountNode).catch(()=>{});
        }
      });
    }


    if (type !== 'episode') {
      if (relatedHeading && config.relatedHeading) relatedHeading.textContent = config.relatedHeading;
      try {
        const records = await loadRelatedRecords(type, id, content);
        if (records.length) {
          relatedList.replaceChildren(...records.map((item) => createRelatedCard(type, item)));
          relatedEmpty.hidden = true;
        } else {
          relatedEmpty.textContent = `No related ${config.label.toLowerCase()} content has been published yet.`;
        }
      } catch {
        relatedEmpty.textContent = 'Related content could not be loaded. Please try again later.';
      }
    }
  } catch (error) {
    status.textContent = error.message || 'We could not load this content.';
    status.classList.add('is-error');
  }
});
