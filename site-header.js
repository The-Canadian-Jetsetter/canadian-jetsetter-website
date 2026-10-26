// Site header behaviour (markup from inject_header.py, styles in site-header.css).
// Ported from the cards site's SiteMenu.astro.
// Desktop: Offerings (and Cards) open full-width panels that slide down from under the bar.
// Mobile: the menu button opens a panel from the right, over a dimmed page; dropdowns expand in place.
// Glass pages: the bar turns solid once the hero has scrolled out from under it.
(function () {
  const root = document.querySelector('[data-site-header]');
  if (!root) return;

  // ---- Desktop panels: one open at a time ----
  const toggles = [...root.querySelectorAll('[data-panel-toggle]')];
  const panelFor = (b) => root.querySelector(`[data-panel="${b.dataset.panelToggle}"]`);
  const openToggle = () => toggles.find((b) => b.getAttribute('aria-expanded') === 'true');

  const setPanel = (b, open) => {
    b.setAttribute('aria-expanded', String(open));
    panelFor(b).classList.toggle('open', open);
  };
  const closePanels = () => toggles.forEach((b) => setPanel(b, false));

  toggles.forEach((b) => b.addEventListener('click', () => {
    const wasOpen = b.getAttribute('aria-expanded') === 'true';
    closePanels();
    if (!wasOpen) setPanel(b, true);
  }));
  document.addEventListener('click', (e) => {
    if (openToggle() && !root.contains(e.target)) closePanels();
  });

  // ---- Mobile drawer ----
  const openBtn = root.querySelector('[data-drawer-open]');
  const closeBtn = root.querySelector('[data-drawer-close]');
  const drawer = root.querySelector('[data-drawer]');
  const scrim = root.querySelector('[data-drawer-scrim]');
  // Everything outside the header is made inert while the drawer is open
  const outside = () => [...document.body.children].filter((el) => el !== root);
  const isDrawerOpen = () => drawer.classList.contains('open');

  const setDrawer = (open) => {
    drawer.classList.toggle('open', open);
    scrim.classList.toggle('open', open);
    openBtn.setAttribute('aria-expanded', String(open));
    document.documentElement.classList.toggle('site-header-locked', open);
    outside().forEach((el) => (el.inert = open));
    if (open) closeBtn.focus();
    else openBtn.focus();
  };
  openBtn.addEventListener('click', () => setDrawer(true));
  closeBtn.addEventListener('click', () => setDrawer(false));
  scrim.addEventListener('click', () => setDrawer(false));

  // Offerings (and Cards) expand in place
  root.querySelectorAll('[data-sub-toggle]').forEach((b) => b.addEventListener('click', () => {
    const open = b.getAttribute('aria-expanded') !== 'true';
    b.setAttribute('aria-expanded', String(open));
    document.getElementById(b.getAttribute('aria-controls')).hidden = !open;
  }));

  // Keep Tab inside the drawer while it's open
  drawer.addEventListener('keydown', (e) => {
    if (e.key !== 'Tab') return;
    const focusable = [...drawer.querySelectorAll('a[href], button')].filter((el) => el.offsetParent !== null);
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  });

  // Escape closes whichever menu is open and returns focus to its button
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    if (isDrawerOpen()) { setDrawer(false); return; }
    const b = openToggle();
    if (b) { closePanels(); b.focus(); }
  });

  // Switching between mobile and desktop widths closes everything
  matchMedia('(min-width: 900px)').addEventListener('change', () => {
    closePanels();
    if (isDrawerOpen()) setDrawer(false);
  });

  // ---- Glass pages: solid once the hero is no longer behind the bar ----
  const hero = document.body.classList.contains('site-header-glass')
    && document.querySelector('[data-site-header-hero]');
  if (hero) {
    const bar = root.querySelector('.site-header__bar');
    let queued = false;
    const update = () => {
      queued = false;
      root.classList.toggle('is-past-hero', hero.getBoundingClientRect().bottom <= bar.offsetHeight);
    };
    const queue = () => { if (!queued) { queued = true; requestAnimationFrame(update); } };
    window.addEventListener('scroll', queue, { passive: true });
    window.addEventListener('resize', queue);
    update();
  }
  // Fades are switched on after the first check (see site-header.css)
  requestAnimationFrame(() => root.classList.add('is-ready'));
})();
