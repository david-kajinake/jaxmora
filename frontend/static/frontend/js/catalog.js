document.addEventListener('DOMContentLoaded', () => {
  const page = document.querySelector('[data-catalog-page]');
  if (!page) return;

  const images = {
    films: [
      'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=720&q=85',
      'https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?auto=format&fit=crop&w=720&q=85',
      'https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&w=720&q=85',
      'https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=720&q=85',
    ],
    music: [
      'https://images.unsplash.com/photo-1516280440614-37939bbacd81?auto=format&fit=crop&w=720&q=85',
      'https://images.unsplash.com/photo-1524368535928-5b5e00ddc76b?auto=format&fit=crop&w=720&q=85',
      'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=720&q=85',
      'https://images.unsplash.com/photo-1506157786151-b8491531f063?auto=format&fit=crop&w=720&q=85',
    ],
    comedy: [
      'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=720&q=85',
      'https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&w=720&q=85',
      'https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=720&q=85',
      'https://images.unsplash.com/photo-1573496799652-408c2ac9fe98?auto=format&fit=crop&w=720&q=85',
    ],
    visuals: [
      'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1557050543-4d5f4e07ef46?auto=format&fit=crop&w=900&q=85',
    ],
  };

  const source = {
    films: {
      titles: ['The Last Mile', 'Echoes of Kigali', 'Wild River', 'After the Fire', 'The Silent Witness', 'Letters to Mombasa', 'Northern Light', 'Crossroads', 'A Thousand Mornings', 'Broken Crown', 'The Fourth Room', 'Dust and Gold', 'Blue Hour', 'The Final Frame', 'Out of Season', 'Before Sunrise', 'Old Friends', 'Paper Planes', 'The Long Walk Home', 'False Start', 'Undercurrent', 'One More Night', 'City of Dust', 'The Map Maker', 'Falling Stars'],
      genres: ['action', 'romantic', 'thriller', 'scifi', 'adventure'],
      origins: [['rwandan'], ['kenyan'], ['hollywood', 'usa'], ['nollywood'], ['bollywood']],
      people: ['Ishimwe Film Co.', 'Nia Studios', 'Eastline Pictures', 'The New Wave', 'Lumina Films'],
      years: ['2026', '2025', '2025', '2026', '2019'],
      label: 'Film',
    },
    music: {
      titles: ['Midnight in Kacyiru', 'Keep the Fire', 'Sauti Ya Moyo', 'No Looking Back', 'Dawn Chorus', 'Kigali to Nairobi', 'Golden Hour', 'Louder Than Love', 'Malaika', 'On My Way', 'Rift Valley Dreaming', 'Night Ride', 'Nshuti', 'After the Rain', 'New Energy', 'Slow Dance', 'Rhythm of Home', 'Two Hearts', 'Soweto Sun', 'First Light', 'All I Need', 'Runaway Train', 'Kisumu Nights', 'Moonflower', 'Good Enough'],
      genres: ['afrobeat', 'amapiano', 'rhumba', 'pop', 'drill', 'rock'],
      origins: [['rwanda'], ['kenya'], ['uganda'], ['nigeria'], ['south-africa']],
      people: ['Ariel Wayz', 'Kora Nuru', 'Jules K.', 'Mwezi', 'Inzozi'],
      years: ['2026', '2026', '2025', '2025', '2025'],
      label: 'Single',
    },
    comedy: {
      titles: ['The Group Chat', 'Rent Day', 'My Auntie Knows', 'The Last Seat', 'Wedding Season', 'Office Wi-Fi', 'Roommate Rules', 'Call Your Mother', 'The Interview', 'First Date', 'Taxi Stories', 'Sunday Lunch', 'Neighbourhood Watch', 'The Reunion', 'Online Class', 'The Lost Phone', 'Airport Drama', 'Family Meeting', 'Wrong Number', 'The Big Match', 'Kitchen Politics', 'Weekend Plans', 'The Delivery', 'Bus Stop Diaries', 'Village Visit'],
      genres: ['standup', 'skit', 'series'],
      origins: [['rwanda'], ['kenya']],
      people: ['Clation Kibonge', 'Emmy Pro', 'Teta Talks', 'Roga Roga', 'The Funny Side'],
      years: ['2026', '2026', '2025'],
      label: 'Comedy',
    },
    visuals: {
      titles: ['Volcanic Morning', 'Golden Vows', 'The City Wakes', 'On the Move', 'Lake Kivu Blue', 'A Quiet Moment', 'Market Day', 'Red Earth', 'Dreaming in Colour', 'The Long Road', 'At First Light', 'Runway Stories', 'Open Water', 'Homecoming', 'The Mountain Calls', 'Street Rhythm', 'Kitenge', 'Wild Grace', 'Bright Horizons', 'A Place to Rest', 'The Ceremony', 'Smoke and Sun', 'New Beginnings', 'Stillness', 'Into the Green'],
      genres: ['nature', 'wedding', 'portrait', 'travel', 'fashion', 'events'],
      origins: [['rwanda'], ['kenya'], ['uganda'], ['nigeria'], ['south-africa']],
      people: ['Innocent Photos', 'Bella Photography', 'Africa Lens', 'Urban Visuals', 'Nuru Studio'],
      years: ['2026', '2026', '2025', '2025', '2024'],
      label: 'Visual',
    },
  };

  const createItems = (type, config) => config.titles.map((title, index) => ({
    id: `${type}-${index + 1}`,
    title,
    genre: config.genres[index % config.genres.length],
    origin: config.origins[index % config.origins.length],
    creator: config.people[index % config.people.length],
    year: config.years[index % config.years.length],
    image: images[type][index % images[type].length],
    label: config.label,
    created: config.titles.length - index,
    popularity: ((index * 17) + 71) % 100,
    views: 12800 + ((index * 2387) % 66000),
    price: type === 'visuals' ? `${2000 + ((index % 4) * 500)} RWF` : type === 'comedy' ? '1,500 RWF' : type === 'music' ? '1,000 RWF' : `${6000 + ((index % 4) * 2000)} RWF`,
    duration: type === 'films' ? `${1 + (index % 2)}h ${31 + ((index * 7) % 27)}m` : type === 'music' ? `0${2 + (index % 3)}:${String(6 + ((index * 11) % 51)).padStart(2, '0')}` : type === 'comedy' ? `${6 + (index % 11)}:${String(10 + ((index * 7) % 43)).padStart(2, '0')}` : 'High resolution',
  }));

  const items = createItems(page.dataset.catalogPage, source[page.dataset.catalogPage]);
  const results = document.querySelector('#catalog-results');
  const count = document.querySelector('#catalog-count');
  const loadMore = document.querySelector('#load-more');
  const empty = document.querySelector('#empty-catalog');
  const search = document.querySelector('#catalog-search');
  const sort = document.querySelector('#catalog-sort');
  const filterButtons = [...document.querySelectorAll('[data-filter]')];
  const state = { filter: 'all', term: '', sort: 'latest', shown: 20, basket: 0 };

  const compactNumber = (number) => `${number >= 1000 ? `${Math.round(number / 1000)}k` : number} views`;
  const titleCase = (value) => value.replace(/\b\w/g, (letter) => letter.toUpperCase());
  const showToast = (message) => {
    const toast = document.querySelector('.toast');
    toast.textContent = message;
    toast.classList.add('show');
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(() => toast.classList.remove('show'), 2500);
  };
  const matches = (item) => {
    const text = [item.title, item.creator, item.genre, item.year, ...item.origin].join(' ').toLowerCase();
    return (state.filter === 'all' || item.genre === state.filter || item.origin.includes(state.filter) || item.year === state.filter) && text.includes(state.term);
  };
  const sortedItems = () => items.filter(matches).sort((a, b) => {
    if (state.sort === 'trending') return (b.popularity * 1.3 + b.views / 10000) - (a.popularity * 1.3 + a.views / 10000);
    if (state.sort === 'popular') return b.popularity - a.popularity;
    if (state.sort === 'views') return b.views - a.views;
    return b.created - a.created;
  });
  const card = (item) => {
    const type = page.dataset.catalogPage;
    const meta = type === 'films' ? `${titleCase(item.genre)} · ${item.duration}` : type === 'music' ? `${titleCase(item.genre)} · ${item.duration}` : type === 'comedy' ? `${titleCase(item.genre)} · ${item.duration}` : `${titleCase(item.genre)} · ${item.duration}`;
    const canPreview = type === 'music' || type === 'comedy';
    return `<article class="catalog-card catalog-card-${type === 'films' ? 'film' : type}" data-item="${item.id}">
      <div class="catalog-card-media"><img src="${item.image}" alt="Artwork for ${item.title}" loading="lazy"><span class="catalog-card-badge">${item.year}</span>${canPreview ? '<button class="catalog-preview" type="button" aria-label="Preview content">▶</button>' : ''}</div>
      <div class="catalog-card-body"><p class="catalog-card-meta">${meta}</p><h3 title="${item.title}">${item.title}</h3><p class="catalog-card-creator">${item.creator}</p><div class="catalog-card-footer"><span>${item.price}</span><small>${compactNumber(item.views)}</small><button class="card-add" type="button" aria-label="Add ${item.title} to basket">+</button></div></div>
    </article>`;
  };
  const render = () => {
    const filtered = sortedItems();
    const visible = filtered.slice(0, state.shown);
    results.innerHTML = visible.map(card).join('');
    count.textContent = `Showing ${visible.length} of ${filtered.length} ${page.dataset.catalogPage}`;
    loadMore.hidden = state.shown >= filtered.length || filtered.length === 0;
    empty.hidden = filtered.length > 0;
  };
  const resetFilters = () => {
    state.filter = 'all'; state.term = ''; state.shown = 20;
    search.value = '';
    filterButtons.forEach((button) => button.classList.toggle('is-active', button.dataset.filter === 'all'));
    render();
  };

  search.addEventListener('input', () => { state.term = search.value.trim().toLowerCase(); state.shown = 20; render(); });
  sort.addEventListener('change', () => { state.sort = sort.value; render(); });
  filterButtons.forEach((button) => button.addEventListener('click', () => {
    state.filter = button.dataset.filter; state.shown = 20;
    filterButtons.forEach((item) => item.classList.toggle('is-active', item === button));
    render();
  }));
  loadMore.addEventListener('click', () => { state.shown += 8; render(); });
  document.querySelector('#clear-catalog-filter').addEventListener('click', resetFilters);
  results.addEventListener('click', (event) => {
    const add = event.target.closest('.card-add');
    const preview = event.target.closest('.catalog-preview');
    if (add) { state.basket += 1; add.textContent = '✓'; showToast('Added to your basket'); }
    if (preview) { const playing = preview.classList.toggle('is-playing'); preview.textContent = playing ? 'Ⅱ' : '▶'; showToast(playing ? '30-second preview playing' : 'Preview paused'); }
  });
  const menu = document.querySelector('.catalog-menu-toggle');
  const nav = document.querySelector('.catalog-nav nav');
  menu?.addEventListener('click', () => { const open = menu.getAttribute('aria-expanded') === 'true'; menu.setAttribute('aria-expanded', String(!open)); nav.classList.toggle('is-open', !open); });
  render();
});
