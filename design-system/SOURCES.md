# Influences and adaptation decisions

Reviewed November 2026. These are influences, not runtime dependencies. Repository defaults may change; record an installed version when integrating a vendor tool.

## The Warm Precision profile

Newsreader for one display line, Inter for headings and prose, flat surfaces, scarce accents and a warm canvas. Display lines use Newsreader's real 600 weight rather than a synthesized bold, so they render the same in every browser and export. Distribution and margins are compositional defaults; typography and strokes are destination-specific; contrast rules are measured against the actual background. Principles, profile and project context are kept separate so a project can swap the profile without touching the rest.

## Impeccable

- https://github.com/pbakaus/impeccable
- https://github.com/pbakaus/impeccable/blob/main/skill/SKILL.src.md
- https://github.com/pbakaus/impeccable/blob/main/skill/reference/init.md
- https://github.com/pbakaus/impeccable/blob/main/skill/reference/document.md
- https://github.com/pbakaus/impeccable/blob/main/skill/reference/operate.md
- https://github.com/pbakaus/impeccable/blob/main/skill/reference/critique.md

Adopt durable product context separate from visual direction, surface-specific modes, pinned-brief precedence, appropriate familiarity in tools, and rendered review. Use critique/audit/distill/adapt/polish as a reusable working vocabulary. Warm Precision adds Explain for analytical artifacts; this is a local extension, not an Impeccable command or mode claim.

## Diagram Design

- https://github.com/cathrynlavery/diagram-design
- https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/SKILL.md
- https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/references/style-guide.md
- https://github.com/cathrynlavery/diagram-design/blob/main/skills/diagram-design/references/profiles.md

Adopt semantic selection, deliberate subtraction, constrained focal emphasis, structural grid discipline, portable profile selection, accessible SVG, and fidelity ledgers. Adapt serif typography, small label defaults, hairline geometry, and tinted fills to the profile and each destination. Split accent fill/text/stroke roles because the profile's orange does not meet the vendor's all-role contrast requirement on Ivory.

## Contrast and accessibility

- https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html

Measure WCAG 2.x relative luminance against the actual background; composite translucent colors first. Normal text needs at least 4.5:1, large text 3:1, and essential marks 3:1. Supporting labels/shape cues also preserve meaning without color. Automated results do not certify the whole artifact's accessibility.

## Fonts

Fonts are distributed under the SIL Open Font License:

- [Inter license](https://github.com/rsms/inter/blob/master/LICENSE.txt)
- [Newsreader license](https://github.com/google/fonts/blob/main/ofl/newsreader/OFL.txt)

## Motion

- GSAP 3.15, vendored unmodified in `vendor/gsap/` under Webflow's [standard no-charge license](https://gsap.com/standard-license).
- [HyperFrames](https://github.com/heygen-com/hyperframes), Apache 2.0, run through `npx` for rendering scenes; not vendored.
