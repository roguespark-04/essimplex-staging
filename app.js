/* ESSIMPLEX site behaviour. Progressive enhancement only: every element is
   readable and usable without this file (the check-in wire is then fully drawn).
   Scroll-linked state works under prefers-reduced-motion too; only autoplay,
   entrance motion and transitions are switched off (see styles.css). */
(function () {
  "use strict";

  var wideMq = window.matchMedia("(min-width: 900px)");
  /* older Android WebViews only have addListener */
  var onChange = function (mq, fn) {
    if (mq.addEventListener) mq.addEventListener("change", fn);
    else if (mq.addListener) mq.addListener(fn);
  };

  /* ---------- Menu (phone and tablet) ---------- */
  var header = document.getElementById("site-header");
  var toggle = document.getElementById("nav-toggle");
  var nav = document.getElementById("primary-nav");
  if (toggle && nav) {
    var setOpen = function (open) {
      nav.classList.toggle("is-open", open);
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
    document.addEventListener("click", function (e) {
      if (toggle.getAttribute("aria-expanded") === "true" && header && !header.contains(e.target)) setOpen(false);
    });
    onChange(wideMq, function () { if (wideMq.matches) setOpen(false); });
  }

  /* ---------- Hero wires: pause the travelling pulse while off screen ---------- */
  var hero = document.querySelector(".hero");
  if (hero && "IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      hero.classList.toggle("is-off", !entries[0].isIntersecting);
    }).observe(hero);
  }

  /* ---------- Check-in wire: filled as the sequence scrolls ----------
     Progress is read straight from the scroll position (no autoplay, no easing), so it is
     also used when the system asks for reduced motion. Only transitions are switched off (CSS). */
  var seqs = Array.prototype.slice.call(document.querySelectorAll("[data-seq]"));
  if (!seqs.length) return;

  var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };
  var items = seqs.map(function (el) {
    return {
      el: el,
      strip: el.querySelector(".seq__strip"),
      plot: el.querySelector("[data-trace]"),
      clips: Array.prototype.slice.call(el.querySelectorAll(".seq-clip")),
      markers: Array.prototype.slice.call(el.querySelectorAll(".seq__marker")),
      steps: Array.prototype.slice.call(el.querySelectorAll(".seq__step"))
    };
  });

  var paint = function (it, x) {
    it.clips.forEach(function (r) {
      r.setAttribute("width", String(100 + x * parseFloat(r.getAttribute("data-w"))));
    });
    it.markers.forEach(function (m, i) {
      var on = x >= parseFloat(m.getAttribute("data-at")) - 0.015;
      m.classList.toggle("is-on", on);
      if (it.steps[i]) it.steps[i].classList.toggle("is-on", on);
    });
  };

  var progress = function (it) {
    var vh = window.innerHeight;
    if (wideMq.matches) {
      /* desktop: the whole plot is in view; draw it as it travels up the screen */
      var r = it.plot.getBoundingClientRect();
      return clamp((vh * 0.9 - r.top) / (r.height + vh * 0.45), 0, 1);
    }
    /* phone/tablet: the strip is pinned under the header; the list scrolling past it drives the line */
    var anchor = it.strip.getBoundingClientRect().bottom + 24;
    var c = it.steps.map(function (s) { var b = s.getBoundingClientRect(); return b.top + Math.min(b.height, 120) / 2; });
    var n = c.length;
    var xs = it.markers.map(function (m) { return parseFloat(m.getAttribute("data-at")); });
    if (anchor <= c[0]) return clamp(xs[0] * (1 - (c[0] - anchor) / 240), 0, xs[0]);
    for (var i = 0; i < n - 1; i++) {
      if (anchor <= c[i + 1]) return xs[i] + (xs[i + 1] - xs[i]) * ((anchor - c[i]) / (c[i + 1] - c[i]));
    }
    return clamp(xs[n - 1] + (1 - xs[n - 1]) * ((anchor - c[n - 1]) / 160), xs[n - 1], 1);
  };

  var root = document.documentElement;
  var showAll = function () {
    root.classList.remove("js-seq");
    items.forEach(function (it) { paint(it, 1); });
  };
  var ticking = false;
  var update = function () {
    ticking = false;
    try {
      items.forEach(function (it) { paint(it, progress(it)); });
    } catch (e) {
      /* anything unexpected: fall back to the readable, fully drawn graph */
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      showAll();
    }
  };
  var onScroll = function () {
    if (ticking) return;
    ticking = true;
    if (window.requestAnimationFrame) window.requestAnimationFrame(update); else update();
  };

  try {
    root.classList.add("js-seq");
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    window.addEventListener("orientationchange", onScroll);
    window.addEventListener("load", onScroll);
    onChange(wideMq, onScroll);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(onScroll);
    update();
  } catch (e) {
    showAll();
  }
})();
