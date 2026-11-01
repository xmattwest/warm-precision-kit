"""Example pages: finished artifacts built from the kit, each shown with the decisions that shaped it.

Every number in a title, lede or note is computed from the same values its chart draws, so a page
cannot claim something its figure does not show. Document shapes, modes and patterns are read from
DOCUMENTS.md; colors and sizes come from tokens.json. All values are illustrative.
"""

import re

import figures
import specimens

esc, inline = specimens.esc, specimens.inline
ILLUSTRATIVE = "Illustrative values, not real data."
SOURCE = "Source: " + ILLUSTRATIVE

# Where each rule lives in the handbook, relative to examples/.
RULES = {
    "anatomy": ("../handbook/adapters-data.html#figure-anatomy", "Data · Figure anatomy"),
    "question": ("../handbook/adapters-data.html#start-with-the-question", "Data · Start with the question"),
    "color": ("../handbook/adapters-data.html#color-and-emphasis", "Data · Color and emphasis"),
    "evidence": ("../handbook/adapters-data.html#evidence-conventions", "Data · Evidence conventions"),
    "review": ("../handbook/adapters-data.html#review", "Data · Review"),
    "sizes": ("../handbook/adapters-data.html#sizes", "Data · Sizes"),
    "tables": ("../handbook/adapters-data.html#tables", "Data · Tables"),
    "rules": ("../handbook/VOICE.html#the-rules", "Voice · The rules"),
    "by-document": ("../handbook/VOICE.html#by-document", "Voice · By document"),
    "attention": ("../handbook/PHILOSOPHY.html#3-attention-is-a-limited-resource", "Principles · Attention is limited"),
    "clutter": ("../handbook/PHILOSOPHY.html#4-remove-clutter-preserve-meaning", "Principles · Remove clutter"),
    "evidence-hierarchy": ("../handbook/PHILOSOPHY.html#2-evidence-shapes-the-hierarchy", "Principles · Evidence shapes the hierarchy"),
    "scale": ("../handbook/PHILOSOPHY.html#6-meaning-survives-a-change-of-scale", "Principles · Meaning survives scale"),
    "explainer": ("../handbook/DOCUMENTS.html#explainer-page", "Documents · Explainer page"),
    "memo": ("../handbook/DOCUMENTS.html#decision-memo", "Documents · Decision memo"),
    "slides": ("../handbook/adapters-slides.html#geometry-and-typography", "Slides · Geometry and typography"),
}

PAGES = (("explainer.html", "Explainer page"), ("memo.html", "Decision memo"),
         ("figures.html", "From default to finished"), ("media.html", "One finding, four sizes"))


def rule_link(key):
    href, label = RULES[key]
    return f'<a href="{esc(href)}">{esc(label)}</a>'


# Data ------------------------------------------------------------------------------------

def season():
    """Cumulative export sales by week, this season against the five before it."""
    weeks, series = specimens.season_series()
    season_name = max(series)
    current = series[season_name]
    prior = {year: values for year, values in series.items() if year != season_name}
    latest = max(i for i, v in enumerate(current) if v is not None)
    average = sum(values[latest] for values in prior.values()) / len(prior)
    best_year = max(prior, key=lambda year: prior[year][-1])
    weekly = [current[0]] + [round(current[i] - current[i - 1], 1) for i in range(1, latest + 1)]
    floor = (prior[best_year][-1] - current[latest]) / (len(weeks) - 1 - latest)
    return {
        "season": season_name,
        "weeks": weeks, "series": series, "current": current, "prior": prior, "latest": latest, "week": latest + 1,
        "total": current[latest], "average": average, "ahead": (current[latest] / average - 1) * 100,
        "ahead_every_week": all(current[i] > max(values[i] for values in prior.values()) for i in range(latest + 1)),
        "weekly": weekly, "best_year": best_year, "best_total": prior[best_year][-1], "floor": floor,
        "remaining": len(weeks) - 1 - latest, "last_week": len(weeks),
    }


RELEASES = [("8:30 report", 0.4, -0.3, 1.1), ("10:30 report", 2.1, 1.2, 3.0), ("12:00 report", 0.2, -0.6, 1.0), ("Close", -0.1, -0.9, 0.7)]
TICKETS = [("Billing", 412), ("Data export", 174), ("Login", 388), ("Notifications", 96), ("Other", 63), ("Performance", 251)]
TICKET_FOCUS = "Login"


def tickets():
    counts = dict(TICKETS)
    leader = max(counts, key=counts.get)
    return {"rows": TICKETS, "total": sum(counts.values()), "leader": leader, "gap": counts[leader] - counts[TICKET_FOCUS],
            "title": f"Login problems trail {leader.lower()} by {counts[leader] - counts[TICKET_FOCUS]} tickets",
            "subtitle": f"Support tickets by category, count, last 30 days (n = {sum(counts.values()):,})"}


# Page parts ------------------------------------------------------------------------------

