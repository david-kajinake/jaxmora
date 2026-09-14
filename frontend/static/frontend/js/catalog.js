import { apiRequest } from './session.js';

const DETAIL_URLS = {
  movie: (id) => `/movie/${encodeURIComponent(id)}/`,
  serie: (id) => `/series/${encodeURIComponent(id)}/`,
  music: (id) => `/music/${encodeURIComponent(id)}/`,
  comedy: (id) => `/comedy/${encodeURIComponent(id)}/`,
  visual: (id) => `/image-visual/${encodeURIComponent(id)}/`,
};

const TYPE_LABELS = {
  movie: 'Movie',
  serie: 'Series',
  music: 'Music',
  comedy: 'Comedy',
  visual: 'Visual',
};

const toList = (payload) => Array.isArray(payload) ? payload : (payload.results || []);

const requestList = async (path) => {
  const response = await apiRequest(path);
  if (!response.ok) throw new Error('The catalogue could not be loaded. Please try again.');
  return toList(await response.json());
};

const create = (tagName, className, text) => {
  const element = document.createElement(tagName);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
};

const formatNumber = (value = 0) => new Intl.NumberFormat(undefined, {
  notation: value >= 1000 ? 'compact' : 'standard',
  maximumFractionDigits: 1,
}).format(value);

const formatPrice = (price) => {
  if (price === null || price === undefined || price === '') return 'Free';
  const value = Number(price);
  return Number.isFinite(value)
    ? `${new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(value)} RWF`
    : `${price} RWF`;
};

const itemType = (pageType, item) => pageType === 'films' ? (item.seasons ? 'serie' : 'movie') : (
  pageType === 'visuals' ? 'visual' : pageType
);

const createMedia = (item, type) => {
  const media = create('div', 'catalog-card-media');
  const thumbnail = item.thumbnail;
  const source = thumbnail || (type === 'visual' ? item.image : item.video);
  if (source) {
    const isImage = Boolean(thumbnail) || type === 'visual';
    const asset = document.createElement(isImage ? 'img' : 'video');
    asset.src = source;
    if (isImage) {
      asset.loading = 'lazy';
      asset.alt = item.title;
    } else {
      asset.preload = 'metadata';
      asset.muted = true;
      asset.playsInline = true;
    }
    asset.setAttribute('aria-label', `${item.title} ${type === 'visual' ? 'image' : 'video'}`);
    media.append(asset);
  } else {
    media.append(create('span', 'catalog-card-placeholder', TYPE_LABELS[type]));
  }
  media.append(create('span', 'catalog-card-badge', String(item.year_released || '')));
  return media;
};

document.addEventListener('DOMContentLoaded', async () => {
  const page = document.querySelector('[data-catalog-page]');
  if (!page) return;

  const pageType = page.dataset.catalogPage;
  const endpoints = page.dataset.catalogEndpoints.split(',').filter(Boolean);
  const results = document.querySelector('#catalog-results');
  const count = document.querySelector('#catalog-count');
  const loadMore = document.querySelector('#load-more');
  const empty = document.querySelector('#empty-catalog');
  const search = document.querySelector('#catalog-search');
  const sort = document.querySelector('#catalog-sort');
  const filterBar = document.querySelector('[data-catalog-filters]');
  const state = { filter: 'all', term: '', sort: 'latest', shown: 20 };
  let items = [];

  const itemMatches = (item) => {
    const type = itemType(pageType, item);
    const searchable = [
      item.title,
      item.description,
      item.category,
      item.production_studio,
      item.owner?.display_name,
      item.year_released,
      TYPE_LABELS[type],
    ].filter(Boolean).join(' ').toLowerCase();
    return (state.filter === 'all' || item.category?.toLowerCase() === state.filter)
      && searchable.includes(state.term);
  };

  const sortedItems = () => items.filter(itemMatches).sort((left, right) => {
    if (state.sort === 'views' || state.sort === 'popular' || state.sort === 'trending') {
      return (right.view_count || 0) - (left.view_count || 0);
    }
    return new Date(right.uploaded_at || 0) - new Date(left.uploaded_at || 0);
  });

  const renderFilters = () => {
    const categories = [...new Set(items.map((item) => item.category?.trim()).filter(Boolean))]
      .sort((left, right) => left.localeCompare(right));
    filterBar.replaceChildren(create('span', '', 'Explore by'));
    [['all', `All ${pageType}`], ...categories.map((category) => [category.toLowerCase(), category])]
      .forEach(([value, label]) => {
        const button = create('button', value === state.filter ? 'is-active' : '', label);
        button.type = 'button';
        button.dataset.filter = value;
        button.addEventListener('click', () => {
          state.filter = value;
          state.shown = 20;
          renderFilters();
          render();
        });
        filterBar.append(button);
      });
  };

  const card = (item) => {
    const type = itemType(pageType, item);
    const link = create('a', `catalog-card catalog-card-${type === 'movie' || type === 'serie' ? 'film' : type}`);
    link.href = DETAIL_URLS[type](item.id);
    link.setAttribute('aria-label', `Open ${item.title}`);
    link.append(createMedia(item, type));

    const body = create('div', 'catalog-card-body');
    body.append(create('p', 'catalog-card-meta', [TYPE_LABELS[type], item.category].filter(Boolean).join(' · ')));
    body.append(create('h3', '', item.title));
    body.lastElementChild.title = item.title;
    body.append(create('p', 'catalog-card-creator', item.owner?.display_name || 'JAXMORA creator'));
    const footer = create('div', 'catalog-card-footer');
    footer.append(create('span', '', formatPrice(item.price)));
    footer.append(create('small', '', `${formatNumber(item.view_count || 0)} views`));
    body.append(footer);
    link.append(body);
    return link;
  };

  const render = () => {
    const filtered = sortedItems();
    const visible = filtered.slice(0, state.shown);
    results.replaceChildren(...visible.map(card));
    count.textContent = `Showing ${visible.length} of ${filtered.length} ${pageType}`;
    loadMore.hidden = state.shown >= filtered.length || filtered.length === 0;
    empty.hidden = filtered.length > 0;
  };

  const showLoadError = (message) => {
    results.replaceChildren();
    empty.hidden = false;
    empty.querySelector('h3').textContent = 'We could not load this catalogue';
    empty.querySelector('p').textContent = message;
    empty.querySelector('#clear-catalog-filter').hidden = true;
    loadMore.hidden = true;
    count.textContent = '';
  };

  search.addEventListener('input', () => {
    state.term = search.value.trim().toLowerCase();
    state.shown = 20;
    render();
  });
  sort.addEventListener('change', () => { state.sort = sort.value; render(); });
  loadMore.addEventListener('click', () => { state.shown += 8; render(); });
  document.querySelector('#clear-catalog-filter').addEventListener('click', () => {
    state.filter = 'all';
    state.term = '';
    state.shown = 20;
    search.value = '';
    renderFilters();
    render();
  });

  const menu = document.querySelector('.catalog-menu-toggle');
  const nav = document.querySelector('.catalog-nav nav');
  menu?.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') === 'true';
    menu.setAttribute('aria-expanded', String(!open));
    nav.classList.toggle('is-open', !open);
  });

  results.setAttribute('aria-busy', 'true');
  try {
    const responses = await Promise.all(endpoints.map(requestList));
    items = responses.flat();
    renderFilters();
    render();
  } catch (error) {
    showLoadError(error.message || 'Please refresh the page and try again.');
  } finally {
    results.removeAttribute('aria-busy');
  }
});
