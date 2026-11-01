# Data and figures

**One question per figure, the finding in the title, the source underneath.**

This standard covers charts, tables, figure cards and the numbers inside prose. Exact colors, sizes and number formats come from the profile's `tokens.json`. `scripts/figures.py` applies them to SVG and generates a matplotlib style, so a handbook specimen, a web page and a paper figure share one source.

## Start with the question

Write the question the figure answers before choosing a chart. Then state the estimand: the quantity, unit, direction, denominator, sample and uncertainty. A plotted effect must not be confused with the raw outcome or with a different estimand.

| Question | Use | Notes |
| --- | --- | --- |
| Which is biggest? | Horizontal bars, sorted | Zero baseline. Labels on the left, values at the bar end. |
| How did it change? | Line | Label each line at its end. One focus line; the rest are context. |
| How is it spread? | Strip, dot or histogram | Show individual points when n is small; a histogram when n is large. |
| Do two things move together? | Scatter | Label the points that matter, not all of them. Hundreds of points go dense and low-opacity. |
| How big is the effect, and how sure? | Interval plot | Dashed reference line at no effect. Name the interval level. |
| What share of the whole? | Stacked bar, 100% or absolute | Pie only for two or three parts. |
| How did a total build up or draw down? | Waterfall | Sage adds, copper subtracts, slate marks the totals. |
| How does one value compare across a grid? | Heatmap or matrix | Sequential ramp for a magnitude, diverging for a signed value. The cell number stays readable. |
| Is this inside its usual range? | Range band or percentile fan | A median line inside 50% and 90% bands. |
| How do many series compare? | Small multiples | One shared scale; never per-panel scales. |
| What are the headline numbers? | KPI tiles with sparklines | A few figures, each with a change and a direction. |
| What is the exact value? | Table | Readers looking up values want a table, not a chart. |
| When does it happen? | Calendar or weekday/hour mosaic | Size encodes count. |

A list belongs in bullets. A relationship belongs in a diagram ([diagrams.md](diagrams.md)). ASCII charts are never acceptable in a published page.

## Figure anatomy

Every figure has the same four parts, top to bottom:

1. **Title:** the finding, as a statement. "Corn exports are running 18% ahead of last year", not "Corn exports".
2. **Subtitle:** measure, unit, sample and period. "Cumulative export sales, million t, marketing year to date".
3. **Plot:** data marks, axis ticks and direct labels only.
4. **Source line:** source, n and method in one line. "Source: USDA FAS weekly export sales, through 23 Oct 2026."

Title, subtitle and source line are page text, not text drawn inside the image. This keeps them selectable and searchable, and it means a long subtitle wraps instead of colliding with an axis title. When a figure must travel as an image (a paper, a card), keep the same order and give each part its own row with fixed spacing from the chart ramp.

Optional fifth part: a one-line note under the plot for an exclusion, a break in series or an annotation key.

## Numbers

- **Units always.** In the subtitle, the column header or directly after the number. Never make the reader guess.
- **Separators.** Thousands with a comma (`12,400`), decimal with a period.
- **Precision.** Fixed decimals within a column or series. Match precision to what the source claims; do not add decimals for effect.
- **Percent and points.** A change in a rate is in percentage points (`+2.1 pp`), not percent.
- **Signs.** True minus (`−3.2`), not a hyphen. Show `+` only for changes.
- **Ranges and intervals.** En dash without spaces: `4.1–5.3`. Name the level: "95% interval".
- **Dates.** ISO in data files (`2026-10-23`). On the page: `23 Oct 2026` for a day, `Oct 2026` for a month.
- **Missing.** `n/a` in tables, a gap in lines. Never zero.
- **Domain units** as the field writes them: `¢/bu`, `$/t`, `MMT`, `bp`.

`figures.fmt()` implements these rules.

## Tables

- Numbers right-aligned with tabular numerals. Text left-aligned.
- Units in the header: "Exports (million t)".
- Horizontal rules only: a structural rule under the header, decorative rules between rows.
- At most one highlighted row, marked by weight and a label, not color alone.
- A wide table scrolls inside its own container. The page never scrolls sideways.
- Over about 15 rows, consider a chart with the table in a disclosure.

## Color and emphasis

