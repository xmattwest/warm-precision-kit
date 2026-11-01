# Warm Precision

**Make the important obvious, the complex understandable, and the next step clear.**

A portable style kit for research, documents, diagrams, presentations and software. It ships with one visual profile, also called Warm Precision. Version 1.0.

## Start here

1. Pick the document from the reader's goal in `DOCUMENTS.md` and start from its shape.
2. Apply the profile in `profiles/warm-precision/` through the medium's adapter in `adapters/`.
3. Show numbers with `adapters/data.md`; write copy with `VOICE.md`.
4. For consequential work, fill in `templates/ARTIFACT_BRIEF.md` first and `templates/REVIEW_RECEIPT.md` last.

Build the browsable handbook from this checkout:

```sh
python3 design-system/scripts/build.py --embed-fonts
python3 -m http.server 8080 --bind 127.0.0.1 --directory handbook
```

Open **http://127.0.0.1:8080/**. With `--embed-fonts` the output carries the real fonts and works offline; without it, pages request Google Fonts and fall back to system stacks.

While editing, `python3 design-system/scripts/build.py --embed-fonts --watch` rebuilds on every save. Reload the browser to see the change.

## Authority and ownership

- `PHILOSOPHY.md` owns the principles.
- `profiles/warm-precision/tokens.json` owns exact colors, type, spacing, media sizes and number formats. Its `contract` owns contrast minimums and accent limits.
- `VOICE.md` owns how copy sounds. `DOCUMENTS.md` owns which document to make and its default shape.
- `../BRAND_KIT.md` explains the identity. Its marked tables are generated from the profile.
- `adapters/` own medium-specific expression. `adapters/data.md` owns figures, tables and number formatting.
- Project context owns audience, facts, terminology and evidence. An artifact brief owns one artifact's purpose and composition.

Precedence: evidence fidelity, accessibility and required publishing conventions; explicit artifact constraints; the profile and medium adapter; philosophy defaults; vendor defaults. An exception states its reason and scope.

## Portable use

Copy this whole `design-system/` directory into another project, or keep one shared checkout and reference it by path. `scripts/build.py` resolves its own location either way. Add the scoped pointer from `templates/AGENT_INSTRUCTIONS.md` to that project's agent instructions.

For figures in another project, import `scripts/figures.py` (standard library) or use the generated `warm-precision.mplstyle` with matplotlib.

## Reusable vocabulary

**Brief → structure → compose → distill → review → publish.**

- Critique: assess purpose, hierarchy, coherence and fit.
- Audit: check correctness, accessibility, states and output behavior.
- Distill: remove redundancy while preserving meaning.
- Adapt: recompose for a destination.
- Polish: reconcile the last details with the system.

Use Impeccable for frontend craft and Diagram Design for publication diagrams where available. Neither is required.

## Contents

- `PHILOSOPHY.md`: principles and decision rules.
- `VOICE.md`: rules, registers, before-and-after edits and a pre-publish check.
- `DOCUMENTS.md`: ten document types, chosen by goal, each with a default shape.
- `profiles/warm-precision/`: tokens, integration notes, and how to make your own profile.
- `adapters/`: web, documents, slides, diagrams, data, motion, and scenes (GSAP in pages, HyperFrames for video).
- `patterns/`: cross-medium information structures.
- `templates/`: project context, artifact brief, scene brief, agent pointer, review receipt.
- `scripts/build.py`: handbook generator and validation. `scripts/figures.py`: number formatting, SVG charts and the matplotlib style. `scripts/specimens.py`: the designed sections of handbook pages. `scripts/examples.py`: the annotated example pages. `scripts/scenes.py`: check, snapshot and render scenes with HyperFrames.
- `assets/`: handbook layout, the example-page styles and the motion reference implementation.
- `scenes/`: one folder per HyperFrames composition, the browser player, and the in-page scene lab.
- `vendor/gsap/`: GSAP 3.15 core and plugins, unmodified.
- `SOURCES.md`: influences and adaptation decisions.
