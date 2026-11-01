"""Designed sections for handbook pages: the kit shown, not only described.

Each function returns HTML that the builder places between a page's introduction and its
Markdown reference. Words come from the Markdown sources where possible, so a specimen
cannot drift from the document it illustrates. Values come from tokens.json.
"""

import html
import json
import re

import figures

ILLUSTRATIVE = "Illustrative values for this specimen, not real data."


def esc(value):
    return html.escape(str(value), quote=True)


def anchor(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def section_text(text, heading):
    match = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return match[1] if match else ""


def table_rows(block):
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in block.splitlines() if line.startswith("|")]
    return [r for r in rows if not all(re.fullmatch(r":?-+:?", c) for c in r)]


def inline(value):
    value = esc(value)
    value = re.sub(r"`([^`]+)`", r"<code>\1</code>", value)
    return re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)


def link_item(label, href):
    return f'<li><a href="{esc(href)}">{esc(label)}</a></li>'


def ratio_label(ratio):
    if ratio >= 4.5:
        return "Text"
    if ratio >= 3:
        return "Marks and large text"
    return "Fill only"


# Home ------------------------------------------------------------------------------------

def home(profile, groups, documents_text):
    theme = figures.Theme(profile)
    swatches = "".join(
        f'<li><span class="chip" style="background:{value}"></span><span class="chip-name">{esc(name.replace("-", " ").title())}</span>'
        f'<code>{value}</code></li>' for name, value in profile["colors"].items())
    picker = table_rows(section_text(documents_text, "Choosing"))[1:]
    goal_rows = "".join(
        f'<li><span>{esc(goal)}</span><a href="handbook/DOCUMENTS.html#{anchor(make)}">{esc(make)}</a></li>'
        for goal, make, *_ in picker)
    contents = "".join(
        f'<div><h3>{esc(name)}</h3><ul>{"".join(link_item(label, href) for label, href in rows)}</ul></div>'
        for name, rows in groups.items() if rows)
    return f'''
<section class="wrap home-intro">
  <p class="context">Brand and style kit</p>
  <h1>Warm Precision</h1>
  <p class="lead">One look, one voice and one way to show numbers, for research, documents and tools that have to be right and readable. Agents read the Markdown. People read these pages.</p>
  <p class="actions"><a class="button" href="warm-precision-kit.zip" download>Download the kit</a><a href="handbook/brand-kit.html">See the brand</a></p>
  <p class="small">Python 3.10+ · Standard library only · Works offline</p>
</section>
<section class="wrap section glance" aria-labelledby="glance">
  <h2 id="glance">At a glance</h2>
  <div class="glance-grid">
    <div class="glance-type">
      <p class="specimen-display">Field notes.</p>
      <p class="glance-note">Newsreader {profile["typography"]["display"]["weight"]} for the one display line. Inter for everything else.</p>
      <div class="signal-specimen" aria-hidden="true"><span class="signal-row"><b>Tests passing</b><span>96.4%</span></span><span class="track"><i style="width:96.4%"></i></span>
      <span class="signal-row"><b>Docs covered</b><span>71.8%</span></span><span class="track"><i class="plain" style="width:71.8%"></i></span></div>
    </div>
    <ul class="glance-colors" aria-label="Palette">{swatches}</ul>
  </div>
</section>
<section class="wrap section" aria-labelledby="goal">
  <h2 id="goal">Start from the reader's goal</h2>
  <p class="reading">Pick the document from what the reader needs to do. Each type has a default shape on the <a href="handbook/DOCUMENTS.html">Documents</a> page.</p>
  <ul class="goal-list">{goal_rows}</ul>
</section>
<section class="wrap section" id="handbook" aria-labelledby="handbook-title">
  <h2 id="handbook-title">The handbook</h2>
  <div class="handbook-grid">{contents}</div>
</section>'''


# Brand -----------------------------------------------------------------------------------

