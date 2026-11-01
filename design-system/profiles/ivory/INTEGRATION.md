# Ivory profile integration

## Token application

Read `tokens.json`. Resolve role names through `roles` into `colors`; components consume roles, not literal hex values. The builder emits CSS custom properties, resolved JSON, contrast receipts, and Diagram Design guidance from this source. Never edit those outputs to change the profile.

Use Newsreader 600 (optical, tracked −0.05 em) only for display moments and the wordmark, Inter for headings, prose, kickers and data labels, and platform monospace only for code and literal technical strings. Kickers are Inter 600, uppercase, tracked 0.12 em, in Slate Deep. Never set prose or kickers in monospace.

## Impeccable

Place durable audience, product, and evidence facts in the project's context file. Record Ivory as the selected profile in `DESIGN.md`; keep each surface's mode and strategy in its brief. Preserve the palette and typography during refinement. The current skill's pinned-brief rule takes precedence over generic overused-font warnings.

When the detector reports Inter as an overused font, use a narrowly scoped, documented font exception supported by the installed version. Do not disable accessibility or hierarchy checks. Familiar controls and denser layouts are appropriate in Operate mode.

Use critique for human judgment, audit for technical checks, and polish for reconciliation. A detector pass cannot establish that an argument or visual hierarchy is good. Inspect real rendered output.

## Diagram Design

Save a named Ivory profile outside the vendor install. Select it with the project's `.diagram-design` marker (`profile: ivory`). A profile is a complete current-schema style guide; the builder's `diagram-design-overlay.md` is mapping guidance, not a complete profile and must not be copied into the library as one.

Apply these explicit adaptations to the effective guide and relevant type rules:

- `paper` and `paper-2`: canvas. Differentiate groups by spacing and outline rather than invented tints.
- `ink` and `ink-strong`: primary text. `muted`, `soft`, and `link`: Blue Slate.
- `accent`: Golden Orange for fill/emphasis, not unqualified text or essential strokes on Ivory. Split uses by role: focal fill uses orange with Onyx labels and a Blue Slate essential outline; focal text/connector uses Blue Slate unless its actual background clears contrast.
- `accent-tint`: use the existing canvas or flat accent fill; do not import translucent colored fills.
- `rule`: subtle Blue Slate opacity only for decorative rules; `rule-solid`: full-strength structure when essential.
- Title: Newsreader 600 with optical sizing. Node names, prose, callouts, kickers and data labels: Inter, with weight and spacing for emphasis. Technical strings: platform monospace.
- Human-readable labels use the destination's ramp, not the vendor's tiny defaults. Technical strings may use the profile's code stack.
- Prominent containers use the profile's radius; connectors and outlines use the adapter's structural stroke. Preserve orthogonal routing, clear attach points, and label masks.

A straight replacement of `accent` with orange would violate the vendor's multi-role contrast contract. The role split above is essential. Inspect the result and record the selected vendor version and adaptations in the project.

Keep semantic selection, geometry checks, accessible SVG names/descriptions, and overview/detail budgets. Do not relax evidence fidelity to hit a node count. Use maintained text source for frequently changing technical diagrams; generate publication views from it.

## Fonts and exports

HTML can use web fonts or embed the profile's publicly served fonts at build time. The builder records source URLs and SHA-256 digests. Embedded output needs no subsequent network request. Default web output falls back to the named system stacks if unavailable; disclose that fallback in a production receipt.

Wait for fonts before screenshots and PDF capture. Editable SVG retains text and embedded font CSS; imports into design tools may need the fonts installed. Check the actual import instead of assuming browser fidelity implies editor fidelity.

## Making your own profile

Copy `profiles/ivory/` to `profiles/<your-slug>/`, change `name`, `slug`, colors and roles in `tokens.json`, and point `PROFILE_DIR` in `scripts/build.py` at the new folder. `build.py --check` rejects any role pairing that fails the profile's contrast contract, so an unreadable palette fails the build instead of shipping.
