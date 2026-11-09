(() => {
  'use strict';
  const button = document.querySelector('.menu-button');
  const nav = document.querySelector('#nav');
  if (!button || !nav) return;
  const close = () => { nav.classList.remove('is-open'); button.setAttribute('aria-expanded', 'false'); button.setAttribute('aria-label', 'Open menu'); };
  button.addEventListener('click', () => {
    const open = nav.classList.toggle('is-open');
    button.setAttribute('aria-expanded', String(open));
    button.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  });
  nav.querySelectorAll('a').forEach(link => link.addEventListener('click', close));
  document.addEventListener('keydown', event => { if (event.key === 'Escape') close(); });
  document.addEventListener('click', event => { if (!nav.contains(event.target) && !button.contains(event.target)) close(); });
})();

// Project filters progressively enhance the Projects page. Without JS all cases remain visible.
(() => {
  'use strict';
  const filters = Array.from(document.querySelectorAll('button[data-filter]'));
  const cards = Array.from(document.querySelectorAll('[data-project-status]'));
  if (!filters.length || !cards.length) return;
  filters.forEach(button => button.addEventListener('click', () => {
    const filter = button.dataset.filter;
    let visible = 0;
    for (const card of cards) {
      const matches = filter === 'all' || card.dataset.projectStatus === filter;
      card.hidden = !matches;
      if (matches) visible++;
    }
    filters.forEach(el => {
      const active = el === button;
      el.classList.toggle('is-selected', active);
      el.setAttribute('aria-pressed', String(active));
    });
    const empty = document.querySelector('.empty-filter');
    if (empty) empty.hidden = visible > 0;
  }));
})();


// V2.3 — Focus-area navigation; client-side enhancement on top of visible public case list.
(() => {
  'use strict';
  const root = document.querySelector('[data-focus-page]');
  if (!root) return;
  const allowed = new Set(['all','intune','entra','defender','sentinel']);
  const raw = new URLSearchParams(window.location.search).get('area') || 'all';
  const area = allowed.has(raw) ? raw : 'all';
  const titles = {all:'All documented work',intune:'Microsoft Intune',entra:'Microsoft Entra ID',defender:'Microsoft Defender',sentinel:'Microsoft Sentinel'};
  let count = 0;
  root.querySelectorAll('[data-focus-item]').forEach(card => {
    const areas = (card.getAttribute('data-focus-areas') || '').split(/\s+/);
    const match = area === 'all' || areas.includes(area);
    card.hidden = !match;
    if (match) count++;
  });
  root.querySelectorAll('[data-focus-filter]').forEach(link => {
    if (link.getAttribute('data-focus-filter') === area) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  });
  const heading = root.querySelector('#focus-selected-title');
  if (heading) heading.textContent = titles[area];
  const countLabel = root.querySelector('#focus-count');
  if (countLabel) countLabel.textContent = count === 1 ? '1 relevant item' : count + ' relevant items';
  const empty = root.querySelector('#focus-empty');
  if (empty) empty.hidden = count > 0;
})();
