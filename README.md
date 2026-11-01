# Warm Precision

A style kit for research, documents, charts and software, written so both people and coding agents can follow it. It gives you one look, one voice and one way to show numbers: design tokens, a voice guide, document shapes, a data standard with SVG and matplotlib helpers, and guidance for web, slides, diagrams, motion and video.

```sh
python3 design-system/scripts/build.py --embed-fonts
```

That builds the browsable handbook into `handbook/`. Open `handbook/index.html`, or serve it with `python3 -m http.server 8080 --directory handbook`. Python 3.10 or newer, standard library only. `--embed-fonts` downloads Inter and Newsreader from Google Fonts once and embeds them, so the handbook then works offline.

## Use it in your project

Copy `design-system/` (and `BRAND_KIT.md` if you want the brand page) into your project. Then paste the paragraph from [`design-system/templates/AGENT_INSTRUCTIONS.md`](design-system/templates/AGENT_INSTRUCTIONS.md) into your `AGENTS.md`, `CLAUDE.md` or equivalent, so your agent reads the principles, tokens and the right adapter before it designs or writes anything.

- **Colors and type** come from [`profiles/warm-precision/tokens.json`](design-system/profiles/warm-precision/tokens.json). The build turns them into CSS custom properties (`tokens.css`), a matplotlib style (`warm-precision.mplstyle`) and a contrast receipt.
- **Charts:** `design-system/scripts/figures.py` draws accessible SVG bar, line, interval, scatter, strip, histogram, heatmap, small-multiple, band, stacked and waterfall charts, plus KPI tiles and tables, from the same tokens.
- **Copy:** [`VOICE.md`](design-system/VOICE.md) has ten rules, three registers and a pre-publish check.
- **Documents:** [`DOCUMENTS.md`](design-system/DOCUMENTS.md) maps the reader's goal to one of ten document types and their default shapes.

To make it yours, copy `profiles/warm-precision/` and change the tokens. The build fails any palette whose text or essential marks miss their contrast minimums. See [the profile notes](design-system/profiles/warm-precision/INTEGRATION.md#making-your-own-profile).

## What it does not do

It ships no component library or framework bindings; it gives you tokens and rules for building your own. Rendering scenes to MP4 is optional and needs Node 22+, FFmpeg and a pinned [HyperFrames](https://github.com/heygen-com/hyperframes) release run through `npx`.

## Development

```sh
python3 design-system/scripts/build.py --embed-fonts --watch   # rebuild on every save
python3 design-system/scripts/build.py --check                 # validate tokens, outputs and links
python3 design-system/scripts/test_build.py
```

## Licenses

The kit is under the [MIT License](LICENSE). Inter and Newsreader are under the SIL Open Font License. GSAP 3.15 is vendored unmodified in `design-system/vendor/gsap/` under Webflow's [standard no-charge license](https://gsap.com/standard-license), which has its own terms.