def brand(profile):
    roles_by_color = {}
    for role, name in profile["roles"].items():
        roles_by_color.setdefault(name, []).append(role)
    canvas = profile["colors"][profile["roles"]["canvas"]]
    cards = []
    for name, value in profile["colors"].items():
        ratio = figures.contrast(value, canvas)
        use = "Canvas" if name == profile["roles"]["canvas"] else ratio_label(ratio)
        roles = ", ".join(roles_by_color.get(name, [])) or "unassigned"
        cards.append(f'<li><span class="swatch" style="background:{value}"></span><strong>{esc(name.replace("-", " ").title())}</strong>'
                     f'<code>{value}</code><span class="swatch-use">{esc(use)}{"" if use == "Canvas" else f" · {ratio:.1f}:1"}</span>'
                     f'<span class="swatch-roles">{esc(roles)}</span></li>')
    web, t = profile["media"]["web"], profile["typography"]
    ramp = [
        ("Display", f'{t["display"]["family"]} {t["display"]["weight"]} · {web["displayMin"]}–{web["display"]} px', '<p class="specimen-display">Field notes.</p>'),
        ("Page heading", f'{t["heading"]["family"]} {t["heading"]["weight"]} · {web["h1"]} px', '<p class="specimen-h1">Warm Precision</p>'),
        ("Section heading", f'{t["heading"]["family"]} {t["heading"]["weight"]} · {web["h2"]} px', '<p class="specimen-h2">Where the time goes</p>'),
        ("Lede", f'{t["body"]["family"]} {t["body"]["weight"]} · {web["lede"]} px', '<p class="specimen-lede">Your week by project and hour, drawn from the commits you already made.</p>'),
        ("Body", f'{t["body"]["family"]} {t["body"]["weight"]} · {web["body"]} px', '<p class="specimen-body">Every square is a weekday and hour. Size shows how many commits landed there.</p>'),
        ("Kicker", f'{t["kicker"]["family"]} {t["kicker"]["weight"]} · {web["kicker"]} px · uppercase', '<p class="context">Weekly report</p>'),
        ("Caption", f'{t["body"]["family"]} {t["body"]["weight"]} · {web["caption"]} px', '<p class="specimen-caption">Source: local git history, merge commits excluded.</p>'),
        ("Code", f'Platform monospace · {web["caption"]} px', '<p><code>python3 report.py --no-open</code></p>'),
    ]
    rows = "".join(f'<div class="ramp-row"><p class="ramp-label">{esc(role)}<span>{esc(spec)}</span></p>{sample}</div>' for role, spec, sample in ramp)
    return f'''
<section class="specimen" aria-labelledby="sp-palette">
  <h2 id="sp-palette">Palette</h2>
  <p class="specimen-intro">Contrast is measured on Ivory. “Fill only” colors need an outline and a dark label.</p>
  <ul class="swatch-grid">{"".join(cards)}</ul>
</section>
<section class="specimen" aria-labelledby="sp-type">
  <h2 id="sp-type">Type</h2>
  <div class="ramp">{rows}</div>
</section>
<section class="specimen" aria-labelledby="sp-marks">
  <h2 id="sp-marks">Marks and controls</h2>
  <div class="marks-grid">
    <div><p class="ramp-label">Wordmark</p><p class="wordmark-sample">field notes.<span>Weekly report</span></p><p class="wordmark-sample">warm precision.<span>Design handbook</span></p></div>
    <div><p class="ramp-label">Controls</p><p class="control-row"><a class="button" href="#sp-marks">Download the kit</a><a class="button secondary" href="#sp-marks">Export report</a></p><p><a href="#sp-marks">Read the preprint</a></p></div>
    <div><p class="ramp-label">Signal bars</p><div class="signal-specimen"><span class="signal-row"><b>Tests passing</b><span>96.4% · 1,212 / 1,257</span></span><span class="track"><i style="width:96.4%"></i></span><span class="signal-row"><b>Docs covered</b><span>71.8% · 158 / 220</span></span><span class="track"><i class="plain" style="width:71.8%"></i></span></div></div>
  </div>
</section>'''


# Voice -----------------------------------------------------------------------------------

def voice(text):
    rules = re.findall(r"^\d+\. \*\*([^*]+)\*\*", section_text(text, "The rules"), re.M)
    pairs = table_rows(section_text(text, "Kept and cut"))[1:]
    rule_items = "".join(f"<li>{inline(rule)}</li>" for rule in rules)
    pair_items = "".join(
        f'<li><p class="pair-label">Before</p><p class="pair-before">{inline(before)}</p>'
        f'<p class="pair-label">After</p><p class="pair-after">{inline(after)}</p><p class="pair-why">{inline(why)}</p></li>'
        for before, after, why in pairs)
    return f'''
<section class="specimen" aria-labelledby="sp-rules">
  <h2 id="sp-rules">Ten rules</h2>
  <ol class="rule-grid">{rule_items}</ol>
</section>
<section class="specimen" aria-labelledby="sp-pairs">
  <h2 id="sp-pairs">Real edits</h2>
  <ul class="pair-grid">{pair_items}</ul>
</section>'''


# Documents -------------------------------------------------------------------------------

SIZES = {"short": 1, "medium": 2, "long": 4}