- **One focus.** Blue Slate is the primary series. Golden Orange marks the single item the title is about, always with a Blue Slate outline because orange alone is under 3:1 on Ivory.
- **Context.** Slate Mist (`#808B90`, 3.5:1 on Ivory) carries comparison series, prior years and reference lines. It is the gray of this system.
- **Second series.** Sage Green with a dark outline or a distinct line pattern, only when two series are equally important.
- **More than three series.** Use small multiples or line patterns. Do not add colors.
- **Tracks and empty cells.** Blue Slate at 12% (`--track`), behind signal bars and meters. Decorative only.
- Every colored mark also has a label, a position or a shape that carries the same meaning.

## Sizes

| Medium | Labels | Captions | Notes |
| --- | --- | --- | --- |
| Web and document | 16 px | 14 px | Figure title 20 px, subtitle 16 px |
| Slide (1600 × 900) | 32 px | 24 px | Rebuild the figure; never enlarge a screenshot |
| Card (1200 × 1200) | 34 px | 28 px | Title 84 px, values 40 px, 72 px margins |
| Paper (matplotlib) | 10 pt | 10 pt | From the document ramp |

The card ramp is compressed on purpose: the largest and smallest sizes are closer together so the card reads at phone width. A wide web chart scrolls locally on phones rather than shrinking below these sizes.

## Tools

SVG is the default for anything shown on a page. It keeps text selectable, scales cleanly, takes the profile's fonts and can animate under the [motion](motion.md) rules.

| Tool | Use it for | Trade-off |
| --- | --- | --- |
| `figures.py` SVG helpers | Web pages, handbook specimens, cards | Standard library, exact tokens; the chart set below |
| Hand-written SVG | One-off explanatory graphics and diagrams | Full control; slower to change |
| matplotlib + `warm-precision.mplstyle` | Analysis and paper figures in Python | Familiar and complete; export SVG with text kept as text |
| Observable Plot or D3 | Interactive charts where interaction carries meaning | Needs a JavaScript runtime; D3 is maximal control at maximal cost |
| Vega-Lite | Declarative charts shared as JSON specs | Themeable through config; heavy runtime for a small page |
| Plotly | Exploratory dashboards | Hard to restrain to this style; avoid for publication |
| Mermaid | Quick internal diagrams | Inconsistent rendering; redraw anything public as SVG |

The handbook build writes `warm-precision.mplstyle` next to `tokens.css`. In Python:

```python
import matplotlib.pyplot as plt
plt.style.use("handbook/warm-precision.mplstyle")
fig, ax = plt.subplots()
ax.plot(x, y)
fig.savefig("figure.svg")  # titles and sources go in the page or caption
```

### The chart set

`figures.py` builds these, each from the profile and each wrapped by `figure()` for the anatomy above. The [Data specimens](../index.html#handbook) on this page render every one.

| Function | Draws |
| --- | --- |
| `bar_chart` | Sorted horizontal bars, one focus |
| `line_chart` | Multi-series lines with end labels |
| `interval_plot` | Estimates with confidence intervals and a reference line |
| `scatter_plot` | Two numeric axes; identity and threshold lines; a dense mode |
| `strip_plot` | Jittered points per group with the median marked |
| `histogram` | One variable's distribution with an optional reference |
| `heatmap` | A matrix, sequential or diverging, with a legend ramp |
| `small_multiples` | A grid of mini line charts on one shared scale |
| `band_chart` | A median line inside percentile or bootstrap bands |
| `stacked_bar` | Part-to-whole bars, absolute or 100% |
| `waterfall` | A running total from signed steps |
| `sparkline` | A tiny inline trend line |
| `kpi_tiles` | Headline numbers with a change and a sparkline |
| `table` | A data table with units, right-aligned figures and one focus row |

matplotlib covers the same families; keep one chart in SVG and its analysis twin in matplotlib reading from the same values, never two hand-built copies.

## Evidence conventions

Keep confidence levels explicit. If thick bars show 90% and thin bars 95%, name both. An equivalence band is a test margin, not a confidence interval. A non-significant test does not show equivalence. Different models, settings or samples can limit comparison even when shown together.

When an estimand conditions on a subset, report what was excluded beside it. Preserve direction and counterexamples. Separate a registered result from an exploratory account.

## Review

- Geometry comes from source values, never from hand-typed labels.
- Title, subtitle, labels and source render from the same data object.
- Nothing overlaps at final size: check axis titles, notes, legends and end labels.
- No highlight or fill hides text: every label clears 4.5:1 on its actual background.
- Tables and wide charts scroll inside their containers on a phone.
- The figure still makes sense in grayscale.
- A data table or text alternative is available without operating the chart.
