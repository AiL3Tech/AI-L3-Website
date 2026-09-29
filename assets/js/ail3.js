/* AI L3 Tech — nav toggle, scroll reveal, work carousels. No dependencies. */
(function () {
  'use strict';

  /* ---- Mobile nav ---- */
  var toggle = document.querySelector('.nav-toggle');
  var links = document.getElementById('nav-links');

  if (toggle && links) {
    /* Holding the reading position across the lock. Pinning the body is what
       stops the page scrolling behind the drawer, but a pinned body has no
       scroll of its own, so the offset has to be carried in top and handed
       back on close, or the visitor reopens the page somewhere else. */
    var lockedAt = 0;

    function lockScroll() {
      lockedAt = window.scrollY || window.pageYOffset || 0;
      document.body.style.top = (-lockedAt) + 'px';
      document.body.classList.add('nav-open');
    }

    function unlockScroll() {
      if (!document.body.classList.contains('nav-open')) { return; }
      document.body.classList.remove('nav-open');
      document.body.style.top = '';
      /* the page scrolls smoothly by default, and putting someone back where
         they were is not a journey they should watch */
      var de = document.documentElement, prev = de.style.scrollBehavior;
      de.style.scrollBehavior = 'auto';
      window.scrollTo(0, lockedAt);
      de.style.scrollBehavior = prev;
    }

    function openNav() {
      toggle.setAttribute('aria-expanded', 'true');
      links.classList.add('is-open');
      lockScroll();
    }

    function closeNav(refocus) {
      toggle.setAttribute('aria-expanded', 'false');
      links.classList.remove('is-open');
      unlockScroll();
      if (refocus) { toggle.focus(); }
    }

    /* Rotating a tablet from portrait to landscape crosses the breakpoint and
       hides the toggle button. Without this the drawer state survives the
       switch and body.nav-open keeps the page locked with nothing left to
       tap, so the visitor is stuck on a page that will not scroll. */
    var wide = window.matchMedia('(min-width: 861px)');
    var onCross = function (e) { if (e.matches) { closeNav(false); } };
    if (wide.addEventListener) {
      wide.addEventListener('change', onCross);
    } else if (wide.addListener) {
      wide.addListener(onCross);               /* older Safari */
    }

    toggle.addEventListener('click', function () {
      if (toggle.getAttribute('aria-expanded') === 'true') { closeNav(false); }
      else { openNav(); }
    });

    links.addEventListener('click', function (e) {
      if (e.target.closest('a')) { closeNav(false); }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && links.classList.contains('is-open')) { closeNav(true); }
    });
  }


  /* ---- Booking calendar: show a way through if the embed is blocked ----
     The calendar is a third-party iframe, and blockers deny those routinely.
     A denied request means the load event never fires, so if it has not fired
     by the time the timer runs out, swap the empty frame for real options. */
  var frame = document.querySelector('[data-booking]');
  var fallback = document.querySelector('[data-booking-fallback]');

  if (frame && fallback) {
    var iframe = frame.querySelector('iframe');
    var loaded = false;

    iframe.addEventListener('load', function () { loaded = true; });

    setTimeout(function () {
      if (!loaded) {
        frame.hidden = true;
        fallback.hidden = false;
      }
    }, 6000);
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

/* ---- Work showcase carousels ---------------------------------------------
   Galleries of product screens inside the example-build cards. A separate IIFE
   on purpose: the reveal block above returns early under reduced motion, and
   these still have to work there - just without the sliding or the autoplay.

   Autoplay stops on hover, on focus, when the card scrolls out of view, when
   the tab is hidden, and from its own button. 2.2.2 asks for a real control,
   not only a hover, and any manual move stops it for good so nothing fights
   the reader. The track is the only thing transformed and it holds nothing but
   images, so no positioned child can re-anchor to it mid-animation.         */
(function () {
  'use strict';

  var motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  var DELAY = 5200;
  var carousels = document.querySelectorAll('[data-carousel]');
  if (!carousels.length) return;

  Array.prototype.forEach.call(carousels, function (root) {
    var track = root.querySelector('.work-track');
    var slides = Array.prototype.slice.call(root.querySelectorAll('.work-slide'));
    var dots = Array.prototype.slice.call(root.querySelectorAll('.work-dot'));
    var caption = root.querySelector('.work-caption');
    var toggle = root.querySelector('.work-pause');
    if (!track || slides.length < 2 || dots.length !== slides.length) return;

    var at = 0, timer = null, seen = false, held = false, stopped = false, primed = false;

    /* Off-screen cards should cost nothing, but a slide that is still lazy when
       it slides in arrives blank. So the moment a card is on screen, drop the
       lazy flag on all of its images and let them fetch ahead of their turn. */
    function prime() {
      if (primed) return;
      primed = true;
      slides.forEach(function (s) {
        var img = s.querySelector('img');
        if (img) img.removeAttribute('loading');
      });
    }

    function render() {
      track.style.transform = 'translateX(' + (-at * 100) + '%)';
      for (var k = 0; k < dots.length; k++) {
        if (k === at) { dots[k].setAttribute('aria-current', 'true'); }
        else { dots[k].removeAttribute('aria-current'); }
        dots[k].tabIndex = k === at ? 0 : -1;
      }
      if (caption) caption.textContent = slides[at].getAttribute('data-label') || '';
    }

    function go(n) {
      at = (n + slides.length) % slides.length;
      render();
    }

    function play() {
      if (timer || stopped || held || !seen || motion.matches) return;
      timer = window.setInterval(function () { go(at + 1); }, DELAY);
    }
    function pause() {
      if (timer) { window.clearInterval(timer); timer = null; }
    }
    function setStopped(v) {
      stopped = v;
      if (toggle) toggle.setAttribute('aria-pressed', v ? 'true' : 'false');
      if (v) { pause(); } else { play(); }
    }

    /* a deliberate move is a decision to steer it by hand */
    function manual(n) { setStopped(true); go(n); }

    dots.forEach(function (dot, k) {
      dot.addEventListener('click', function () { manual(k); });
      dot.addEventListener('keydown', function (e) {
        var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        if (!d) return;
        e.preventDefault();
        manual(at + d);
        dots[at].focus();
      });
    });

    if (toggle) {
      toggle.addEventListener('click', function () { setStopped(!stopped); });
    }

    root.addEventListener('pointerenter', function () { held = true; pause(); });
    root.addEventListener('pointerleave', function () { held = false; play(); });
    root.addEventListener('focusin', function () { held = true; pause(); });
    root.addEventListener('focusout', function () {
      if (!root.contains(document.activeElement)) { held = false; play(); }
    });

    /* Swipe, for the single-column layout where these are thumb-sized. The
       gesture only counts as a swipe when it is more sideways than up, so
       flicking the page along does not shuffle the slides, and pointercancel
       resets it for the times the browser takes the gesture anyway. */
    var x0 = null, y0 = null;
    root.addEventListener('pointerdown', function (e) {
      if (e.pointerType === 'mouse') return;
      x0 = e.clientX;
      y0 = e.clientY;
    });
    root.addEventListener('pointercancel', function () { x0 = y0 = null; });
    root.addEventListener('pointerup', function (e) {
      if (x0 === null) return;
      var dx = e.clientX - x0, dy = e.clientY - y0;
      x0 = y0 = null;
      if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) {
        manual(at + (dx < 0 ? 1 : -1));
      }
    });

    document.addEventListener('visibilitychange', function () {
      if (document.hidden) { pause(); } else { play(); }
    });

    /* Safari only grew addEventListener on a MediaQueryList in 14. Without the
       guard the throw takes every carousel on the page down with it. */
    if (motion.addEventListener) {
      motion.addEventListener('change', function () {
        if (motion.matches) { pause(); } else { play(); }
      });
    }

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          seen = entry.isIntersecting;
          if (seen) { prime(); play(); } else { pause(); }
        });
      }, { threshold: 0.35 }).observe(root);
    } else {
      seen = true;
      prime();
    }

    render();
    play();
  });
})();