def documents(text):
    cards = []
    for match in re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", text, re.S | re.M):
        name, body = match[1], match[2]
        if "**Shape**" not in body:
            continue
        reader = body.strip().split("\n\n")[0]
        steps = re.findall(r"^\d+\. (.+?) \((short|medium|long)\)$", body, re.M)
        blocks = "".join(f'<li class="block block-{size}" style="--size:{SIZES[size]}"><span>{esc(label)}</span></li>' for label, size in steps)
        cards.append(f'<li><a class="doc-name" href="#{anchor(name)}">{esc(name)}</a><p class="doc-reader">{inline(reader)}</p>'
                     f'<ol class="doc-shape" aria-label="{esc(name)} shape">{blocks}</ol></li>')
    return f'''
<section class="specimen" aria-labelledby="sp-shapes">
  <h2 id="sp-shapes">Ten shapes</h2>
  <p class="specimen-intro">Block height shows the most each section should take: short, medium or long.</p>
  <ul class="doc-grid">{"".join(cards)}</ul>
</section>'''


# Data ------------------------------------------------------------------------------------

def season_series():
    years = {"2021": 1.30, "2022": 1.15, "2023": 1.05, "2024": 1.22, "2025": 1.10}
    weeks = [f"W{w}" for w in range(1, 21)]
    series = {}
    for year, rate in years.items():
        total, values = 0.0, []
        for w in range(20):
            total += rate * (0.8 + 0.4 * ((w * 7 + int(year)) % 5) / 4)
            values.append(round(total, 1))
        series[year] = values
    total, current = 0.0, []
    for w in range(20):
        if w < 12:
            total += 1.55 * (0.85 + 0.3 * ((w * 3) % 4) / 3)
            current.append(round(total, 1))
        else:
            current.append(None)
    series["2026"] = current
    return weeks, series