def choosing(documents_text, make):
    """Mode, pattern and medium for a document type, read from the Choosing table."""
    for goal, name, mode, pattern, medium in specimens.table_rows(specimens.section_text(documents_text, "Choosing"))[1:]:
        if name == make:
            return {"goal": goal, "mode": mode, "pattern": pattern, "medium": medium}
    raise KeyError(f"{make} is not in DOCUMENTS.md's Choosing table")


def shape(documents_text, make):
    """The document type's default sections, in order, from DOCUMENTS.md."""
    body = specimens.section_text(documents_text, make)
    steps = re.findall(r"^\d+\. (.+?) \((short|medium|long)\)$", body, re.M)
    assert steps, f"No shape for {make} in DOCUMENTS.md"
    return steps


def intro(kicker, title, lead, meta):
    items = "".join(f"<li>{esc(k)}: <b>{esc(v)}</b></li>" for k, v in meta)
    return (f'<header class="ex-wrap ex-intro"><p class="context"><a href="index.html">Examples</a> · {esc(kicker)}</p>'
            f'<h1>{esc(title)}</h1><p class="lead">{lead}</p><ul class="ex-meta">{items}</ul></header>')


def shape_strip(documents_text, make, anchors):
    steps = shape(documents_text, make)
    assert len(steps) == len(anchors), f"{make}: {len(steps)} shape steps, {len(anchors)} anchors"
    links = "".join(f'<li><a href="#{a}"><b>{i}</b>{esc(label)} <span>{esc(size)}</span></a></li>'
                    for i, ((label, size), a) in enumerate(zip(steps, anchors), 1))
    return (f'<nav class="ex-wrap" aria-label="{esc(make)} shape"><p class="context">The {esc(make.lower())} shape, from Documents</p>'
            f'<ol class="ex-shape">{links}</ol></nav>')


def annotated(label, rows):
    """rows: [(anchor, sheet_html, (title, text, rule_key) or None)]. Notes are numbered in reading order."""
    out, number = [], 0
    for anchor, sheet, note in rows:
        mark = note_html = ""
        if note:
            number += 1
            title, text, rule = note
            mark = f'<span class="ex-mark" aria-hidden="true">{number}</span>'
            note_html = (f'<aside class="ex-note" aria-label="Note {number}: {esc(title)}"><p class="ex-note-head"><b>{number}</b>{esc(title)}</p>'
                         f'<p>{inline(text)}</p>{rule_link(rule)}</aside>')
        out.append(f'<div class="ex-row"><div class="ex-sheet" id="{anchor}">{mark}{sheet}</div>{note_html}</div>')
    return (f'<section class="ex-wrap ex-section ex-annotated" aria-label="{esc(label)}">'
            f'<p class="ex-toggle" hidden><button type="button" class="button secondary" aria-pressed="true">Hide the notes</button></p>'
            f'{"".join(out)}</section>')


def next_steps(current):
    names = [name for name, _ in PAGES]
    i = names.index(current)
    prev_link = f'<a class="button secondary" href="{PAGES[i - 1][0]}">← {esc(PAGES[i - 1][1])}</a>' if i > 0 else ""
    next_link = f'<a class="button" href="{PAGES[i + 1][0]}">{esc(PAGES[i + 1][1])} →</a>' if i < len(PAGES) - 1 else \
        '<a class="button" href="../warm-precision-kit.zip" download>Download the kit</a>'
    return (f'<section class="ex-wrap ex-section"><h2>Next</h2><p class="ex-next">{prev_link}{next_link}'
            f'<a class="button secondary" href="index.html">All examples</a></p></section>')


# Explainer -------------------------------------------------------------------------------

def _season_chart(theme, s, id, width=720, height=340):
    return figures.line_chart(theme, s["weeks"], s["series"], id=id, focus=s["season"], y_min=0, width=width, height=height,
                              title="Cumulative export sales by week", tick_every=4)


