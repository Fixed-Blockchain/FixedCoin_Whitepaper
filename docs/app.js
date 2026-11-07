const toggle = document.querySelector('.nav-toggle');
const contents = document.querySelector('.contents');

if (toggle && contents) {
  toggle.addEventListener('click', () => {
    const open = contents.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
  });
  contents.addEventListener('click', (event) => {
    if (event.target.matches('a') && window.innerWidth <= 900) {
      contents.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });
}

const navLinks = [...document.querySelectorAll('.contents > a')];
const sections = navLinks
  .map((link) => document.querySelector(link.getAttribute('href')))
  .filter(Boolean);

if ('IntersectionObserver' in window && sections.length) {
  const observer = new IntersectionObserver((entries) => {
    const visible = entries
      .filter((entry) => entry.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!visible) return;
    navLinks.forEach((link) => {
      const active = link.getAttribute('href') === `#${visible.target.id}`;
      link.classList.toggle('active', active);
      if (active) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }, { rootMargin: '-18% 0px -70% 0px', threshold: [0, 0.2, 0.6] });
  sections.forEach((section) => observer.observe(section));
}
