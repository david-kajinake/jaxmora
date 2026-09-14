import { apiRequest } from './session.js';

const SECTIONS = {
  films: {
    endpoints: ['movies/', 'series/'],
    detailUrl: (item) => item.seasons
      ? `/series/${encodeURIComponent(item.id)}/`
      : `/movie/${encodeURIComponent(item.id)}/`,
  },
  music: {
    endpoints: ['music/'],
    detailUrl: (item) => `/music/${encodeURIComponent(item.id)}/`,
  },
  comedy: {
    endpoints: ['comedies/'],
    detailUrl: (item) => `/comedy/${encodeURIComponent(item.id)}/`,
  },
  visuals: {
    endpoints: ['visual-images/'],
    detailUrl: (item) => `/image-visual/${encodeURIComponent(item.id)}/`,
  },
};

const create = (tagName, className, text) => {
  const element = document.createElement(tagName);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
};

const toList = (payload) => Array.isArray(payload) ? payload : (payload.results || []);

const fetchList = async (endpoint) => {
  const response = await apiRequest(endpoint);
  if (!response.ok) throw new Error('Unable to load content.');
  return toList(await response.json());
};

const formatPrice = (price) => {
  if (price === null || price === undefined || price === '') return 'Free';
  const number = Number(price);
  return Number.isFinite(number)
    ? `${new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(number)} RWF`
    : `${price} RWF`;
};

const ownerName = (item) => item.owner?.display_name || 'JAXMORA creator';

const addSearchTerms = (element, type, item) => {
  element.dataset.searchable = [
    item.title,
    item.description,
    item.category,
    ownerName(item),
    type,
  ].filter(Boolean).join(' ').toLowerCase();
};

const addAsset = (card, source, title, image = false) => {
  if (!source) {
    card.append(create('div', 'home-card-placeholder', 'Content coming soon'));
    return;
  }
  const asset = document.createElement(image ? 'img' : 'video');
  asset.src = source;
  if (image) {
    asset.alt = title;
    asset.loading = 'lazy';
  } else {
    asset.muted = true;
    asset.playsInline = true;
    asset.preload = 'metadata';
    asset.setAttribute('aria-label', `${title} video`);
  }
  card.append(asset);
};

const createFilmCard = (item, detailUrl) => {
  const isSerie = Boolean(item.seasons);
  const card = create('a', 'film-card media-card');
  card.href = detailUrl(item);
  addSearchTerms(card, isSerie ? 'series' : 'movie', item);
  addAsset(card, item.thumbnail || item.video, item.title, Boolean(item.thumbnail));
  card.append(create('div', 'card-gradient'));
  card.append(create('span', 'card-tag', item.category || (isSerie ? 'Series' : 'Movie')));
  const info = create('div', 'film-info');
  info.append(create('p', 'meta', isSerie ? 'Series' : 'Feature film'));
  info.append(create('h3', '', item.title));
  info.append(create('p', 'creator', ownerName(item)));
  const price = create('div', 'price-row');
  price.append(create('span', '', formatPrice(item.price)));
  price.append(create('span', '', `${item.view_count || 0} views`));
  info.append(price);
  card.append(info);
  return card;
};

const createMusicCard = (item, detailUrl) => {
  const card = create('a', 'music-card');
  card.href = detailUrl(item);
  addSearchTerms(card, 'music', item);
  addAsset(card, item.thumbnail || item.video, item.title, Boolean(item.thumbnail));
  const copy = create('div');
  copy.append(create('p', 'track-number', item.category || 'Music'));
  copy.append(create('h3', '', item.title));
  copy.append(create('p', '', ownerName(item)));
  copy.append(create('span', '', formatPrice(item.price)));
  card.append(copy);
  return card;
};

const createComedyCard = (item, detailUrl) => {
  const card = create('a', 'comedy-card');
  card.href = detailUrl(item);
  addSearchTerms(card, 'comedy', item);
  addAsset(card, item.thumbnail || item.video, item.title, Boolean(item.thumbnail));
  card.append(create('span', '', String(item.year_released || 'Comedy')));
  const copy = create('div');
  copy.append(create('h3', '', item.title));
  copy.append(create('p', '', ownerName(item)));
  card.append(copy);
  return card;
};

const createVisualCard = (item, detailUrl) => {
  const card = create('a', 'image-card');
  card.href = detailUrl(item);
  addSearchTerms(card, 'visual', item);
  addAsset(card, item.thumbnail || item.image, item.title, true);
  const copy = create('div');
  copy.append(create('h3', '', item.title));
  copy.append(create('p', '', `${ownerName(item)} · ${formatPrice(item.price)}`));
  card.append(copy);
  return card;
};

const CARD_CREATORS = {
  films: createFilmCard,
  music: createMusicCard,
  comedy: createComedyCard,
  visuals: createVisualCard,
};

document.addEventListener('DOMContentLoaded', async () => {
  await Promise.all([...document.querySelectorAll('[data-home-content]')].map(async (target) => {
    const type = target.dataset.homeContent;
    const config = SECTIONS[type];
    try {
      const lists = await Promise.all(config.endpoints.map(fetchList));
      const items = lists.flat()
        .sort((left, right) => new Date(right.uploaded_at || 0) - new Date(left.uploaded_at || 0))
        .slice(0, 4);
      if (!items.length) {
        target.append(create('p', 'home-content-status', 'No content has been published yet.'));
        return;
      }
      target.replaceChildren(...items.map((item) => CARD_CREATORS[type](item, config.detailUrl)));
    } catch {
      target.replaceChildren(create('p', 'home-content-status', 'Content could not be loaded. Please try again later.'));
    } finally {
      target.removeAttribute('aria-busy');
    }
  }));
});