def explainer(profile, documents_text):
    theme = figures.Theme(profile)
    s = season()
    mt = lambda v, d=1: figures.fmt(v, theme, decimals=d, unit=" million t")
    ahead = figures.fmt(s["ahead"], theme, decimals=0, kind="percent")
    first_year, last_year = min(s["prior"]), max(s["prior"])
    lowest = min(s["weekly"])
    title = f"Export sales are running {ahead} ahead of the five-year average"
    meta = choosing(documents_text, "Explainer page")
    picture_title = (f"This season is ahead of every year since {first_year}, every week so far" if s["ahead_every_week"]
                     else f"This season is ahead of the {first_year}–{last_year} average")
    tiles = figures.kpi_tiles(theme, [
        {"label": "Sales to date", "value": s["total"], "decimals": 1, "unit": " Mt", "trend": s["current"][:s["latest"] + 1]},
        {"label": "Ahead of five-year average", "value": s["ahead"], "decimals": 1, "kind": "percent"},
        {"label": f"Week {s['week']} sales", "value": s["weekly"][-1], "decimals": 1, "unit": " Mt",
         "delta": s["weekly"][-1] - s["weekly"][-2], "delta_decimals": 1, "delta_unit": " Mt"},
        {"label": "Slowest week so far", "value": lowest, "decimals": 1, "unit": " Mt"}])
    weeks_shown = [3, 7, s["latest"]]
    table_rows = [(year, *[figures.fmt(values[i], theme, decimals=1) for i in weeks_shown])
                  for year, values in sorted(s["series"].items(), reverse=True)]
    data_table = figures.table(["Season", *[f"Week {i + 1} (million t)" for i in weeks_shown]], table_rows,
                               numeric=(1, 2, 3), focus_row=0, focus_label="this season", label="Cumulative sales by season")
    rows = [
        ("ex-takeaway",
         f'<p class="context">Export outlook · week {s["week"]}</p><h2 class="ex-title">{esc(title)}</h2>'
         f'<p class="lead">For anyone booking freight this winter. After {s["week"]} weeks, this season\'s sales total '
         f'{esc(mt(s["total"]))}, against {esc(mt(s["average"]))} on average at the same week of {first_year}–{last_year}.</p>',
         ("The title is the finding",
          "It states the result and its size, so a stranger knows what the page says before reading on. "
          "The lede names the reader and gives the two numbers the title compares.", "by-document")),
        ("ex-picture",
         figures.figure(picture_title, "Cumulative net export sales, million t, by week of the marketing year",
                        _season_chart(theme, s, "ex-season"), SOURCE + f" {s['season']} through week {s['week']}.",
                        note=f"{first_year}–{last_year} in Slate Mist for context; the dot marks the latest week."),
         ("One focus, the rest as context",
          "This season is Blue Slate with one orange end mark. The five earlier seasons are Slate Mist. Every line is labelled "
          "at its end, so there is no legend to decode.", "color")),
        ("ex-pace",
         f'<h3>The pace has held for {s["week"]} weeks</h3><p>Weekly sales have stayed between {esc(mt(lowest))} and '
         f'{esc(mt(max(s["weekly"])))}. No single week carries the total.</p>{tiles}',
         ("Numbers carry the confidence",
          "No “strong” or “robust”. The tiles give the figure, its unit and its scope, and the copy never adds an adjective "
          "the numbers already cover.", "rules")),
        ("ex-risk",
         f'<h3>What it would take to fall behind</h3><p>{s["best_year"]} finished week {s["last_week"]} at '
         f'{esc(mt(s["best_total"]))}, the most of any recent season. To end below it, sales would have to average under '
         f'{esc(mt(s["floor"], 2))} a week for the remaining {s["remaining"]} weeks. The slowest week this season was '
         f'{esc(mt(lowest))}.</p>',
         ("Every number is computed",
          "The floor, the gap and the slowest week are calculated from the same series the chart draws. Change the data "
          "and the sentence changes with it.", "review")),
        ("ex-next",
         '<h3>What to do next</h3><ul><li>Plan freight for weeks 13 to 20 at the current pace, not the five-year average.</li>'
         f'<li>Check again at week 16. If weekly sales average under {esc(mt(s["floor"], 2))}, revisit this page.</li></ul>',
         ("End on the next move",
          "An explainer finishes with what the reader can do, in a short list. Not a summary of what they just read.", "explainer")),
        ("ex-detail",
         f'<details><summary>The numbers behind the chart</summary>{data_table}<p class="small">Cumulative net sales at weeks 4, 8 '
         f'and {s["week"]}. {esc(ILLUSTRATIVE)}</p></details>',
         ("Detail moves to a disclosure",
          "The exact values sit one click away, in a table. Readers who want to check the chart can, and nobody else has to "
          "scroll past it.", "tables")),
    ]
    anchors = ["ex-takeaway", "ex-picture", "ex-pace", "ex-next", "ex-detail"]
    body = (intro("Explainer page", "An explainer page, annotated",
                  f"The reader is a planner deciding whether to book extra freight. The goal: <strong>{esc(meta['goal'].lower())}</strong> "
                  "in a few minutes. The page is on the left; the decisions behind it are on the right.",
                  [("Document", "Explainer page"), ("Mode", meta["mode"]), ("Pattern", meta["pattern"]), ("Medium", meta["medium"])])
            + shape_strip(documents_text, "Explainer page", anchors)
            + annotated("Explainer page with notes", rows) + next_steps("explainer.html"))
    return "An explainer page, annotated", body, "A finished explainer page built with Warm Precision, with the design decisions beside it."


# Decision memo ---------------------------------------------------------------------------

