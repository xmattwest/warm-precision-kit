/* Warm Precision scene lab: the in-page GSAP specimens on the Scenes handbook page.
   Every specimen is authored in its finished state. Script builds a timeline from that
   state back to the start, so a blocked script or reduced motion still shows the whole
   figure. Each timeline is exposed on window.wpScenes for frame-by-frame review. */
(function () {
  "use strict";
  var gsap = window.gsap;
  if (!gsap) return;
  var plugins = [window.ScrollTrigger, window.Flip, window.DrawSVGPlugin, window.MorphSVGPlugin, window.MotionPathPlugin]
    .filter(Boolean);
  gsap.registerPlugin.apply(gsap, plugins);
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var scenes = window.wpScenes = {};

  /* Shared transport: a button and a slider bound to one timeline. */
  function transport(id, tl) {
    var bar = document.querySelector('.lab-controls[data-for="' + id + '"]');
    if (!bar) return;
    var button = bar.querySelector("button"), range = bar.querySelector("input"), out = bar.querySelector("output");
    function sync() {
      range.value = String(tl.progress());
      out.textContent = tl.progress() >= 1 ? "Finished frame" : tl.time().toFixed(1) + " / " + tl.duration().toFixed(1) + " s";
      button.textContent = tl.isActive() ? "Pause" : tl.progress() >= 1 ? "Replay" : "Play";
    }
    tl.eventCallback("onUpdate", sync);
    tl.eventCallback("onComplete", sync);
    button.addEventListener("click", function () {
      if (tl.isActive()) tl.pause(); else if (tl.progress() >= 1) tl.restart(); else tl.play();
      sync();
    });
    range.addEventListener("input", function () { tl.pause(); tl.progress(Number(range.value)); sync(); });
    bar.hidden = false;
    sync();
  }

  /* Play once when half the figure is in view; never on reduced motion. */
  function onView(el, fn) {
    if (reduce) return;
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { seen.disconnect(); fn(); } });
    }, { threshold: 0.5 });
    seen.observe(el);
  }

  /* 1. The brief: a seed drops, roots reach down, a sprout opens. */
  var seed = document.getElementById("lab-seed");
  if (seed && window.MotionPathPlugin && window.DrawSVGPlugin && window.MorphSVGPlugin) {
    var tl = gsap.timeline({ paused: true });
    tl.fromTo("#lab-seed-body", { rotation: 0 }, {
        rotation: 0, motionPath: { path: "#lab-fall", start: 0, end: 1 }, duration: 0.8, ease: "power2.in" }, 0)
      .fromTo("#lab-seed-body", { rotation: 0 }, { rotation: 24, duration: 0.3, ease: "power2.out" }, 0.8)
      .fromTo(".lab-root", { drawSVG: "0%" }, { drawSVG: "100%", duration: 0.7, stagger: 0.15, ease: "power2.out" }, 0.95)
      .fromTo("#lab-stem", { drawSVG: "0%" }, { drawSVG: "100%", duration: 0.8, ease: "power2.inOut" }, 1.45);
    seed.querySelectorAll(".lab-leaf").forEach(function (leaf, i) {
      var at = 2.15 + i * 0.15;
      tl.fromTo(leaf, { opacity: 0 }, { opacity: 1, duration: 0.1, ease: "none" }, at)
        .fromTo(leaf, { morphSVG: leaf.getAttribute("data-bud") }, { morphSVG: leaf.getAttribute("d"), duration: 0.6, ease: "power3.out" }, at);
    });
    tl.progress(1);
    scenes.seed = tl;
    transport("lab-seed", tl);
    onView(seed, function () { tl.restart(); });
  }

  /* 2. Scroll: one stacked bar of 100% moves apart into four ranked bars. */
  var split = document.getElementById("lab-split");
  if (split) {
    var st = gsap.timeline({ paused: true });
    split.querySelectorAll(".lab-bar").forEach(function (bar) {
      st.fromTo(bar, { attr: { x: Number(bar.getAttribute("data-stack-x")), y: Number(bar.getAttribute("data-stack-y")) } },
        { attr: { x: Number(bar.getAttribute("x")), y: Number(bar.getAttribute("y")) }, duration: 1, ease: "power2.inOut" }, 0);
    });
    st.fromTo(split.querySelector(".lab-early"), { opacity: 1 }, { opacity: 0, duration: 0.2, ease: "none" }, 0.05)
      .fromTo(split.querySelectorAll(".lab-late"), { opacity: 0 }, { opacity: 1, duration: 0.25, stagger: 0.04, ease: "none" }, 0.5);
    st.progress(1);
    scenes.split = st;
    if (!reduce && window.ScrollTrigger) {
      window.ScrollTrigger.create({ trigger: split, start: "top 80%", end: "bottom 40%", scrub: 0.4, animation: st });
    }
  }

  /* 3. Flip: values change first, then rows move to their new rank. */
  var rank = document.getElementById("lab-rank");
  if (rank && window.Flip) {
    var states = JSON.parse(rank.getAttribute("data-states"));
    var peak = Number(rank.getAttribute("data-peak"));
    var list = rank.querySelector(".lab-rank-list");
    var status = rank.querySelector(".lab-rank-status");
    var buttons = rank.querySelectorAll("[data-season]");
    var change = null;
    function reorder(values) {
      var items = Array.prototype.slice.call(list.children);
      var flip = window.Flip.getState(items);
      items.sort(function (a, b) { return values[b.getAttribute("data-key")] - values[a.getAttribute("data-key")]; })
           .forEach(function (li) { list.appendChild(li); });
      scenes.rank = window.Flip.from(flip, { duration: reduce ? 0 : 0.6, ease: "power2.inOut", stagger: 0.03 });
    }
    function show(season) {
      var values = states[season];
      if (change) change.progress(1).kill(); // finish the last change before starting the next
      if (scenes.rank) scenes.rank.progress(1);
      change = gsap.timeline();
      Array.prototype.forEach.call(list.children, function (li) {
        var v = values[li.getAttribute("data-key")];
        li.querySelector(".lab-rank-value").textContent = v.toFixed(1) + "%";
        change.to(li.querySelector("i"), { width: (v / peak * 100).toFixed(1) + "%", duration: reduce ? 0 : 0.5,
          ease: "power2.inOut", overwrite: "auto" }, 0);
      });
      change.call(reorder, [values]);
      var leader = Object.keys(values).sort(function (a, b) { return values[b] - values[a]; })[0];
      if (status) status.textContent = season + ": Exporter " + leader + " leads with " + values[leader].toFixed(1) + "%.";
      buttons.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-season") === season)); });
    }
    buttons.forEach(function (b) {
      b.addEventListener("click", function () { if (b.getAttribute("aria-pressed") !== "true") show(b.getAttribute("data-season")); });
    });
    rank.querySelector(".lab-toggle").hidden = false;
    scenes.showSeason = show;
  }
})();