def data(profile, motion=False):
    theme = figures.Theme(profile)
    bars = figures.bar_chart(theme, [("Feed", 38.5), ("Ethanol", 34.2), ("Exports", 15.8), ("Food and industrial", 11.5)],
                             id="sp-bar", focus="Feed", decimals=1, kind="percent", title="Use shares", motion=motion)
    weeks, series = season_series()
    lines = figures.line_chart(theme, weeks, series, id="sp-line", focus="2026", decimals=0, y_min=0,
                               title="Cumulative sales by week", tick_every=4, motion=motion)
    intervals = figures.interval_plot(theme, [("8:30 report", 0.4, -0.3, 1.1), ("10:30 report", 2.1, 1.2, 3.0),
                                              ("12:00 report", 0.2, -0.6, 1.0), ("Close", -0.1, -0.9, 0.7)],
                                      id="sp-int", focus="10:30 report", unit="¢", title="Price response by release time",
                                      reference_label="No effect")
    rows = [("2026-10-02", 1412.6, -4.1, 9.83), ("2026-10-09", 1588.0, 12.4, 11.42), ("2026-10-16", 1301.9, -18.0, 12.72),
            ("2026-10-23", 1650.3, 26.8, 14.37)]
    from datetime import date
    display = [(f"{date.fromisoformat(d).day} {date.fromisoformat(d):%b %Y}", figures.fmt(v, theme, decimals=1),
                figures.fmt(c, theme, decimals=1, kind="percent", sign=True), figures.fmt(t, theme, decimals=2)) for d, v, c, t in rows]
    table = figures.table(["Week ending", "Net sales (thousand t)", "Change vs prior week", "Season to date (million t)"],
                          display, numeric=(1, 2, 3), focus_row=3, label="Weekly sales table")
    formats = [("1234567", figures.fmt(1234567, theme), "Thousands separator"),
               ("-3.2", figures.fmt(-3.2, theme, decimals=1), "True minus sign"),
               ("0.2149 as a share", figures.fmt(21.49, theme, decimals=1, kind="percent"), "Percent, fixed decimals"),
               ("21.5% to 23.6%", figures.fmt(2.1, theme, decimals=1, kind="pp"), "Change in a rate is points"),
               ("4.1 to 5.3", figures.fmt_range(4.1, 5.3, theme, decimals=1), "En dash range, no spaces"),
               ("None", figures.fmt(None, theme), "Missing is never zero"),
               ("2026-10-23", "23 Oct 2026", "ISO in data, day month year on the page")]
    format_table = figures.table(["Input", "Display", "Rule"], formats, label="Number formats")

    # The chart set added after the November survey: scatter, distribution, matrix, small multiples, bands, part-to-whole, tiles.
    scatter = figures.scatter_plot(theme,
        [(28 + (i * 53 % 44), 30 + (i * 29 % 40) + (i * 53 % 44) * 0.4) for i in range(44)] + [(74, 86, "Session 12")],
        id="sp-scatter", x_label="Cold-start price ($)", y_label="Final close ($)", identity=True, focus="Session 12",
        x_min=20, x_max=100, y_min=20, y_max=100, title="Cold start vs final close")
    dense = figures.scatter_plot(theme, [((i * 17 % 90) + 2, ((i * 17 % 90) - 20) ** 2 * 0.06 + (i * 31 % 18)) for i in range(260)],
        id="sp-dense", x_label="ΔV vs apo pocket (Å³)", y_label="centroid distance (Å)", dense=True, vline=20,
        vline_label="rule threshold", x_min=0, x_max=95, y_min=0, title="Rule geometry")
    strip = figures.strip_plot(theme, {"1×": [0.48, 0.50, 0.52, 0.47, 0.55, 0.49], "10×": [0.55, 0.60, 0.58, 0.62, 0.50, 0.57],
                                       "100×": [0.61, 0.72, 0.65, 0.70, 0.68, 0.66]},
                               id="sp-strip", value_label="Seller surplus split", focus="100×", decimals=2, x_min=0.4, x_max=0.8)
    hist = figures.histogram(theme, [round(((i * 37 % 100) / 100) ** 1.8 * 6 + 0.6, 2) for i in range(160)],
                             id="sp-hist", value_label="Activity ratio (×)", reference=1, reference_label="no-report day", decimals=1, bins=14)
    cap_rows = ["b1a", "b1b", "b2", "controls"]
    cap_cols = [f"s{i}" for i in range(6)]
    cap_vals = [[0.1, 0.5, 0.9, 0.7, 0.3, 0.2], [0.0, 0.2, 0.6, 0.8, 0.4, 0.1], [0.6, 0.9, 0.8, 0.5, 0.3, 0.1], [0.0, 0.0, 0.1, 0.0, 0.0, 0.0]]
    heatmap = figures.heatmap(theme, cap_rows, cap_cols, cap_vals, id="sp-heat", decimals=1, legend_label="max ΔV, scaled 0–1")
    diverging = figures.heatmap(theme, ["8:30", "10:30", "12:00", "Close"], ["Mon", "Tue", "Wed", "Thu", "Fri"],
        [[-0.3, 0.2, -0.1, 0.4, 0.1], [1.8, 2.1, 1.9, 2.4, 2.0], [0.1, -0.2, 0.3, -0.1, 0.0], [-0.4, -0.1, -0.6, 0.2, -0.3]],
        id="sp-div", diverging=True, decimals=1, unit="¢", legend_label="price change (¢/bu)")
    sm_weeks = [f"W{i}" for i in range(1, 13)]
    panels = [("Corn", [1.2, 2.5, 3.9, 5.0, 6.1, 7.4, 8.8, 10.1, 11.0, 12.2, 13.1, 14.4]),
              ("Soybeans", [2.0, 2.3, 3.1, 3.4, 4.9, 5.2, 6.1, 6.3, 8.0, 8.4, 9.1, 9.5]),
              ("Wheat", [5.1, 4.4, 4.0, 3.6, 3.2, 2.9, 2.7, 3.1, 3.4, 4.0, 4.3, 4.9]),
              ("Sorghum", [0.8, 1.1, 1.6, 2.0, 2.3, 2.9, 3.2, 3.5, 4.1, 4.4, 5.0, 5.7])]
    multiples = figures.small_multiples(theme, sm_weeks, panels, id="sp-multi", decimals=0, unit=" Mt", title="Cumulative sales by crop")
    band = figures.band_chart(theme, sm_weeks,
        [1.1, 1.3, 1.25, 1.4, 1.35, 1.5, 1.45, 1.55, 1.6, 1.52, 1.58, 1.62],
        [([0.7, 0.8, 0.75, 0.85, 0.8, 0.9, 0.85, 0.95, 1.0, 0.92, 0.98, 1.02],
          [1.6, 1.9, 1.85, 2.0, 1.95, 2.1, 2.05, 2.2, 2.3, 2.18, 2.28, 2.35]),
         ([0.9, 1.05, 1.0, 1.15, 1.1, 1.25, 1.2, 1.3, 1.35, 1.28, 1.34, 1.4],
          [1.35, 1.6, 1.55, 1.7, 1.65, 1.8, 1.75, 1.85, 1.95, 1.84, 1.92, 1.98])],
        id="sp-band", reference=1, reference_label="no-report day", band_labels=["90%", "50%"],
        point=(8, 1.6, "this year"), tick_every=2, decimals=1, unit="×", y_min=0, title="Activity vs seasonal range")
    stacked = figures.stacked_bar(theme, [("2026", [38.5, 34.2, 15.8, 11.5]), ("2025", [34.0, 31.5, 21.0, 13.5]),
                                          ("2024", [33.1, 29.8, 24.0, 13.1])],
                                  ["Feed", "Ethanol", "Exports", "Food and industrial"], id="sp-stack", normalize=True, title="Use shares by year")
    wf = figures.waterfall(theme, 1200, [("New crop", 420), ("Feed and residual", -520), ("Exports", -310), ("Ethanol", -180)],
                           id="sp-wf", start_label="Beginning", end_label="Ending stocks", unit=" Mt", title="Corn balance sheet")
    tiles = figures.kpi_tiles(theme, [
        {"label": "Events studied", "value": 503},
        {"label": "Peak activity ratio", "value": 4.2, "decimals": 1, "unit": "×", "delta": 0.8, "delta_decimals": 1, "delta_unit": "×",
         "trend": [2.1, 2.6, 3.1, 3.4, 3.9, 4.2]},
        {"label": "Share in first 5 min", "value": 75.9, "decimals": 1, "kind": "percent", "delta": 3.1, "delta_kind": "pp",
         "trend": [68, 70, 71, 73, 74, 75.9]},
        {"label": "Median response", "value": 2.1, "decimals": 1, "unit": " ¢/bu", "delta": -0.3, "delta_decimals": 1, "delta_unit": " ¢",
         "higher_is_better": False, "trend": [2.6, 2.5, 2.4, 2.3, 2.2, 2.1]}])
    return f'''
<section class="specimen" aria-labelledby="sp-anatomy">
  <h2 id="sp-anatomy">Figure anatomy</h2>
  <p class="specimen-intro">Finding as the title, measure as the subtitle, the plot, one source line. The title and source are page text, so they cannot collide with the chart. {ILLUSTRATIVE}</p>
  {figures.figure("Feed is the largest use in this example", "Share of total use, %, one marketing year", bars, "Source: " + ILLUSTRATIVE)}
  {figures.figure("This season is running ahead of every year shown", "Cumulative net sales, million t, by week of the marketing year", lines,
                  "Source: " + ILLUSTRATIVE + " 2026 through week 12.", note="2021–2025 in Slate Mist for context; the dot marks the latest week.")}
  {figures.figure("Only the 10:30 report moves price beyond noise", "Mean price change in the 5 minutes after release, ¢/bu, with 95% intervals", intervals,
                  "Source: " + ILLUSTRATIVE)}
</section>
<section class="specimen" aria-labelledby="sp-relationships">
  <h2 id="sp-relationships">Relationships and distributions</h2>
  <p class="specimen-intro">One point, one row, one cell per observation. Highlight the series that carries the finding and hold the rest as context. {ILLUSTRATIVE}</p>
  {figures.figure("Sessions settle near where they open", "Final close vs cold-start price, $; the dashed line is no change", scatter, "Source: " + ILLUSTRATIVE,
                  note="Highlight one point; the rest stay as context. Add a y=x line so the reader sees the comparison.")}
  {figures.figure("Most candidates cluster below the rule threshold", "Pocket geometry, one mark per snapshot", dense, "Source: " + ILLUSTRATIVE,
                  note="Hundreds of points use small, low-opacity marks and a threshold rule, never a legend.")}
  {figures.figure("Higher stakes raise the seller’s split", "Seller surplus split by stakes multiple; the bar marks the median", strip, "Source: " + ILLUSTRATIVE)}
  {figures.figure("Activity clusters just above the no-report day", "Count of events by activity ratio", hist, "Source: " + ILLUSTRATIVE)}
</section>
<section class="specimen" aria-labelledby="sp-matrix">
  <h2 id="sp-matrix">Matrices</h2>
  <p class="specimen-intro">A sequential ramp for a magnitude, a diverging ramp centered on zero for a signed value. The cell number stays readable against its fill. {ILLUSTRATIVE}</p>
  {figures.figure("Later samples recover the pocket more often", "Capture strength by batch and sampling snapshot, scaled 0–1", heatmap, "Source: " + ILLUSTRATIVE)}
  {figures.figure("Only the 10:30 release moves price", "Mean price change by release time and weekday, ¢/bu", diverging, "Source: " + ILLUSTRATIVE,
                  note="Diverging ramp: copper below zero, slate above, parchment at no change.")}
</section>
<section class="specimen" aria-labelledby="sp-compose">
  <h2 id="sp-compose">Comparison and composition</h2>
  <p class="specimen-intro">Small multiples share one scale so panels compare honestly. Bands show a range behind a median. Part-to-whole bars and the balance sheet read left to right. {ILLUSTRATIVE}</p>
  {figures.figure("Corn and sorghum are pulling ahead", "Cumulative sales by crop, million t, weeks 1–12, shared scale", multiples, "Source: " + ILLUSTRATIVE, wide=True)}
  {figures.figure("This year sits at the top of its seasonal range", "Activity ratio with 50% and 90% bands", band, "Source: " + ILLUSTRATIVE)}
  {figures.figure("Feed and ethanol take the larger share each year", "Share of total use, %, by marketing year", stacked, "Source: " + ILLUSTRATIVE)}
  {figures.figure("Exports draw ending stocks down the most", "Corn balance, million t, from beginning to ending stocks", wf, "Source: " + ILLUSTRATIVE,
                  note="Sage adds, copper subtracts, slate marks the two totals.")}
</section>
<section class="specimen" aria-labelledby="sp-tiles">
  <h2 id="sp-tiles">Numbers at a glance</h2>
  <p class="specimen-intro">A few headline figures with a change against the prior period and a sparkline for direction. Green and copper text carry the good or bad reading; the number carries the size. {ILLUSTRATIVE}</p>
  {tiles}
</section>
<section class="specimen" aria-labelledby="sp-tables">
  <h2 id="sp-tables">Tables and numbers</h2>
  <p class="specimen-intro">Units in the header, numbers right-aligned in tabular figures, one highlighted row.</p>
  {table}
  {format_table}
</section>'''