def memo(profile, documents_text):
    theme = figures.Theme(profile)
    meta = choosing(documents_text, "Decision memo")
    best = max(RELEASES, key=lambda r: r[1])
    clears = [r for r in RELEASES if r[2] > 0]
    assert clears == [best], "The memo's recommendation assumes exactly one release clears zero"
    c = lambda v: figures.fmt(v, theme, decimals=1, sign=True)
    rng = lambda lo, hi: figures.fmt_range(lo, hi, theme, decimals=1)
    intervals = figures.interval_plot(theme, RELEASES, id="ex-releases", focus=best[0], unit="¢",
                                      title="Price response by release time", reference_label="No effect")
    options = [("Keep 8:30", "8:30 report"), ("Move to 10:45", "10:30 report"), ("Move to 12:15", "12:00 report"), ("After the close", "Close")]
    after = {"Keep 8:30": "No", "Move to 10:45": "Yes", "Move to 12:15": "Yes, and 12:00", "After the close": "Yes, all of them"}
    cost = {"Keep 8:30": "None", "Move to 10:45": "Note drafted after 10:30", "Move to 12:15": "Misses the morning", "After the close": "Read the next day"}
    by_release = {r[0]: r for r in RELEASES}
    table_rows = [(name, f"{c(by_release[rel][1])} ({rng(by_release[rel][2], by_release[rel][3])})", after[name], cost[name]) for name, rel in options]
    focus_row = [rel for _, rel in options].index(best[0])
    compare = figures.table(["Option", "Price response (¢/bu, 95% interval)", "Readers already have the release", "Cost to the team"],
                            table_rows, numeric=(1,), focus_row=focus_row, focus_label="recommended", label="Options compared")
    rows = [
        ("ex-question",
         '<p class="context">Decision memo · for the reports lead · decide by Friday</p>'
         '<h2 class="ex-title">Should the weekly price note go out after the 10:30 release?</h2>',
         ("Open with the question",
          "The reader came here to decide something. The title is that decision, and the kicker says who decides and by when.",
          "memo")),
        ("ex-recommendation",
         f'<p class="ex-answer"><strong>Yes. Move the note from 8:30 to 10:45.</strong> The 10:30 report is the only release whose '
         f'price response clears zero: {esc(c(best[1]))} ¢/bu on average in the five minutes after it '
         f'(95% interval {esc(rng(best[2], best[3]))}).</p>',
         ("Answer first, then the reason",
          "One word, one action, one number with its interval. The reader can say yes before they reach the evidence.",
          "evidence-hierarchy")),
        ("ex-options",
         figures.figure("Only the 10:30 report moves price beyond noise",
                        "Mean price change in the 5 minutes after release, ¢/bu, with 95% intervals", intervals, SOURCE)
         + compare,
         ("Every option on the same dimensions",
          "The chart answers “how big, and how sure?” and draws the no-effect line, so an interval that crosses zero is visible "
          "as one. The table puts every option on the same four columns.", "question")),
        ("ex-risks",
         '<h3>Risks, and what would change the answer</h3><ul>'
         '<li>Readers in earlier time zones get the note two hours later. Ask the three largest before switching.</li>'
         '<li>If the 10:30 response falls inside the 8:30 interval for eight weeks running, switch back.</li></ul>',
         ("Say what would change the answer",
          "A recommendation is stronger when it names the evidence that would overturn it. That condition is measurable.",
          "evidence")),
        ("ex-open",
         '<h3>Open questions</h3><ul><li>Does the effect hold in harvest months, when volume is higher?</li>'
         '<li>Would a short 8:30 alert plus the full 10:45 note serve both groups?</li></ul>',
         ("Unknowns stay labelled",
          "Open questions are listed as questions. Nothing is filled in with a plausible guess.", "evidence-hierarchy")),
    ]
    anchors = ["ex-question", "ex-recommendation", "ex-options", "ex-risks", "ex-open"]
    body = (intro("Decision memo", "A decision memo, annotated",
                  f"The reader is the person who signs off. The goal: <strong>{esc(meta['goal'].lower())}</strong>, "
                  "without asking a follow-up question.",
                  [("Document", "Decision memo"), ("Mode", meta["mode"]), ("Pattern", meta["pattern"]), ("Medium", meta["medium"])])
            + shape_strip(documents_text, "Decision memo", anchors)
            + annotated("Decision memo with notes", rows) + next_steps("memo.html"))
    return "A decision memo, annotated", body, "A finished decision memo built with Warm Precision, with the design decisions beside it."


# From default to finished ------------------------------------------------------------------

def _draft_columns(theme, rows, id):
    """The spreadsheet default: data order, a color per bar, a legend, heavy gridlines."""
    width, height, left, top, bottom, legend_w = 720, 340, 56, 16, 28, 190
    plot_w, plot_h = width - left - legend_w - 24, height - top - bottom
    peak = 450
    roles = ("series-primary", "emphasis", "outcome-positive", "emphasis-text", "context", "text-secondary")
    slot = plot_w / len(rows)
    caption = theme.chart["caption"]
    parts = [figures._open(theme, width, height, id, "Tickets by category, default chart",
                           "Columns in alphabetical order, one color per category, with a legend")]
    for t in range(0, peak + 1, 50):
        y = top + plot_h * (1 - t / peak)
        parts.append(f'<line x1="{left}" x2="{left + plot_w:.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{theme["structure"]}" stroke-width="1"/>')
        parts.append(figures._text(theme, left - 8, y + caption * 0.34, str(t), size=caption, anchor="end", color="text-secondary"))
    for i, (label, value) in enumerate(rows):
        h = plot_h * value / peak
        parts.append(f'<rect x="{left + i * slot + slot * 0.18:.1f}" y="{top + plot_h - h:.1f}" width="{slot * 0.64:.1f}" height="{h:.1f}" fill="{theme[roles[i]]}"/>')
    lx = width - legend_w
    parts.append(f'<rect x="{lx}" y="{top}" width="{legend_w}" height="{len(rows) * 30 + 16}" fill="none" stroke="{theme["structure"]}"/>')
    for i, (label, _) in enumerate(rows):
        y = top + 16 + i * 30
        parts.append(f'<rect x="{lx + 14}" y="{y}" width="14" height="14" fill="{theme[roles[i]]}"/>')
        parts.append(figures._text(theme, lx + 38, y + 12, label, size=caption))
    return "".join(parts) + "</svg>"


