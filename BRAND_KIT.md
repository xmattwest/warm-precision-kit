# Brand kit

**The Warm Precision profile: a warm Ivory canvas, one serif display line, Inter for everything else, slate structure and one orange focus.**

This is the kit's default profile: make the important obvious, the complex understandable, and the next step clear. Use it as it ships, or copy it and change the tokens to make your own identity (see [Integration](design-system/profiles/warm-precision/INTEGRATION.md)).

The philosophy lives in [design-system/PHILOSOPHY.md](design-system/PHILOSOPHY.md), the voice in [VOICE.md](design-system/VOICE.md), document shapes in [DOCUMENTS.md](design-system/DOCUMENTS.md) and the data standard in [adapters/data.md](design-system/adapters/data.md). Exact values live in [tokens.json](design-system/profiles/warm-precision/tokens.json). The marked reference below is generated from those tokens; rebuild it with `python3 design-system/scripts/build.py --embed-fonts --write-brand`.

## 1. Palette and typography

<!-- profile-tokens:start -->
| Color | Exact value | Role |
| --- | --- | --- |
| Ivory | `#FFFFF0` | Canvas and open space |
| Onyx | `#0F0F0F` | Primary text |
| Blue Slate | `#2C3E50` | Structure, links, buttons, primary data |
| Golden Orange | `#F39C12` | The one focus; fill only, with an outline |
| Sage Green | `#87A96B` | Secondary series or positive cue; fill only |
| Slate Deep | `#1E3447` | Secondary text and kickers |
| Copper Deep | `#96590A` | Text-safe accent |
| Sage Deep | `#5F7F4A` | Text-safe positive cue |
| Parchment | `#F5EEDC` | Detail wells, never a second canvas |
| Slate Mist | `#808B90` | Context series and reference lines; marks only |

| Typography | Family | Weight | Tracking |
| --- | --- | --- | --- |
| Display | Newsreader | 600 | −0.05 em |
| Wordmark | Newsreader | 600 | −0.06 em |
| Heading | Inter | 600 | −0.02 em |
| Body | Inter | 400 | 0 em |
| Kicker | Inter | 600 | 0.12 em |
| Code | ui-monospace | 400 | 0 em |

| Medium | Body / primary labels | Supporting text |
| --- | --- | --- |
| Web | 18 px | 14 px |
| Document | 11 pt | 9 pt |
| Slide | 32 px | 24 px |
| Card | 30 px | 28 px |
| Video | 36 px | 28 px |
| Diagram | 16 px | 14 px |
| Chart | 16 px | 14 px |

Container radii: 8–12 px. Structural and focus strokes: 2/3 px. Decorative rules: 1 px at 22% Blue Slate; tracks at 12%.
<!-- profile-tokens:end -->

### Color roles and emphasis

Ivory is the canvas. Onyx is primary text. Slate Deep is secondary text and kickers. Blue Slate carries structure, links, focus rings, buttons and the primary data series. Golden Orange marks the one thing a composition is about. Slate Mist is the context color for comparison series, prior periods and reference lines.

Use the 60–30–10 rule as a compositional guide: a mostly open canvas, a clear dark hierarchy, and no more than 10% accent area. Dense tools may need more ink; that is fine. Use spacing, size and weight before color.

Golden Orange and Sage Green stay fill-only on Ivory. When accent-colored text is needed, use Copper Deep or Sage Deep, which clear 4.5:1. Parchment is a detail well, never a second canvas. Blue Slate at 22% draws decorative rules; at 12% it fills tracks and empty cells. Neither carries meaning on its own. No gradients, no decorative shadows. A publishing requirement can justify a scoped exception; record its purpose and destination.

### Background-aware contrast

Measure every pairing against its actual background. Normal text needs 4.5:1; large text and essential marks need 3:1. Onyx, Slate Deep and Blue Slate clear normal text on Ivory, and Ivory clears it on Blue Slate. Slate Mist clears 3:1 for marks and large labels only.

Golden Orange and Sage Green do not clear 3:1 on Ivory. A focus mark in orange always has a Blue Slate outline and an Onyx label. A legend cannot repair an invisible mark. Never place Onyx text on Blue Slate, or Blue Slate text on Onyx.

## 2. Type

Three families, each with one job:

- **Newsreader 600, tracked tight (−0.05 em),** for display lines and the wordmark. One display line per view: a product name, a page's single statement, a slide's assertion. A short line that ends with a period, like "Field notes.", is the model.
- **Inter** for everything else. 400 for prose, 600 for headings, labels and emphasis. Kickers are Inter 600, 12 px, uppercase, tracked 0.12 em, in Slate Deep.
- **The platform monospace** only for code, commands and file paths. Never for kickers, prose or decoration.

Numbers in tables, charts and readouts use tabular numerals.

The wordmark pattern is lowercase Newsreader with a closing period ("warm precision.") over a small uppercase Inter tag ("DESIGN HANDBOOK"). Use it for a product's masthead, not for headings.

Ordinary pages use Inter headings: 40 px page title, 24 px section heading, 18 px subsection. Display type is opt-in through `.display-title`, from 48 px on phones to 80 px on wide screens. Each medium has its own ramp (web, document, slide, card); verify at the final size and cut content before shrinking type.

## 3. Layout and form

Generous margins and a consistent grid. Web reading pages are 1040 px wide at most, tools 1200 px, with at least 24 px gutters on phones. Necessary density in tables and tools is fine.

One argument or task per view. Split an overloaded composition into overview and detail. Group by proximity before adding a container. Containers and buttons use 8 px radii; large panels may use 12 px. Buttons are Blue Slate with Ivory text, or outlined in Blue Slate. Decorative rules are 1 px at 22%; structural strokes are 2 px; focus rings are 3 px.

## 4. Diagrams and data

Choose the visual by meaning: quantities in charts, relationships in diagrams, exact values in tables. Every figure follows the anatomy in [adapters/data.md](design-system/adapters/data.md): finding as the title, measure and sample as the subtitle, the plot, then one source line.

Blue Slate draws primary marks and diagram routes. Orange marks one focus, with an outline. Slate Mist carries context. Label data directly. No 3D, no gradients, no chart furniture, no ASCII charts.

State units, denominators, samples, interval levels and exclusions. Preserve counterexamples and uncertainty. When simplifying a source, report what was merged, omitted or moved.

## 5. Voice

Say what it is, show the number, stop. The full guide, with registers and before-and-after edits, is [VOICE.md](design-system/VOICE.md). The short version:

- First line says what it is, in words an outsider knows.
- No gates, phases or codenames in public copy.
- Numbers carry the confidence; adjectives do not.
- One point where you drafted three. Vary sentence length.
- No em dashes. No launch theatre, slogans or emojis.

## 6. Production review

- Purpose and primary takeaway or task are clear in five seconds.
- The document type and shape match the reader's goal ([DOCUMENTS.md](design-system/DOCUMENTS.md)).
- Values come from the token source.
- One focus per figure; accent meaning is consistent.
- Every text, control and data-mark pairing clears its contrast threshold on its real background.
- Type, spacing and units suit the final size; nothing overlaps or clips.
- Copy passes the [VOICE.md](design-system/VOICE.md) checks.
- Figures trace to source files; exclusions are visible.
- Interfaces have relevant states, keyboard support, visible focus and useful labels.

Use [REVIEW_RECEIPT.md](design-system/templates/REVIEW_RECEIPT.md) for consequential outputs. Look at the rendered result; a passing check does not replace judgment.
