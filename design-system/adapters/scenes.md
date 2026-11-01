# Scenes and video

A scene is motion that tells something: an action, a sequence, a short film. Write it as one HTML file with a paused GSAP timeline. The same file plays in a page and renders to MP4 with HyperFrames, frame for frame.

Page motion (hover, draw-on, tick-to-value, scrub) stays in [motion.md](motion.md). Scenes are for everything sequenced beyond those three moves.

## Pick the tool

| You want | Use | Why |
| --- | --- | --- |
| Hover, focus, pressed, disclosure | CSS transitions | State changes at 180 ms, nothing to load |
| A chart that draws once in view | `motion.js` and the three moves | Vanilla, under 100 lines |
| Motion tied to scroll, a click or a slider in a page | GSAP | ScrollTrigger, Flip, DrawSVG, MorphSVG, MotionPath |
| A clip to post, a launch film, an explainer | HyperFrames with GSAP | Renders HTML to MP4 the same way every time |
| Depth: a camera move through a 3D space | Three.js inside a HyperFrames scene | Only when depth carries meaning |

## From a description to a scene

1. Describe it in a [scene brief](../templates/SCENE_BRIEF.md): format, length, the beats in order, the last frame, the data source. A paragraph is enough.
2. Turn the beats into a timing table: second, what changes, how it moves.
3. Build the last frame first. It has to read on its own, as a still or a thumbnail.
4. Build the timeline from the start toward that frame with `fromTo`, so any moment can be shown by seeking.
5. Review by stills. `scenes.py snapshot` writes a contact sheet of exact frames. Fix what the stills show, then render.

## The scene contract

- One paused timeline per composition, registered as `window.__timelines["<id>"]`. The root's `data-duration` is the length.
- Everything visible is a function of timeline time. No `Date`, unseeded random numbers, timers, network requests, `repeat: -1` or `play()` inside a scene.
- Use `fromTo`, never `from`. Seeking backward must land on the same frame every time.
- One data block drives every mark and number. Values come from the source, and a source line is on screen.
- Fonts and scripts load from the scene's own `assets/` folder, which the build writes. Nothing loads from the network.
- The last frame is complete and holds for at least two seconds (`sceneEndHoldMs` in the profile).
- In a page, a scene opens on its last frame and plays when asked. Reduced motion never autoplays.

## What makes it ours

- Arrival order is reading order: context, axis, reference line, data, the one annotation, then stillness.
- Titles land and stay still. Nothing floats, breathes, pulses or slowly creeps in scale. Data never loops.
- One accent per scene. Golden Orange is a fill; accent text is Copper Deep.
- Every transition has a cause on screen. In the 10:30 sample the clock shrinks into the chart's first axis label.
- No launch theatre: no glowing dots, stamped verdicts, confetti or spinning logos.

## Timing

| Move | Duration | Ease |
| --- | --- | --- |
| An element arrives | 0.3–0.6 s | `expo.out` or `power4.out` |
| A camera or colour move | 0.6–1.0 s | `power2.inOut` |
| An element leaves | 40–50% of its entrance | `power3.in` |
| Words in a title | 60–120 ms apart | |
| Bars or list items | 40–80 ms apart | |
| A count to a number | 1.2–1.6 s, landing exactly | `power3.out` |
| Holding a line to be read | 0.5 s plus 0.3 s a word | |
| The last frame | 2 s or more | |

These start from HyperFrames' defaults, which were measured from finished films, and keep the kit's rule that numbers land exactly.

## Formats

| Use | Size | Note |
| --- | --- | --- |
| Landscape video, talks | 1920 × 1080 | The `video` scale in tokens.json |
| Square social | 1080 × 1080 | Same type scale |
| Portrait feed | 1080 × 1350 | Same type scale |
| Vertical | 1080 × 1920 | Keep text in the middle 80% |

Scenes run at 30 fps. Type sizes: title 64 px, body 36, labels 30, kicker and caption 28, a single big number 144. Nothing that must be read goes below 28 px, which is about what a phone can read in a 1080 px frame.

## Commands

```
python3 design-system/scripts/build.py --embed-fonts           # writes handbook/scenes/<name>/
python3 design-system/scripts/scenes.py check                   # lint, runtime and layout checks
python3 design-system/scripts/scenes.py snapshot ten-thirty     # contact sheet of exact frames
python3 design-system/scripts/scenes.py render ten-thirty       # MP4 in handbook/scenes/renders/
```

Rendering needs Node 22 or newer and FFmpeg. `scenes.py` runs a pinned HyperFrames release through `npx`, so nothing is installed into the kit.

## Adding a scene

Create `design-system/scenes/<name>/index.html`. Link `assets/fonts.css`, `assets/scene.css`, `assets/gsap.min.js` with any plugins it uses, and `assets/player.js` last. The build copies each scene into `handbook/scenes/<name>/` with exactly the assets it references, so every scene folder is a complete HyperFrames project. The in-page specimens live in `scenes/lab.js` and `scenes/lab.css` and load only on this page.

## Licenses

GSAP 3.15 is vendored in `vendor/gsap/` under Webflow's standard no-charge license, which allows commercial use. HyperFrames is Apache 2.0 and runs through `npx`; it is not vendored.