def _draft_bars(theme, rows, id):
    """Sorted, one color, names beside bars, but still an axis and gridlines instead of values."""
    rows = sorted(rows, key=lambda r: r[1], reverse=True)
    size, caption = theme.chart["label"], theme.chart["caption"]
    width, row, bar, peak = 720, 44, 24, 450
    label_w = figures._label_width([r[0] for r in rows], size)
    plot_w = width - label_w - 24
    height = row * len(rows) + 32
    parts = [figures._open(theme, width, height, id, "Tickets by category, sorted with an axis",
                           "Horizontal bars sorted largest first, one color, with gridlines and a value axis")]
    for t in range(0, peak + 1, 50):
        x = label_w + plot_w * t / peak
        parts.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="0" y2="{row * len(rows)}" stroke="{theme["structure"]}" stroke-opacity="0.5"/>')
        parts.append(figures._text(theme, x, height - 8, str(t), size=caption, anchor="middle", color="text-secondary"))
    for i, (label, value) in enumerate(rows):
        y = i * row + (row - bar) / 2
        parts.append(figures._text(theme, label_w - 12, y + bar / 2 + size * 0.36, label, anchor="end"))
        parts.append(f'<rect x="{label_w:.1f}" y="{y:.1f}" width="{plot_w * value / peak:.1f}" height="{bar}" rx="2" fill="{theme["series-primary"]}"/>')
    return "".join(parts) + "</svg>"


def figure_stages(profile):
    theme = figures.Theme(profile)
    t = tickets()
    rows = t["rows"]
    plain = figures.bar_chart(theme, rows, id="st-labelled", title="Tickets by category")
    focused = figures.bar_chart(theme, rows, id="st-focus", focus=TICKET_FOCUS, title="Tickets by category")
    final = figures.figure(t["title"], t["subtitle"], figures.bar_chart(theme, rows, id="st-final", focus=TICKET_FOCUS, title=t["title"]), SOURCE)
    gray = figures.figure(t["title"], t["subtitle"], figures.bar_chart(theme, rows, id="st-gray", focus=TICKET_FOCUS, title=t["title"]),
                          SOURCE + " Shown in grayscale.")
    draft = lambda title, svg: f'<p class="ex-draft-title">{esc(title)}</p><div class="wp-figure-plot">{svg}</div>'
    return t, [
        ("The default", "This is what a spreadsheet gives you: columns in alphabetical order, a different color for every bar, "
         "a legend to decode and a title that names the topic.",
         "Every color claims the bars differ in kind. Here they differ only in size, and the reader has to match swatches to find out which is which.",
         "color", draft("Tickets by category", _draft_columns(theme, rows, "st-default"))),
        ("Sort, turn sideways, use one color", "Bars are sorted largest first and turned horizontal, so each name sits beside its own bar. "
         "One color, because the categories are the same kind of thing. The legend is gone.",
         "The reader can answer “which is biggest?” without looking anywhere else.",
         "question", draft("Tickets by category", _draft_bars(theme, rows, "st-sorted"))),
        ("Label the values, drop the axis", "Each bar ends in its exact count. The gridlines, the axis and its tick labels go, "
         "because the labels now carry the numbers.",
         "Fewer things to look at, and nothing lost. Removing an element is safe when the reader can still draw the same conclusion.",
         "clutter", draft("Tickets by category", plain)),
        ("Mark the one thing it is about", f"{TICKET_FOCUS} gets the one orange fill, with a Blue Slate outline, because orange alone "
         "is under 3:1 contrast on Ivory. Its value is set in bold.",
         "The finding is about login, so the eye should land there first. One focus per figure, never a rainbow of emphasis.",
         "attention", draft("Tickets by category", focused)),
        ("Write the finding as the title", "The topic title becomes the finding, with the number in it. The subtitle states the measure, "
         "unit, period and n. A source line closes the figure. All three are page text, not pixels in the image.",
         "A reader who sees only the title still leaves with the result, and a long subtitle wraps instead of colliding with the plot.",
         "anatomy", final),
        ("Check it as a reader would", "In grayscale the focus still reads, through the outline and the bold value. The numbers are "
         "in the labels, so the figure works without hovering or a tooltip.",
         "Color is never the only carrier of meaning. This check takes ten seconds and catches most of what goes wrong.",
         "review", f'<div class="ex-grayscale">{gray}</div>'),
    ]


