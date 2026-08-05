document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.mobile-menu-toggle');
  const nav = document.querySelector('.primary-nav');
  const search = document.querySelector('#site-search');
  const basketCount = document.querySelector('.basket-count');
  const toast = document.querySelector('.toast');
  let basketItems = 0;
  let toastTimer;

  const showToast = (message) => {
    toast.textContent = message;
    toast.classList.add('show');
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove('show'), 2600);
  };

  toggle?.addEventListener('click', () => {
    const isOpen = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!isOpen));
    nav.classList.toggle('is-open', !isOpen);
  });

  nav?.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      nav.querySelectorAll('a').forEach((item) => item.classList.remove('active'));
      link.classList.add('active');
      toggle?.setAttribute('aria-expanded', 'false');
      nav.classList.remove('is-open');
    });
  });

  document.querySelectorAll('.add-to-basket').forEach((button) => {
    button.addEventListener('click', () => {
      basketItems += 1;
      basketCount.textContent = basketItems;
      showToast('Added to your basket');
    });
  });

  document.querySelectorAll('.play-button').forEach((button) => {
    button.addEventListener('click', () => {
      const isPlaying = button.classList.toggle('is-playing');
      button.textContent = isPlaying ? 'Ⅱ' : '▶';
      button.setAttribute('aria-label', isPlaying ? 'Pause preview' : 'Play preview');
      showToast(isPlaying ? '30-second preview playing' : 'Preview paused');
    });
  });

  document.querySelectorAll('.hero-dots button').forEach((dot) => {
    dot.addEventListener('click', () => {
      document.querySelectorAll('.hero-dots button').forEach((item) => item.classList.remove('is-current'));
      dot.classList.add('is-current');
    });
  });

  search?.addEventListener('input', () => {
    const term = search.value.trim().toLowerCase();
    document.querySelectorAll('[data-searchable]').forEach((card) => {
      card.classList.toggle('is-filtered', Boolean(term) && !card.dataset.searchable.includes(term));
    });
  });

  document.addEventListener('keydown', (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      search?.focus();
    }
  });

  document.querySelector('.newsletter form')?.addEventListener('submit', (event) => {
    event.preventDefault();
    const email = document.querySelector('#newsletter-email');
    if (email.value.trim()) {
      email.value = '';
      showToast('You are on the JAXMORA list. Welcome!');
    }
  });
});