# Motion ----------------------------------------------------------------------------------

def motion(profile):
    theme = figures.Theme(profile)
    weeks, series = season_series()
    lines = figures.line_chart(theme, weeks, series, id="mo-line", focus="2026", y_min=0, title="Cumulative sales by week",
                               tick_every=4, motion=True)
    ticks = [(38.5, 1, "", "%", "Feed share"), (2.1, 1, "+", " ¢/bu", "10:30 response"), (14.37, 2, "", " Mt", "Season to date, million t")]
    tick_html = "".join(
        f'<div><p class="tick-value" data-tick="{v}" data-decimals="{d}" data-prefix="{p}" data-suffix="{s}">{p}{v:,.{d}f}{s}</p><p class="tick-label">{esc(label)}</p></div>'
        for v, d, p, s, label in ticks)
    states = [("2025", [34.0, 31.5, 21.0, 13.5]), ("2026", [38.5, 34.2, 15.8, 11.5])]
    labels = ["Feed", "Ethanol", "Exports", "Food and industrial"]
    x0, scale, row, bar = 190, 9, 44, 24

    def geometry(values):
        return {f"b{i}": f"M{x0},{i * row + 10} h{v * scale:.1f} v{bar} h{-v * scale:.1f} Z" for i, v in enumerate(values)}

    def texts(values):
        return {f"v{i}": f"{v:.1f}%" for i, v in enumerate(values)}

    registered = [{"label": year, "geom": geometry(v), "text": texts(v)} for year, v in states]
    first = registered[-1]
    svg = [f'<svg class="wp-chart" viewBox="0 0 720 {row * 4}" role="img" aria-labelledby="mo-scrub-t"><title id="mo-scrub-t">Use shares, 2025 and 2026</title>']
    for i, label in enumerate(labels):
        svg.append(f'<text x="{x0 - 12}" y="{i * row + 27}" text-anchor="end" fill="{theme["text-primary"]}" font-size="16" font-family="{esc(theme.body)}">{esc(label)}</text>')
        svg.append(f'<path data-geom="b{i}" data-scrub-geom d="{first["geom"][f"b{i}"]}" fill="{theme["series-primary"]}"/>')
        svg.append(f'<text data-text="v{i}" x="{x0 + max(v[i] for _, v in states) * scale + 10:.1f}" y="{i * row + 27}" fill="{theme["text-secondary"]}" font-size="14" font-family="{esc(theme.code)}">{first["text"][f"v{i}"]}</text>')
    svg.append(f'<line x1="{x0}" x2="{x0}" y1="0" y2="{row * 4}" stroke="{theme["structure"]}" stroke-width="2"/></svg>')
    scrub = (f'<div id="mo-scrub" data-states="{esc(json.dumps(registered))}">{"".join(svg)}</div>'
             f'<p class="scrub-control" hidden><label for="mo-scrub-range">Marketing year</label><input id="mo-scrub-range" type="range" min="0" max="1" step="1" value="1" '
             f'data-scrub="mo-scrub" data-readout="mo-scrub-readout" aria-valuetext="2026"><output id="mo-scrub-readout">2026</output></p>')
    return f'''
<section class="specimen" aria-labelledby="sp-motion">
  <h2 id="sp-motion">The three moves</h2>
  <p class="specimen-intro">Each specimen is complete without script and with reduced motion on. {ILLUSTRATIVE}</p>
  {figures.figure("Draw-on: lines arrive in reading order", "Context years first, the focus year last", lines, "Source: " + ILLUSTRATIVE)}
  <figure class="wp-figure" aria-labelledby="mo-tick-title"><p class="wp-figure-title" id="mo-tick-title">Tick-to-value: numbers land exactly</p><p class="wp-figure-subtitle">Counts from zero once in view, with tabular numerals</p>
  <div class="tick-grid">{tick_html}</div><figcaption>Source: {ILLUSTRATIVE}</figcaption></figure>
  <figure class="wp-figure" aria-labelledby="mo-scrub-title"><p class="wp-figure-title" id="mo-scrub-title">Scrub: geometry moves, readouts stay registered</p><p class="wp-figure-subtitle">Share of total use, %, by marketing year</p>
  <div class="wp-figure-plot">{scrub}</div><figcaption>Source: {ILLUSTRATIVE}</figcaption></figure>
</section>'''