def figures_page(profile, documents_text):
    t, stages = figure_stages(profile)
    items = "".join(
        f'<li class="ex-stage"><div class="ex-stage-text"><p class="context ex-stage-step">Step {i}</p><h3>{esc(name)}</h3>'
        f'<p>{inline(what)}</p><p>{inline(why)}</p><p class="ex-rule">{rule_link(rule)}</p></div><div>{visual}</div></li>'
        for i, (name, what, why, rule, visual) in enumerate(stages, 1))
    body = (intro("From default to finished", "From default to finished, in six edits",
                  f"One set of numbers, {t['total']:,} support tickets in six categories, taken from a spreadsheet default to a "
                  "published figure. Each step is one rule from the data standard.",
                  [("Question", "Which category is biggest, and is login catching up?"), ("Chart", "Sorted horizontal bars"),
                   ("Helper", "figures.bar_chart and figures.figure")])
            + f'<section class="ex-wrap ex-section" aria-label="Six edits"><ol class="ex-stages">{items}</ol></section>'
            + next_steps("figures.html"))
    return "From default to finished", body, "One chart taken from a spreadsheet default to a finished figure, one rule at a time."


# One finding, four sizes ---------------------------------------------------------------------

def _wrap(text, size, width, factor=0.5):
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if len(trial) * size * factor > width and line:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + [line]


def _svg_text(x, y, body, *, size, fill, family, weight=None, anchor="start", tracking=None, numeric=False):
    weight_attr = f' font-weight="{weight}"' if weight else ""
    track = f' letter-spacing="{tracking:.2f}"' if tracking else ""
    nums = ' font-variant-numeric="tabular-nums"' if numeric else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" fill="{fill}" font-family="{esc(family)}" '
            f'font-size="{size}"{weight_attr}{track}{nums}>{esc(body)}</text>')


def _canvas_bars(theme, rows, *, x0, y0, width, height, label, value, stroke):
    """Sorted bars with names and values, sized for a fixed canvas (card or slide)."""
    rows = sorted(rows, key=lambda r: r[1], reverse=True)
    row = height / len(rows)
    bar = row * 0.56
    label_w = max(len(r[0]) for r in rows) * label * 0.56 + 24
    value_w = max(len(f"{r[1]:,}") for r in rows) * value * 0.62 + 20
    plot_w = width - label_w - value_w
    peak = max(v for _, v in rows)
    parts = []
    for i, (name, v) in enumerate(rows):
        y = y0 + i * row + (row - bar) / 2
        focal = name == TICKET_FOCUS
        w = plot_w * v / peak
        parts.append(_svg_text(x0 + label_w - 20, y + bar / 2 + label * 0.36, name, size=label, fill=theme["text-primary"], family=theme.body,
                               anchor="end", weight=600 if focal else None))
        outline = f' stroke="{theme["structure"]}" stroke-width="{stroke}"' if focal else ""
        parts.append(f'<rect x="{x0 + label_w:.1f}" y="{y:.1f}" width="{w:.1f}" height="{bar:.1f}" rx="3" '
                     f'fill="{theme["emphasis"] if focal else theme["series-primary"]}"{outline}/>')
        parts.append(_svg_text(x0 + label_w + w + 14, y + bar / 2 + value * 0.36, f"{v:,}", size=value, fill=theme["text-secondary"],
                               family=theme.body, weight=600 if focal else None, numeric=True))
    parts.append(f'<line x1="{x0 + label_w:.1f}" x2="{x0 + label_w:.1f}" y1="{y0:.1f}" y2="{y0 + height:.1f}" stroke="{theme["structure"]}" stroke-width="{stroke}"/>')
    return "".join(parts)


def card_svg(profile, t, id="card"):
    theme = figures.Theme(profile)
    c, ty = profile["media"]["card"], profile["typography"]
    display = figures.font_stack(ty["display"])
    w, h, m = c["width"], c["height"], c["margin"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{id}-t">'
             f'<title id="{id}-t">Figure card, {w} by {h}: {esc(t["title"])}</title>',
             f'<rect width="{w}" height="{h}" fill="{theme["canvas"]}"/>',
             _svg_text(m, m + c["wordmark"] * 0.75, "warm precision.", size=c["wordmark"], fill=theme["text-primary"], family=display,
                       weight=ty["wordmark"]["weight"], tracking=ty["wordmark"]["tracking"] * c["wordmark"])]
    y = m + c["wordmark"] + 120
    for line in _wrap(t["title"], c["title"], w - 2 * m, 0.46):
        parts.append(_svg_text(m, y, line, size=c["title"], fill=theme["text-primary"], family=display, weight=ty["display"]["weight"],
                               tracking=ty["display"]["tracking"] * c["title"]))
        y += c["title"] * 1.08
    y += 4
    for line in _wrap(t["subtitle"], c["body"], w - 2 * m, 0.52):
        parts.append(_svg_text(m, y, line, size=c["body"], fill=theme["text-secondary"], family=theme.body))
        y += c["body"] * 1.35
    source_y = h - m
    parts.append(_canvas_bars(theme, t["rows"], x0=m, y0=y + 24, width=w - 2 * m, height=source_y - c["caption"] - 40 - (y + 24),
                              label=c["label"], value=c["value"], stroke=profile["stroke"]["emphasis"]))
    parts.append(_svg_text(m, source_y, SOURCE, size=c["caption"], fill=theme["text-secondary"], family=theme.body))
    return "".join(parts) + "</svg>"


