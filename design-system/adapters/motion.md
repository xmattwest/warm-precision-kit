# Motion and animation

## First principles

Static carries meaning; motion carries attention. The complete static composition must always be legible on its own. Motion shows how it was built; it never adds information the static lacks. This is a comprehension rule, not a performance preference.

Every animated value binds to source data, never to a hand-typed number. A chart draws the same evidence object it would print; a ticking figure lands on the exact registered decimal; a scrub lands only on registered states. Motion that invents intermediate values presents them as decoration, never as evidence.

Motion is progressive enhancement. The page ships complete and still; script adds movement only when the reader's settings allow it. Reduced motion receives the finished composition instantly, with nothing missing and nothing left half-drawn.

## What makes it ours

A Warm Precision animation builds the figure in reading order and then stops: axis, estimates, intervals, verdict, then stillness. The pleasure is in the order of arrival and in numbers landing exactly.

Two experiments settled this. An opening 600 ms stillness beat tied on delight and lost on clarity (4/3 against 4/4 for immediate construction). The beat read as dead air, not anticipation. It is removed from the framework; construction begins on view. A stamped verdict ceremony scored 2/1 and is now forbidden: ceremony on a verdict reads as hype, and the verdict must stand static from the first paint. Delight lives in arrival order and exact landings, with the numbers ticking last. Never in beats or stamps.

Data never loops, shimmers or pulses. Decorative line work may be sketched by hand; data marks are always drawn from the data.

## The timing language

One vocabulary, everywhere. The profile owns duration and easing: a 180 ms base with ease-out for state (hover, focus, pressed, disclosure). Explanatory sequences may run longer: draw-on up to 900 ms, full figure builds under 3 seconds, with a 60–70 ms stagger between steps. A sequence reads as one hand drawing, not a cascade of widgets.

Use three moves and no others without a doctrine line justifying the fourth:

- **Draw-on.** Strokes arrive via `pathLength` and dash offset; axis before marks, estimates before intervals, margins last as the verdict. The reading order of the static becomes the arrival order of the motion.
- **Tick-to-value.** Figures count from zero to the exact registered decimal with tabular numerals, ease-out, and a guaranteed exact landing. Never ease through precision the source does not claim.
- **Scrub-between-states.** A control interpolates geometry between two registered states and lands on one; readouts always show exact registered values, never the in-between. If the in-between cannot be shown honestly, animate the transition and swap the readout at the start.

## Techniques

CSS transitions own state changes. SVG draw-on uses `pathLength="1"` with `stroke-dasharray: 1` and offset from 1 to 0. No path measuring, no JS geometry. Count-ups run on `requestAnimationFrame` with `IntersectionObserver` firing once; format every frame, land exactly. Scroll-linked progress uses view timelines as enhancement only. Keep client script vanilla and tiny; the reference implementation is `assets/motion.js` with its companion `assets/motion.css`, both under a hundred lines each.

Gate everything on a motion class the script adds only when reduced motion is off. No motion class, no movement, no hidden content: selectors that hide pre-animation states must live under that gate, so a blocked or failed script still shows the finished page.

## Maintaining the style

Anything sequenced beyond these three moves (a scroll story, a re-rank, a described action, a video) is a scene. Scenes follow [scenes.md](scenes.md) and use GSAP and HyperFrames; this page's moves stay vanilla.

A new motion is a proposal, not a commit. It ships first as a specimen on this page's handbook edition (built by `scripts/specimens.py`), scored for clarity and restraint. It earns a line in this doctrine describing when it is the right move. Specimens stay on the page as living regression tests: if a rebuild changes them, the style changed. `scripts/figures.py` emits the draw-on and rise attributes, so charts built with it animate the same way.

Review every motion against the receipt: static-complete without script, exact landings, registered states only, reduced-motion instant, tabular numerals throughout, and no layout shift after arrival.