# Dispatch --------------------------------------------------------------------------------

def _seed_scene(theme):
    """Static final frame of the sprout scene; scenes/lab.js animates it from the brief."""
    t = theme
    leaves = [("lab-leaf-l", "M360 156 C 332 128, 296 128, 272 146 C 296 168, 334 170, 360 156 Z", "M360 156 C 357 151, 356 147, 358 143 C 361 147, 362 151, 360 156 Z"),
              ("lab-leaf-r", "M360 138 C 390 106, 430 106, 452 122 C 430 148, 390 152, 360 138 Z", "M360 138 C 362 133, 363 129, 362 125 C 359 129, 358 133, 360 138 Z")]
    roots = ["M360 258 C 357 280, 346 300, 326 318", "M360 258 C 363 284, 374 304, 396 322", "M360 258 C 360 290, 362 318, 357 344"]
    parts = ['<svg id="lab-seed" class="wp-chart lab-svg" viewBox="0 0 720 360" role="img" aria-labelledby="lab-seed-t">',
             '<title id="lab-seed-t">A seed in soil with three roots, a stem and two open leaves</title>',
             f'<rect x="0" y="244" width="720" height="116" fill="{t["well"]}"/>',
             f'<line x1="40" x2="680" y1="244" y2="244" stroke="{t["structure"]}" stroke-width="2"/>',
             '<path id="lab-fall" d="M292 24 C 318 90, 352 170, 360 254" fill="none" stroke="none"/>']
    parts += [f'<path class="lab-root" d="{d}" fill="none" stroke="{t["context"]}" stroke-width="3" stroke-linecap="round"/>' for d in roots]
    parts.append(f'<path id="lab-stem" d="M360 258 C 360 214, 352 176, 360 130" fill="none" stroke="{t["outcome-positive-text"]}" stroke-width="4" stroke-linecap="round"/>')
    parts += [f'<path id="{i}" class="lab-leaf" d="{leaf}" data-bud="{bud}" fill="{t["outcome-positive"]}" stroke="{t["outcome-positive-text"]}" stroke-width="2"/>'
              for i, leaf, bud in leaves]
    parts.append(f'<g id="lab-seed-body" transform="translate(360 254) rotate(24)"><ellipse rx="11" ry="7" fill="{t["emphasis-text"]}"/></g></svg>')
    return "".join(parts)


