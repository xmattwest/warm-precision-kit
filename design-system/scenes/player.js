/* Warm Precision scene player.
   In a browser it plays a HyperFrames composition by seeking its paused GSAP
   timeline frame by frame, the same way the renderer does. Under the HyperFrames
   runtime it does nothing. The composition first lands on its finished frame.
   Opened on its own, it then plays from the start unless reduced motion is on;
   inside an iframe it waits for Play. ?autoplay=1 forces playback, ?autoplay=0
   suppresses it, and ?t=2.5 shows one exact frame with no controls (for review). */
(function () {
  "use strict";
  function underRuntime() {
    return !!(window.__hf || window.__player || window.__hyperframes || window.__HF_VIRTUAL_TIME__);
  }
  function start() {
    if (underRuntime()) return;
    var root = document.querySelector("[data-composition-id]");
    var timelines = window.__timelines || {};
    var tl = root && timelines[root.getAttribute("data-composition-id")];
    if (!tl) return;
    var width = Number(root.getAttribute("data-width")), height = Number(root.getAttribute("data-height"));
    var duration = Number(root.getAttribute("data-duration")) || tl.duration();
    var params = new URLSearchParams(window.location.search);
    var still = params.has("t");
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var barHeight = still ? 0 : 52;
    var css = document.createElement("style");
    css.textContent = "html,body{height:100%;overflow:hidden}body{position:relative}" +
      "[data-composition-id]{position:absolute!important;transform-origin:0 0}" +
      ".wpp-bar{position:fixed;left:0;right:0;bottom:0;height:52px;display:flex;align-items:center;gap:16px;padding:0 16px;" +
      "background:var(--canvas,#FFFFF0);border-top:1px solid rgb(44 62 80 / .22);font:400 14px/1 var(--scene-body,sans-serif);color:var(--text-primary,#0F0F0F)}" +
      ".wpp-bar button{min-width:84px;min-height:36px;border:1px solid var(--structure,#2C3E50);border-radius:8px;background:var(--structure,#2C3E50);" +
      "color:var(--on-structure,#FFFFF0);font:600 14px/1 var(--scene-body,sans-serif);cursor:pointer}" +
      ".wpp-bar button:focus-visible,.wpp-bar input:focus-visible{outline:3px solid var(--focus,#2C3E50);outline-offset:3px}" +
      ".wpp-bar input{flex:1;min-width:0;accent-color:var(--structure,#2C3E50)}" +
      ".wpp-bar output{flex:none;text-align:right;font-variant-numeric:tabular-nums;color:var(--text-secondary,#1E3447)}" +
      "@media (max-width:420px){.wpp-bar{gap:10px;padding:0 10px}.wpp-bar button{min-width:72px}}";
    document.head.appendChild(css);

    function fit() {
      var scale = Math.min(window.innerWidth / width, (window.innerHeight - barHeight) / height);
      var left = (window.innerWidth - width * scale) / 2, top = (window.innerHeight - barHeight - height * scale) / 2;
      root.style.transform = "translate(" + left + "px," + top + "px) scale(" + scale + ")";
      root.style.left = "0"; root.style.top = "0";
    }
    window.addEventListener("resize", fit);
    fit();

    if (still) { tl.seek(Math.max(0, Math.min(Number(params.get("t")) || 0, duration)), false); return; }

    var bar = document.createElement("div");
    bar.className = "wpp-bar";
    bar.innerHTML = '<button type="button">Play</button><input type="range" min="0" step="any" aria-label="Scene time"><output aria-live="off"></output>';
    document.body.appendChild(bar);
    var button = bar.querySelector("button"), range = bar.querySelector("input"), readout = bar.querySelector("output");
    range.max = String(duration);
    var playing = false, origin = null, from = 0, now = duration;
    var ticker = window.gsap.ticker;

    function show(t) {
      now = Math.max(0, Math.min(t, duration));
      tl.seek(now, false); // false: run onUpdate, so text driven by the timeline lands too
      range.value = String(now);
      readout.textContent = now.toFixed(1) + " / " + duration.toFixed(1) + " s";
      range.setAttribute("aria-valuetext", readout.textContent);
    }
    function label() { button.textContent = playing ? "Pause" : now >= duration ? "Replay" : "Play"; }
    function stop() { playing = false; ticker.remove(frame); label(); }
    function frame(time) { // GSAP's ticker time, in seconds
      if (origin === null) origin = time;
      show(from + (time - origin));
      if (now >= duration) stop();
    }
    function play() {
      from = now >= duration ? 0 : now;
      origin = null; playing = true; label();
      ticker.add(frame);
    }
    button.addEventListener("click", function () {
      if (playing) { stop(); } else { play(); }
    });
    range.addEventListener("input", function () { stop(); show(Number(range.value)); });

    show(duration); // static-complete: open on the finished frame
    label();
    var top = window.self === window.top;
    if (params.get("autoplay") === "1" || (top && !reduce && params.get("autoplay") !== "0")) { show(0); play(); }
  }
  if (document.readyState === "complete") start();
  else window.addEventListener("load", start);
})();