def slide_svg(profile, t, id="slide"):
    theme = figures.Theme(profile)
    s, ty = profile["media"]["slide"], profile["typography"]
    w, h, m = s["width"], s["height"], s["margin"]
    kicker = ty["kicker"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="{id}-t">'
             f'<title id="{id}-t">Slide, {w} by {h}: {esc(t["title"])}</title>',
             f'<rect width="{w}" height="{h}" fill="{theme["canvas"]}"/>',
             _svg_text(m, m, "SUPPORT · LAST 30 DAYS", size=s["kicker"], fill=theme["kicker"], family=theme.body,
                       weight=kicker["weight"], tracking=kicker["tracking"] * s["kicker"]),
             _svg_text(m, m + 64, t["title"], size=s["h1"], fill=theme["text-primary"], family=theme.body, weight=ty["heading"]["weight"],
                       tracking=ty["heading"]["tracking"] * s["h1"]),
             _svg_text(m, m + 112, t["subtitle"], size=s["caption"], fill=theme["text-secondary"], family=theme.body)]
    top, source_y = m + 160, h - m + 24
    parts.append(_canvas_bars(theme, t["rows"], x0=m, y0=top, width=w - 2 * m, height=source_y - s["caption"] - 32 - top,
                              label=s["body"], value=s["body"], stroke=profile["stroke"]["emphasis"]))
    parts.append(_svg_text(m, source_y, SOURCE, size=s["caption"], fill=theme["text-secondary"], family=theme.body))
    return "".join(parts) + "</svg>"


def media(profile, documents_text):
    theme = figures.Theme(profile)
    t = tickets()
    chart, card, slide = profile["media"]["chart"], profile["media"]["card"], profile["media"]["slide"]
    web = figures.figure(t["title"], t["subtitle"], figures.bar_chart(theme, t["rows"], id="md-web", focus=TICKET_FOCUS, title=t["title"]), SOURCE)
    phone = figures.figure(t["title"], t["subtitle"],
                           figures.bar_chart(theme, t["rows"], id="md-phone", focus=TICKET_FOCUS, width=340, title=t["title"]), SOURCE)
    panels = [
        ("Web page", f"720 px figure · {chart['label']} px labels", f'<div class="ex-canvas web">{web}</div>',
         "Title, subtitle and source are page text. The plot is drawn at 720 px with labels at the chart ramp. On a narrow "
         "screen it scrolls inside its own box instead of shrinking.", True),
        ("Phone", f"rebuilt at 340 px · labels stay {chart['label']} px", f'<div class="ex-phone">{phone}</div>',
         "The chart is drawn again at phone width, not scaled down. Bars get shorter; names and values stay readable.", False),
        ("Figure card", f"{card['width']} × {card['height']} · {card['title']} px title · {card['label']} px labels",
         f'<div class="ex-canvas">{card_svg(profile, t)}</div>',
         f"The card travels as an image, so the title is drawn in, in Newsreader for the one display line. The ramp is compressed "
         f"({card['caption']} to {card['title']} px) so it still reads when a feed shows it at phone width.", False),
        ("Slide", f"{slide['width']} × {slide['height']} · {slide['h1']} px title · {slide['body']} px labels",
         f'<div class="ex-canvas">{slide_svg(profile, t)}</div>',
         f"An assertion title instead of a topic, {slide['margin']} px safe margins, and labels at body size for the back of the room. "
         "Rebuilt for the slide, never a screenshot of the web chart.", True),
    ]
    wide_class = ' class="ex-wide"'
    items = "".join(f'<figure{wide_class if wide else ""}><p class="ex-media-label"><b>{esc(name)}</b><span>{esc(spec)}</span></p>{visual}'
                    f'<figcaption class="ex-why">{esc(why)}</figcaption></figure>' for name, spec, visual, why, wide in panels)
    kept = figures.table(["Stays the same", "Changes with the medium"], [
        ("The finding, word for word", "Type sizes, from the medium's ramp in tokens.json"),
        ("Sort order and the one focus", "Line length, and so where the title wraps"),
        ("Colors, by role", "Label column width and bar length"),
        ("The source line", "Whether the title is page text or drawn into the image")], label="What stays and what changes")
    body = (intro("One finding, four sizes", "One finding, four sizes",
                  "The finished figure from the previous example, recomposed for a web page, a phone, a social card and a slide. "
                  "The finding and its emphasis never change. The sizes come from each medium's ramp in the profile.",
                  [("Rule", "Recompose rather than shrink"), ("Sizes", "tokens.json → media"), ("Helpers", "figures.py and hand-placed SVG")])
            + f'<section class="ex-wrap ex-section" aria-label="Four media"><div class="ex-media">{items}</div></section>'
            + f'<section class="ex-wrap ex-section"><h2>What stays and what changes</h2>{kept}<p class="small">{rule_link("scale")} · '
              f'{rule_link("sizes")} · {rule_link("slides")}</p></section>'
            + next_steps("media.html"))
    return "One finding, four sizes", body, "The same figure recomposed for web, phone, a social card and a slide, from one set of tokens."


