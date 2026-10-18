/* ESSIMPLEX site behaviour. Progressive enhancement only: every element is
   readable without this file. Motion respects prefers-reduced-motion and
   only animates transform/opacity (counters update text). */
(function () {
  "use strict";

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hasIO = "IntersectionObserver" in window;

  /* ---------- Sticky header: solid once the page scrolls ---------- */
  var header = document.getElementById("site-header");
  if (header) {
    var ticking = false;
    var onScroll = function () {
      header.classList.toggle("is-scrolled", window.scrollY > 24);
      ticking = false;
    };
    window.addEventListener("scroll", function () {
      if (!ticking) { ticking = true; requestAnimationFrame(onScroll); }
    }, { passive: true });
    onScroll();
  }

  /* ---------- Mobile navigation ---------- */
  var toggle = document.getElementById("nav-toggle");
  var nav = document.getElementById("primary-nav");
  if (toggle && nav) {
    var setOpen = function (open) {
      nav.classList.toggle("is-open", open);
      if (header) header.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    };
    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) setOpen(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        setOpen(false);
        toggle.focus();
      }
    });
    window.matchMedia("(min-width: 881px)").addEventListener("change", function (m) {
      if (m.matches) setOpen(false);
    });
  }

  /* ---------- Animated counters on fact stats ---------- */
  var counters = Array.prototype.slice.call(document.querySelectorAll("[data-count]"));
  var runCount = function (el) {
    var target = parseFloat(el.getAttribute("data-count"));
    var start = null;
    var dur = 1300;
    var step = function (t) {
      if (start === null) start = t;
      var p = Math.min(1, (t - start) / dur);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = String(Math.round(target * eased));
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };

  /* ---------- Reveal on enter ---------- */
  var revealables = document.querySelectorAll("[data-reveal]");
  if (!hasIO || reduce) {
    revealables.forEach(function (el) { el.classList.add("is-in"); });
  } else {
    var revealIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          revealIO.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
    revealables.forEach(function (el) { revealIO.observe(el); });

    if (counters.length) {
      counters.forEach(function (el) { el.textContent = "0"; });
      var countIO = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            runCount(entry.target);
            countIO.unobserve(entry.target);
          }
        });
      }, { threshold: 0.6 });
      counters.forEach(function (el) { countIO.observe(el); });
    }
  }

  /* ---------- Loops that only run while on screen ---------- */
  var toggleOnView = function (selector, cls) {
    var els = document.querySelectorAll(selector);
    if (!hasIO || !els.length) return;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) { entry.target.classList.toggle(cls, entry.isIntersecting); });
    });
    els.forEach(function (el) { io.observe(el); });
  };
  toggleOnView(".diagram", "is-playing");
  toggleOnView(".live", "is-live");

  /* ---------- Nody Bot check-in sequence: steps advance as you scroll ---------- */
  var how = document.querySelector(".how");
  if (how && hasIO) {
    var seq = how.querySelector(".seq");
    var steps = Array.prototype.slice.call(how.querySelectorAll(".step"));
    var nodes = Array.prototype.slice.call(how.querySelectorAll(".seq__node"));
    var last = steps.length - 1;
    var setStep = function (n) {
      steps.forEach(function (s, i) {
        s.classList.toggle("is-current", i === n);
        s.classList.toggle("is-done", i < n);
      });
      nodes.forEach(function (d, i) {
        d.classList.toggle("is-current", i === n);
        d.classList.toggle("is-done", i <= n);
      });
      if (seq) seq.style.setProperty("--seq", n <= 0 ? 0 : n / last);
    };
    how.classList.add("is-stepping");
    if (seq) seq.classList.add("is-stepping");
    setStep(-1);
    var stepIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) setStep(steps.indexOf(entry.target));
      });
    }, { rootMargin: "-42% 0px -42% 0px" });
    steps.forEach(function (s) { stepIO.observe(s); });
  }
})();
