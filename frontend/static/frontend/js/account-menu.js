document.addEventListener('DOMContentLoaded', () => {
  const accountMenus = [...document.querySelectorAll('[data-account-menu]')];

  const closeMenu = (menu) => {
    const trigger = menu.querySelector('.account-menu-trigger');
    const dropdown = menu.querySelector('.account-dropdown');
    trigger?.setAttribute('aria-expanded', 'false');
    if (dropdown) dropdown.hidden = true;
  };

  accountMenus.forEach((menu) => {
    const trigger = menu.querySelector('.account-menu-trigger');
    const dropdown = menu.querySelector('.account-dropdown');
    if (!trigger || !dropdown) return;

    trigger.addEventListener('click', () => {
      const willOpen = dropdown.hidden;
      accountMenus.forEach(closeMenu);
      dropdown.hidden = !willOpen;
      trigger.setAttribute('aria-expanded', String(willOpen));
    });

    menu.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        closeMenu(menu);
        trigger.focus();
      }
    });
  });

  document.addEventListener('click', (event) => {
    accountMenus.forEach((menu) => {
      if (!menu.contains(event.target)) closeMenu(menu);
    });
  });
});