# Index ---------------------------------------------------------------------------------------

METHOD = [
    ("Name the reader's job", "“For this audience, make ___ clear so they can ___.”", "../handbook/PHILOSOPHY.html#1-meaning-before-styling", "Principles"),
    ("Pick the document", "What does the reader need to do? The answer picks one of ten shapes.", "../handbook/DOCUMENTS.html#choosing", "Documents"),
    ("Choose each figure", "Write the question first. The question picks the chart.", "../handbook/adapters-data.html#start-with-the-question", "Data"),
    ("Apply the profile", "Colors by role, sizes from the medium's ramp. Nothing typed by hand.", "../handbook/brand-kit.html", "Brand"),
    ("Edit the copy", "Finding first, numbers instead of adjectives, no em dashes.", "../handbook/VOICE.html#check-before-publishing", "Voice"),
    ("Review the output", "At its real size, in grayscale, and without the chart.", "../handbook/templates-REVIEW_RECEIPT.html", "Review receipt"),
]


def index(profile, documents_text):
    theme = figures.Theme(profile)
    s, t = season(), tickets()
    steps = "".join(f'<li><h3>{esc(name)}</h3><p>{esc(text)}</p><a href="{esc(href)}">{esc(label)}</a></li>' for name, text, href, label in METHOD)
    previews = {
        "explainer.html": _season_chart(theme, s, "pv-season"),
        "memo.html": figures.interval_plot(theme, RELEASES, id="pv-releases", focus="10:30 report", unit="¢", reference_label="No effect"),
        "figures.html": _draft_columns(theme, t["rows"], "pv-default") + figures.bar_chart(theme, t["rows"], id="pv-final", focus=TICKET_FOCUS),
        "media.html": card_svg(profile, t, id="pv-card") + slide_svg(profile, t, id="pv-slide"),
    }
    blurbs = {
        "explainer.html": ("Explainer page", f"Export sales are running {figures.fmt(s['ahead'], theme, kind='percent')} ahead",
                           "A one-page explanation for a planner, with six notes on why each part is built the way it is."),
        "memo.html": ("Decision memo", "Should the note go out after 10:30?",
                      "A yes-or-no decision, answered first, with every option on the same dimensions."),
        "figures.html": ("Figure method", "From default to finished",
                         "A spreadsheet chart becomes a published figure in six edits, one rule each."),
        "media.html": ("Recomposition", "One finding, four sizes",
                       "The same figure as a web chart, a phone chart, a 1200 px card and a slide."),
    }
    cards = "".join(
        f'<li class="ex-card"><div class="ex-card-preview{" pair" if slug in ("figures.html", "media.html") else ""}" aria-hidden="true">{previews[slug]}</div>'
        f'<div class="ex-card-body"><p class="context">{esc(kind)}</p><h3><a href="{slug}">{esc(title)}</a></h3><p>{esc(text)}</p></div></li>'
        for slug, (kind, title, text) in blurbs.items())
    body = (f'<header class="ex-wrap ex-intro"><p class="context">Examples</p><h1>What the kit produces, and why it looks that way</h1>'
            f'<p class="lead">Four finished pieces built from the same tokens and rules. Each shows its decisions beside it, with a link to '
            f'the rule that made each one. {esc(ILLUSTRATIVE)}</p></header>'
            f'<section class="ex-wrap ex-section" aria-labelledby="ex-method"><h2 id="ex-method">The method</h2>'
            f'<p class="specimen-intro">The same six decisions, in the same order, for every artifact. The examples below make each one visible.</p>'
            f'<ol class="ex-flow">{steps}</ol></section>'
            f'<section class="ex-wrap ex-section" aria-labelledby="ex-gallery"><h2 id="ex-gallery">The examples</h2><ul class="ex-gallery">{cards}</ul></section>'
            f'<section class="ex-wrap ex-section" aria-labelledby="ex-own"><h2 id="ex-own">Use it</h2>'
            f'<p class="reading">Every page here is generated by <code>scripts/examples.py</code> from the kit you download. Copy the profile and change '
            f'the tokens, and these pages rebuild in your colors.</p><p class="ex-next"><a class="button" href="../warm-precision-kit.zip" download>Download the kit</a>'
            f'<a class="button secondary" href="../handbook/profiles-warm-precision-INTEGRATION.html#making-your-own-profile">Make your own profile</a></p></section>')
    return "Examples", body, "Finished artifacts built with Warm Precision, with the method and the decisions behind them."


def pages(profile, documents_text):
    """slug → (title, body, description) for every example page."""
    builders = {"index.html": index, "explainer.html": explainer, "memo.html": memo, "figures.html": figures_page, "media.html": media}
    return {slug: build(profile, documents_text) for slug, build in builders.items()}