def _split_scene(theme):
    """One bushel as a single stacked bar, split into four ranked bars as the reader scrolls."""
    t = theme
    rows = [("Feed", 38.5), ("Ethanol", 34.2), ("Exports", 15.8), ("Food and industrial", 11.5)]
    x0, scale, row, bar, top = 190, 5.0, 52, 28, 44
    parts = ['<svg id="lab-split" class="wp-chart lab-svg" viewBox="0 0 720 260" role="img" aria-labelledby="lab-split-t">',
             '<title id="lab-split-t">Use of one bushel: feed 38.5%, ethanol 34.2%, exports 15.8%, food and industrial 11.5%</title>',
             f'<text class="lab-early" x="{x0 - 12}" y="{top + 20}" text-anchor="end" opacity="0" fill="{t["text-primary"]}" font-size="16" font-family="{esc(theme.body)}">One bushel</text>']
    stack_x = x0
    for i, (label, value) in enumerate(rows):
        y = top + i * row
        width = value * scale
        parts.append(f'<text class="lab-label lab-late" x="{x0 - 12}" y="{y + 20}" text-anchor="end" fill="{t["text-primary"]}" font-size="16" font-family="{esc(theme.body)}">{esc(label)}</text>')
        parts.append(f'<rect class="lab-bar" x="{x0}" y="{y}" width="{width:.1f}" height="{bar}" data-stack-x="{stack_x:.1f}" data-stack-y="{top}" '
                     f'fill="{t["series-primary"]}" stroke="{t["canvas"]}" stroke-width="2"/>')
        parts.append(f'<text class="lab-late" x="{x0 + width + 10:.1f}" y="{y + 20}" fill="{t["text-secondary"]}" font-size="14" font-family="{esc(theme.code)}">{value:.1f}%</text>')
        stack_x += width
    parts.append(f'<line x1="{x0}" x2="{x0}" y1="{top - 6}" y2="{top + row * 4 - 16}" stroke="{t["structure"]}" stroke-width="2"/></svg>')
    return "".join(parts)


RANK_STATES = [("2024/25", [("A", 34.0), ("B", 25.5), ("C", 15.2), ("D", 11.8), ("E", 7.1), ("F", 6.4)]),
               ("2025/26", [("B", 31.2), ("A", 28.4), ("D", 14.6), ("C", 12.0), ("F", 7.3), ("E", 6.5)])]


