/* AI L3 Tech — nav toggle + scroll reveal. No dependencies. */
(function () {
  'use strict';

  /* ---- Mobile nav ---- */
  var toggle = document.querySelector('.nav-toggle');
  var links = document.getElementById('nav-links');

  if (toggle && links) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      links.classList.toggle('is-open', !open);
      document.body.classList.toggle('nav-open', !open);
    });

    links.addEventListener('click', function (e) {
      if (e.target.closest('a')) {
        toggle.setAttribute('aria-expanded', 'false');
        links.classList.remove('is-open');
        document.body.classList.remove('nav-open');
      }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && links.classList.contains('is-open')) {
        toggle.setAttribute('aria-expanded', 'false');
        links.classList.remove('is-open');
        document.body.classList.remove('nav-open');
        toggle.focus();
      }
    });
  }

  /* ---- Vertical switcher: ARIA tabs, arrow-key navigable ----
     Without JS every panel stays visible, so the content is never hidden. */
  var tablist = document.querySelector('[data-vtabs]');

  if (tablist) {
    var tabs = Array.prototype.slice.call(tablist.querySelectorAll('[role="tab"]'));
    var panels = tabs.map(function (t) {
      return document.getElementById(t.getAttribute('aria-controls'));
    });

    var select = function (i, moveFocus) {
      tabs.forEach(function (t, j) {
        t.setAttribute('aria-selected', String(j === i));
        t.tabIndex = j === i ? 0 : -1;
        if (panels[j]) { panels[j].hidden = j !== i; }
      });
      if (moveFocus) { tabs[i].focus(); }
    };

    tablist.addEventListener('click', function (e) {
      var t = e.target.closest('[role="tab"]');
      if (t) { select(tabs.indexOf(t)); }
    });

    tablist.addEventListener('keydown', function (e) {
      var i = tabs.indexOf(document.activeElement);
      if (i < 0) { return; }
      var n;
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { n = (i + 1) % tabs.length; }
      else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { n = (i - 1 + tabs.length) % tabs.length; }
      else if (e.key === 'Home') { n = 0; }
      else if (e.key === 'End') { n = tabs.length - 1; }
      else { return; }
      e.preventDefault();
      select(n, true);
    });

    select(0);
  }

  /* ---- Scroll reveal (skipped entirely under reduced motion) ---- */
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var targets = document.querySelectorAll('.reveal, .reveal-stagger');

  if (reduced || !('IntersectionObserver' in window)) {
    Array.prototype.forEach.call(targets, function (el) { el.classList.add('is-in'); });
    return;
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      }
    });
  }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });

  Array.prototype.forEach.call(targets, function (el) { io.observe(el); });
})();
