document.addEventListener('DOMContentLoaded', () => {
  const search = document.querySelector('#creator-search');
  const cards = [...document.querySelectorAll('.directory-card')];
  const buttons = [...document.querySelectorAll('[data-creator-filter]')];
  const count = document.querySelector('#creator-count');
  const empty = document.querySelector('#empty-creators');
  const clear = document.querySelector('#clear-creator-filters');
  const menu = document.querySelector('.catalog-menu-toggle');
  const nav = document.querySelector('.catalog-nav nav');
  if (!search) return;

  let category = 'all';
  const render = () => {
    const term = search.value.trim().toLowerCase();
    let visible = 0;
    cards.forEach((card) => {
      const matches = (category === 'all' || card.dataset.category === category) && card.dataset.creatorName.includes(term);
      card.classList.toggle('is-hidden', !matches);
      if (matches) visible += 1;
    });
    count.textContent = `${visible} creator${visible === 1 ? '' : 's'}`;
    empty.hidden = visible > 0;
  };

  search.addEventListener('input', render);
  buttons.forEach((button) => button.addEventListener('click', () => {
    category = button.dataset.creatorFilter;
    buttons.forEach((item) => item.classList.toggle('is-active', item === button));
    render();
  }));
  clear.addEventListener('click', () => { search.value = ''; category = 'all'; buttons.forEach((button) => button.classList.toggle('is-active', button.dataset.creatorFilter === 'all')); render(); });
  menu?.addEventListener('click', () => { const open = menu.getAttribute('aria-expanded') === 'true'; menu.setAttribute('aria-expanded', String(!open)); nav.classList.toggle('is-open', !open); });
  render();
});