def _rank_scene():
    """A ranked list that re-sorts between two registered seasons with Flip. Exporter B is the focus."""
    label, rows = RANK_STATES[-1]
    peak = max(v for _, state in RANK_STATES for _, v in state)
    states = {name: {key: value for key, value in state} for name, state in RANK_STATES}
    buttons = "".join(f'<button type="button" class="button secondary" data-season="{esc(name)}" aria-pressed="{str(name == label).lower()}">{esc(name)}</button>'
                      for name, _ in RANK_STATES)
    focus = ' class="focus"'
    items = "".join(f'<li data-key="{key}"{focus if key == "B" else ""}><span class="lab-rank-name">Exporter {key}</span>'
                    f'<span class="lab-rank-track"><i style="width:{value / peak * 100:.1f}%"></i></span>'
                    f'<span class="lab-rank-value">{value:.1f}%</span></li>' for key, value in rows)
    return (f'<div id="lab-rank" class="lab-rank" data-states="{esc(json.dumps(states))}" data-peak="{peak}">'
            f'<div class="control-row lab-toggle" role="group" aria-label="Marketing year" hidden>{buttons}</div>'
            f'<ol class="lab-rank-list">{items}</ol><p class="lab-rank-status" role="status"></p></div>')


def scenes(profile):
    theme = figures.Theme(profile)
    controls = ('<p class="lab-controls" data-for="{id}" hidden><button type="button" class="button">Play</button>'
                '<input type="range" min="0" max="1" step="0.001" value="1" aria-label="Scene time"><output>Finished frame</output></p>')
    seed = figures.figure("Brief: a seed drops, roots reach down, a sprout opens",
                          "MotionPath carries the fall, DrawSVG draws roots and stem, MorphSVG opens the leaves",
                          _seed_scene(theme) + controls.format(id="lab-seed"),
                          "Plays once when it comes into view. Drag the slider to stop on any moment.")
    split = figures.figure("Scroll: one bushel splits into its four uses",
                           "Share of use, %. ScrollTrigger ties the split to your scroll position",
                           _split_scene(theme), "Source: " + ILLUSTRATIVE)
    rank = figures.figure("Flip: exporter B overtakes A",
                          "Share of world exports, %, by marketing year. Values change first, then rows move",
                          _rank_scene(), "Source: " + ILLUSTRATIVE)
    frames = [("ten-thirty", "10:30", "1920 × 1080, 10 seconds. A clock becomes the chart’s first axis label; bars arrive in time order; the number lands last.", "wide"),
              ("sunrise", "Sunrise", "1080 × 1080, 6 seconds. The square brand sting: horizon, sun, wordmark, hold.", "square")]
    video = "".join(
        f'<figure class="lab-video lab-video-{shape}" aria-labelledby="video-{name}"><p class="wp-figure-title" id="video-{name}">{esc(title)}</p><p class="wp-figure-subtitle">{esc(note)}</p>'
        f'<iframe class="lab-frame" src="../scenes/{name}/index.html" title="{esc(title)} scene player" loading="lazy"></iframe>'
        f'<figcaption><a href="../scenes/{name}/index.html">Open full size</a> · Render: <code>python3 design-system/scripts/scenes.py render {name}</code></figcaption></figure>'
        for name, title, note, shape in frames)
    return f'''
<section class="specimen" aria-labelledby="sp-gsap">
  <h2 id="sp-gsap">In the page, with GSAP</h2>
  <p class="specimen-intro">Things a video cannot do: respond to scroll, to a click, to a slider. Each piece is written in its finished state, so it reads complete without script and with reduced motion on.</p>
  {seed}
  {split}
  {rank}
</section>
<section class="specimen" aria-labelledby="sp-video">
  <h2 id="sp-video">As video, with HyperFrames</h2>
  <p class="specimen-intro">Each scene is one HTML file with a paused GSAP timeline. The same file plays here and renders to MP4, frame for frame. Each opens on its last frame; press Play.</p>
  <div class="lab-video-grid">{video}</div>
</section>'''


def for_document(key, profile, text):
    """Return (html, page options) for a document's designed section."""
    if key == "BRAND_KIT.md":
        return brand(profile), {}
    if key == "VOICE.md":
        return voice(text), {}
    if key == "DOCUMENTS.md":
        return documents(text), {}
    if key == "adapters/data.md":
        return data(profile), {}
    if key == "adapters/motion.md":
        return motion(profile), {"motion": True}
    if key == "adapters/scenes.md":
        return scenes(profile), {"styles": ("scenes/lab.css",), "scripts": SCENE_SCRIPTS}
    return "", {}


SCENE_SCRIPTS = tuple(f"scenes/vendor/gsap/{name}.min.js" for name in
                      ("gsap", "ScrollTrigger", "Flip", "DrawSVGPlugin", "MorphSVGPlugin", "MotionPathPlugin")) + ("scenes/lab.js",)
