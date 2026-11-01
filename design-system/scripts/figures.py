"""Warm Precision figures: number formatting, portable SVG charts and a matplotlib style.

Standard library only. Every color, size and format comes from the profile's tokens.json,
so a chart built here matches the handbook, a share card and a paper figure.

    import json, figures
    theme = figures.Theme(json.load(open("design-system/profiles/warm-precision/tokens.json")))
    svg = figures.bar_chart(theme, [("Corn", 41.2), ("Soy", 33.0)], unit="%", decimals=1, id="crops")
    html = figures.figure("Corn leads", "Share of acres, 2026, %", svg, "Source: USDA NASS")

Titles, subtitles and source lines live outside the SVG as real text (see `figure`). The SVG
carries only data and its labels, so nothing inside the image can collide with a caption.
"""

import hashlib
import html
import math

GENERIC_FAMILIES = {"serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui",
                    "ui-serif", "ui-sans-serif", "ui-monospace", "ui-rounded", "math", "emoji"}


def font_stack(spec):
    family = spec["family"]
    first = family if family in GENERIC_FAMILIES else f'"{family}"'
    return f'{first}, {spec["fallback"]}'


def contrast(foreground, background):
    """WCAG 2.x contrast ratio between two #RRGGBB colors."""
    def lum(value):
        channels = [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        return sum(w * (c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4)
                   for w, c in zip((.2126, .7152, .0722), channels))
    a, b = sorted((lum(foreground), lum(background)))
    return (b + .05) / (a + .05)


def _rgb(value):
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


def _hex(channels):
    return "#" + "".join(f"{max(0, min(255, round(c))):02X}" for c in channels)


def _lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def ramp(theme, t, *, diverging=False):
    """A color for a normalized value t in [0, 1]. Sequential canvas->structure, or diverging copper<-well->slate."""
    canvas, structure = _rgb(theme["canvas"]), _rgb(theme["structure"])
    if not diverging:
        return _hex(_lerp(canvas, structure, 0.12 + 0.88 * max(0.0, min(1.0, t))))
    mid, low, high = _rgb(theme["well"]), _rgb(theme["emphasis-text"]), _rgb(theme["series-primary"])
    t = max(0.0, min(1.0, t))
    return _hex(_lerp(low, mid, t / 0.5)) if t < 0.5 else _hex(_lerp(mid, high, (t - 0.5) / 0.5))


def on(theme, background):
    """Readable text color (primary ink or ivory) for a solid background fill."""
    return theme["on-structure"] if contrast(theme["on-structure"], background) >= contrast(theme["text-primary"], background) else theme["text-primary"]


# Segment palette for part-to-whole, ordered for adjacent contrast. Fills only; keep to five.
SEGMENT_ROLES = ("series-primary", "series-secondary", "emphasis-text", "context", "text-secondary")


class Theme:
    def __init__(self, profile):
        self.profile = profile
        self.colors = {role: profile["colors"][name] for role, name in profile["roles"].items()}
        self.chart = profile["media"]["chart"]
        self.data = profile["data"]
        self.body = font_stack(profile["typography"]["body"])
        self.code = font_stack(profile["typography"]["code"])
        self.rule_opacity = profile["stroke"]["decorativeOpacity"]
        self.track_opacity = profile["stroke"]["trackOpacity"]

    def __getitem__(self, role):
        return self.colors[role]


# Numbers ---------------------------------------------------------------------------------

def fmt(value, theme=None, *, decimals=0, unit="", kind="number", sign=False, prefix=""):
    """Format one number for display.

    kind: "number", "percent" (12.3%), "pp" (percentage points, always signed),
    "currency" (the profile's currency symbol as a prefix, after any sign: −$3.20).
    unit is appended as written, so pass " t" for a spaced word unit and "¢/bu" for a symbol.
    """
    data = theme.data if theme else {"thousands": ",", "decimal": ".", "minus": "\u2212", "missing": "n/a", "currency": "$"}
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return data["missing"]
    if kind == "pp":
        sign, unit = True, unit or " pp"
    if kind == "percent":
        unit = unit or "%"
    if kind == "currency":
        prefix = prefix or data.get("currency", "$")
    text = f"{abs(value):,.{decimals}f}".replace(",", "\x00").replace(".", data["decimal"]).replace("\x00", data["thousands"])
    if value < 0 and float(text.replace(data["thousands"], "").replace(data["decimal"], ".")) != 0:
        lead = data["minus"]
    elif sign and value > 0:
        lead = "+"
    else:
        lead = ""
    return f"{lead}{prefix}{text}{unit}"


def fmt_range(low, high, theme=None, **options):
    separator = theme.data["range"] if theme else "\u2013"
    return f"{fmt(low, theme, **options)}{separator}{fmt(high, theme, **options)}"


# SVG building blocks ---------------------------------------------------------------------

def _esc(value):
    return html.escape(str(value), quote=True)


def _text(theme, x, y, body, *, size=None, anchor="start", color="text-primary", weight=None, mono=False):
    size = size or theme.chart["label"]
    family = theme.code if mono else theme.body
    weight_attr = f' font-weight="{weight}"' if weight else ""
    numeric = ' font-variant-numeric="tabular-nums"' if mono else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" fill="{theme[color]}" font-family="{_esc(family)}" '
            f'font-size="{size}"{weight_attr}{numeric}>{_esc(body)}</text>')


def _open(theme, width, height, id, title, desc):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" class="wp-chart" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
            f'role="img" aria-labelledby="{id}-t {id}-d"><title id="{id}-t">{_esc(title)}</title><desc id="{id}-d">{_esc(desc)}</desc>')


def _median(values):
    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2


def _line_path(values, x_at, y_at):
    """An SVG path through the values; None breaks the line instead of bridging the gap."""
    path, pen = [], "M"
    for i, v in enumerate(values):
        if v is None:
            pen = "M"
            continue
        path.append(f"{pen}{x_at(i):.1f},{y_at(v):.1f}")
        pen = "L"
    return " ".join(path)


def _label_width(labels, size):
    return max(len(str(label)) for label in labels) * size * 0.56 + 12


def _nice_ticks(low, high, count=4):
    if high == low:
        high = low + 1
    raw = (high - low) / count
    magnitude = 10 ** math.floor(math.log10(raw))
    step = min((m * magnitude for m in (1, 2, 2.5, 5, 10) if m * magnitude >= raw), default=raw)
    start = math.floor(low / step) * step
    ticks, value = [], start
    while value <= high + step * 1e-9:
        ticks.append(round(value, 10))
        value += step
    if ticks[-1] < high:
        ticks.append(round(ticks[-1] + step, 10))
    return ticks


# Charts ----------------------------------------------------------------------------------

def bar_chart(theme, rows, *, id, focus=None, sort=True, width=720, decimals=0, unit="", kind="number",
              title="Bar chart", motion=False):
    """Horizontal bars with direct value labels. rows: [(label, value)]. Zero baseline always."""
    rows = sorted(rows, key=lambda r: r[1], reverse=True) if sort else list(rows)
    size, row, bar = theme.chart["label"], 44, 24
    label_w = _label_width([r[0] for r in rows], size)
    value_w = max(len(fmt(v, theme, decimals=decimals, unit=unit, kind=kind)) for _, v in rows) * size * 0.62 + 16
    plot_w = width - label_w - value_w
    peak = max(max(v for _, v in rows), 0) or 1
    height = row * len(rows)
    parts = [_open(theme, width, height, id, title,
                   "; ".join(f"{l}: {fmt(v, theme, decimals=decimals, unit=unit, kind=kind)}" for l, v in rows))]
    for i, (label, value) in enumerate(rows):
        y = i * row + (row - bar) / 2
        w = max(value, 0) / peak * plot_w
        focal = label == focus
        fill = theme["emphasis"] if focal else theme["series-primary"]
        stroke = f' stroke="{theme["structure"]}" stroke-width="{theme.chart["stroke"]}"' if focal else ""
        rise = f' data-rise data-step="{min(i + 1, 8)}"' if motion else ""
        parts.append(_text(theme, label_w - 12, y + bar / 2 + size * 0.36, label, anchor="end"))
        parts.append(f'<rect x="{label_w:.1f}" y="{y:.1f}" width="{w:.1f}" height="{bar}" rx="2" fill="{fill}"{stroke}{rise}/>')
        parts.append(_text(theme, label_w + w + 8, y + bar / 2 + size * 0.34, fmt(value, theme, decimals=decimals, unit=unit, kind=kind),
                           size=theme.chart["caption"], color="text-secondary", mono=True, weight=600 if focal else None))
    parts.append(f'<line x1="{label_w:.1f}" x2="{label_w:.1f}" y1="0" y2="{height}" stroke="{theme["structure"]}" stroke-width="{theme.chart["stroke"]}"/>')
    return "".join(parts) + "</svg>"


def line_chart(theme, x_labels, series, *, id, focus, width=720, height=340, decimals=0, unit="", kind="number",
               y_min=None, y_max=None, title="Line chart", mark_last=True, motion=False, tick_every=1):
    """Lines with end labels. The focus series is Blue Slate; every other series is context.

    series: {name: [values]} aligned to x_labels. None leaves a gap.
    """
    size, caption = theme.chart["label"], theme.chart["caption"]
    values = [v for s in series.values() for v in s if v is not None]
    low = min(values) if y_min is None else y_min
    high = max(values) if y_max is None else y_max
    ticks = _nice_ticks(low, high)
    low, high = ticks[0], ticks[-1]
    tick_text = [fmt(t, theme, decimals=decimals, unit=unit, kind=kind) for t in ticks]
    left = max(len(t) for t in tick_text) * caption * 0.62 + 12
    right = _label_width(series.keys(), size) + 12
    top, bottom = 12, 36
    plot_w, plot_h = width - left - right, height - top - bottom
    x_at = lambda i: left + (plot_w * i / max(len(x_labels) - 1, 1))
    y_at = lambda v: top + plot_h * (1 - (v - low) / (high - low))
    desc = "; ".join(f"{name}: " + ", ".join(f"{x} {fmt(v, theme, decimals=decimals, unit=unit, kind=kind)}"
                                            for x, v in zip(x_labels, vals) if v is not None) for name, vals in series.items())
    parts = [_open(theme, width, height, id, title, desc)]
    for t, label in zip(ticks, tick_text):
        y = y_at(t)
        parts.append(f'<line x1="{left:.1f}" x2="{left + plot_w:.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{theme["structure"]}" stroke-opacity="{theme.rule_opacity}" stroke-width="1"/>')
        parts.append(_text(theme, left - 8, y + caption * 0.34, label, size=caption, anchor="end", color="text-secondary", mono=True))
    for i, label in enumerate(x_labels):
        last_far = i == len(x_labels) - 1 and (len(x_labels) - 1) % tick_every >= tick_every / 2
        if i % tick_every == 0 or last_far:
            parts.append(_text(theme, x_at(i), height - 10, label, size=caption, anchor="middle", color="text-secondary"))
    ordered = [name for name in series if name != focus] + [focus]
    end_labels = []
    for step, name in enumerate(ordered):
        vals = series[name]
        focal = name == focus
        color = theme["series-primary"] if focal else theme["series-context"]
        width_px = theme.chart["markStroke"] if focal else theme.chart["stroke"]
        draw = f' pathLength="1" data-draw data-step="{min(step + 1, 8)}"' if motion else ""
        parts.append(f'<path d="{_line_path(vals, x_at, y_at)}" fill="none" stroke="{color}" stroke-width="{width_px}" stroke-linejoin="round" stroke-linecap="round"{draw}/>')
        last = max(i for i, v in enumerate(vals) if v is not None)
        if last < len(x_labels) - 1:  # series ends early: label it at its own end, not in the gutter
            parts.append(_text(theme, x_at(last) + 14, y_at(vals[last]) + size * 0.34, name,
                               color="text-primary" if focal else "text-secondary", weight=600 if focal else None))
            if focal and mark_last:
                parts.append(f'<circle cx="{x_at(last):.1f}" cy="{y_at(vals[last]):.1f}" r="6" fill="{theme["emphasis"]}" stroke="{theme["structure"]}" stroke-width="{theme.chart["stroke"]}"/>')
            continue
        end_labels.append([y_at(vals[last]), name, focal, x_at(last), vals[last]])
    end_labels.sort()
    for i in range(1, len(end_labels)):  # keep end labels from overlapping
        end_labels[i][0] = max(end_labels[i][0], end_labels[i - 1][0] + size * 1.15)
    for y, name, focal, x, value in end_labels:
        parts.append(_text(theme, left + plot_w + 10, y + size * 0.34, name, color="text-primary" if focal else "text-secondary",
                           weight=600 if focal else None))
        if focal and mark_last:
            parts.append(f'<circle cx="{x:.1f}" cy="{y_at(value):.1f}" r="6" fill="{theme["emphasis"]}" stroke="{theme["structure"]}" stroke-width="{theme.chart["stroke"]}"/>')
    return "".join(parts) + "</svg>"


def interval_plot(theme, rows, *, id, reference=0, width=720, decimals=1, unit="", kind="number", focus=None,
                  title="Interval plot", reference_label=None):
    """Estimates with intervals. rows: [(label, estimate, low, high)]. A reference line marks no effect."""
    size, caption, row = theme.chart["label"], theme.chart["caption"], 44
    label_w = _label_width([r[0] for r in rows], size)
    lows = [r[2] for r in rows] + [reference]
    highs = [r[3] for r in rows] + [reference]
    ticks = _nice_ticks(min(lows), max(highs))
    low, high = ticks[0], ticks[-1]
    plot_w = width - label_w - 24
    height = row * len(rows) + 40
    x_at = lambda v: label_w + plot_w * (v - low) / (high - low)
    desc = "; ".join(f"{l}: {fmt(e, theme, decimals=decimals, unit=unit, kind=kind)} "
                     f"({fmt_range(a, b, theme, decimals=decimals, unit=unit, kind=kind)})" for l, e, a, b in rows)
    parts = [_open(theme, width, height, id, title, desc)]
    for t in ticks:
        x = x_at(t)
        parts.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="0" y2="{row * len(rows):.1f}" stroke="{theme["structure"]}" stroke-opacity="{theme.rule_opacity}"/>')
        parts.append(_text(theme, x, height - 12, fmt(t, theme, decimals=0 if float(t).is_integer() else decimals, unit=unit, kind=kind),
                           size=caption, anchor="middle", color="text-secondary", mono=True))
    ref = x_at(reference)
    parts.append(f'<line x1="{ref:.1f}" x2="{ref:.1f}" y1="0" y2="{row * len(rows):.1f}" stroke="{theme["structure"]}" stroke-width="{theme.chart["stroke"]}" stroke-dasharray="4 4"/>')
    if reference_label:
        parts.append(_text(theme, ref + 6, 12, reference_label, size=caption, color="text-secondary"))
    for i, (label, estimate, a, b) in enumerate(rows):
        y = i * row + row / 2 + 4
        focal = label == focus
        parts.append(_text(theme, label_w - 12, y + size * 0.34, label, anchor="end"))
        parts.append(f'<line x1="{x_at(a):.1f}" x2="{x_at(b):.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{theme["series-primary"]}" stroke-width="{theme.chart["markStroke"]}" stroke-linecap="round"/>')
        fill = theme["emphasis"] if focal else theme["series-primary"]
        parts.append(f'<circle cx="{x_at(estimate):.1f}" cy="{y:.1f}" r="7" fill="{fill}" stroke="{theme["structure"]}" stroke-width="{theme.chart["stroke"]}"/>')
    return "".join(parts) + "</svg>"


# More charts: scatter, distribution, matrix, small multiples, bands, part-to-whole, tiles -

def _axes(theme, parts, *, left, top, plot_w, plot_h, xticks, yticks, x_at, y_at,
          x_decimals, y_decimals, x_unit, y_unit, x_kind, y_kind, x_label, y_label):
    """Shared x/y axis furniture: gridlines, tick labels, axis lines and axis titles."""
    caption = theme.chart["caption"]
    bottom = top + plot_h
    for t in yticks:
        y = y_at(t)
        parts.append(f'<line x1="{left:.1f}" x2="{left + plot_w:.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{theme["structure"]}" stroke-opacity="{theme.rule_opacity}" stroke-width="1"/>')
        parts.append(_text(theme, left - 8, y + caption * 0.34, fmt(t, theme, decimals=y_decimals, unit=y_unit, kind=y_kind),
                           size=caption, anchor="end", color="text-secondary", mono=True))
    for t in xticks:
        x = x_at(t)
        parts.append(_text(theme, x, bottom + caption * 1.4, fmt(t, theme, decimals=x_decimals, unit=x_unit, kind=x_kind),
                           size=caption, anchor="middle", color="text-secondary", mono=True))
    parts.append(f'<line x1="{left:.1f}" x2="{left + plot_w:.1f}" y1="{bottom:.1f}" y2="{bottom:.1f}" stroke="{theme["structure"]}" stroke-width="{theme.chart["stroke"]}"/>')
    if x_label:
        parts.append(_text(theme, left + plot_w / 2, bottom + caption * 3.1, x_label, size=caption, anchor="middle", color="text-secondary"))
    if y_label:
        yx, yy = left - _label_width([fmt(t, theme, decimals=y_decimals, unit=y_unit, kind=y_kind) for t in yticks], caption) - 6, top + plot_h / 2
        parts.append(f'<text x="{yx:.1f}" y="{yy:.1f}" text-anchor="middle" transform="rotate(-90 {yx:.1f} {yy:.1f})" '
                     f'fill="{theme["text-secondary"]}" font-family="{_esc(theme.body)}" font-size="{caption}">{_esc(y_label)}</text>')


def scatter_plot(theme, points, *, id, x_label="", y_label="", width=720, height=440,
                 x_decimals=0, y_decimals=0, x_unit="", y_unit="", x_kind="number", y_kind="number",
                 identity=False, vline=None, hline=None, vline_label=None, hline_label=None,
                 focus=None, dense=False, x_min=None, x_max=None, y_min=None, y_max=None, title="Scatter plot"):
    """Points on two numeric axes. points: [(x, y)] or [(x, y, label)]. Highlight one series grey-on-grey.

    dense: small low-opacity marks for hundreds of points. identity: a y=x reference. vline/hline: threshold rules.
    """
    size, caption = theme.chart["label"], theme.chart["caption"]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    span = [min(xs + ys), max(xs + ys)]
    ex = ([vline] if vline is not None else []) + (span if identity else [])
    ey = ([hline] if hline is not None else []) + (span if identity else [])
    xticks = _nice_ticks(min(xs + ex) if x_min is None else x_min, max(xs + ex) if x_max is None else x_max)
    yticks = _nice_ticks(min(ys + ey) if y_min is None else y_min, max(ys + ey) if y_max is None else y_max)
    x0, x1, y0, y1 = xticks[0], xticks[-1], yticks[0], yticks[-1]
    labelled = any(len(p) > 2 and p[2] for p in points)
    left = _label_width([fmt(t, theme, decimals=y_decimals, unit=y_unit, kind=y_kind) for t in yticks], caption) + (caption + 6 if y_label else 0) + 10
    bottom_pad = caption * (3.4 if x_label else 1.8)
    top, right = 12, (14 if not labelled else 70)
    plot_w, plot_h = width - left - right, height - top - bottom_pad
    x_at = lambda v: left + plot_w * (v - x0) / (x1 - x0)
    y_at = lambda v: top + plot_h * (1 - (v - y0) / (y1 - y0))
    desc = f"{len(points)} points" + (f"; x {x_label}" if x_label else "") + (f"; y {y_label}" if y_label else "")
    parts = [_open(theme, width, height, id, title, desc)]
    _axes(theme, parts, left=left, top=top, plot_w=plot_w, plot_h=plot_h, xticks=xticks, yticks=yticks, x_at=x_at, y_at=y_at,
          x_decimals=x_decimals, y_decimals=y_decimals, x_unit=x_unit, y_unit=y_unit, x_kind=x_kind, y_kind=y_kind, x_label=x_label, y_label=y_label)
    if identity:
        lo, hi = max(x0, y0), min(x1, y1)
        parts.append(f'<line x1="{x_at(lo):.1f}" y1="{y_at(lo):.1f}" x2="{x_at(hi):.1f}" y2="{y_at(hi):.1f}" stroke="{theme["context"]}" stroke-width="{theme.chart["stroke"]}" stroke-dasharray="6 5"/>')
    for v, lab, horiz in ((vline, vline_label, False), (hline, hline_label, True)):
        if v is None:
            continue
        if horiz:
            parts.append(f'<line x1="{left:.1f}" x2="{left + plot_w:.1f}" y1="{y_at(v):.1f}" y2="{y_at(v):.1f}" stroke="{theme["structure"]}" stroke-width="{theme.chart["stroke"]}" stroke-dasharray="4 4"/>')
            if lab:
                parts.append(_text(theme, left + plot_w, y_at(v) - 6, lab, size=caption, anchor="end", color="text-secondary"))
        else:
            parts.append(f'<line x1="{x_at(v):.1f}" x2="{x_at(v):.1f}" y1="{top:.1f}" y2="{top + plot_h:.1f}" stroke="{theme["structure"]}" stroke-width="{theme.chart["stroke"]}" stroke-dasharray="4 4"/>')
            if lab:
                parts.append(_text(theme, x_at(v) + 6, top + caption, lab, size=caption, color="text-secondary"))
    r = 3 if dense else 5
    opacity = 0.5 if dense else 0.85
    focal = []
    for p in points:
        x, y = p[0], p[1]
        label = p[2] if len(p) > 2 else None
        if label and label == focus:
            focal.append((x, y, label))
            continue
        parts.append(f'<circle cx="{x_at(x):.1f}" cy="{y_at(y):.1f}" r="{r}" fill="{theme["series-primary"] if (focus is None and not labelled) else theme["context"]}" fill-opacity="{opacity}"/>')
        if label and not dense and focus is None:
            parts.append(_text(theme, x_at(x) + r + 4, y_at(y) + caption * 0.34, label, size=caption, color="text-secondary"))
    for x, y, label in focal:
        parts.append(f'<circle cx="{x_at(x):.1f}" cy="{y_at(y):.1f}" r="{r + 2}" fill="{theme["emphasis"]}" stroke="{theme["structure"]}" stroke-width="{theme.chart["stroke"]}"/>')
        parts.append(_text(theme, x_at(x) + r + 6, y_at(y) + caption * 0.34, label, size=caption, color="text-primary", weight=600))
    return "".join(parts) + "</svg>"


def strip_plot(theme, groups, *, id, value_label="", width=720, row=86, decimals=1, unit="", kind="number",
               focus=None, x_min=None, x_max=None, title="Strip plot"):
    """One row of jittered dots per group, with the group median marked. groups: {name: [values]}.

    Jitter is deterministic (index-based), so the figure rebuilds identically.
    """
    size, caption = theme.chart["label"], theme.chart["caption"]
    names = list(groups)
    allv = [v for vals in groups.values() for v in vals]
    xticks = _nice_ticks(min(allv) if x_min is None else x_min, max(allv) if x_max is None else x_max)
    x0, x1 = xticks[0], xticks[-1]
    label_w = _label_width(names, size)
    right = 16
    plot_w = width - label_w - right
    top = caption * 1.8  # room for the top row's median label
    height = top + row * len(names) + caption * (3.0 if value_label else 1.6)
    x_at = lambda v: label_w + plot_w * (v - x0) / (x1 - x0)
    desc = "; ".join(f"{n}: n={len(groups[n])}, median {fmt(_median(groups[n]), theme, decimals=decimals, unit=unit, kind=kind)}" for n in names)
    parts = [_open(theme, width, height, id, title, desc)]
    for t in xticks:
        x = x_at(t)
        parts.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top:.1f}" y2="{top + row * len(names):.1f}" stroke="{theme["structure"]}" stroke-opacity="{theme.rule_opacity}"/>')
        parts.append(_text(theme, x, top + row * len(names) + caption * 1.4, fmt(t, theme, decimals=decimals, unit=unit, kind=kind), size=caption, anchor="middle", color="text-secondary", mono=True))
    if value_label:
        parts.append(_text(theme, label_w + plot_w / 2, height - 2, value_label, size=caption, anchor="middle", color="text-secondary"))
    band = row * 0.52
    for gi, name in enumerate(names):
        cy = top + gi * row + row / 2
        focal = name == focus
        vals = groups[name]
        parts.append(_text(theme, label_w - 12, cy + size * 0.34, name, anchor="end", weight=600 if focal else None))
        color = theme["emphasis"] if focal else theme["series-primary"]
        for i, v in enumerate(vals):
            jitter = ((i * 37 % 11) / 10 - 0.5) * band
            parts.append(f'<circle cx="{x_at(v):.1f}" cy="{cy + jitter:.1f}" r="4" fill="{color}" fill-opacity="0.55"/>')
        med = _median(vals)
        parts.append(f'<line x1="{x_at(med):.1f}" x2="{x_at(med):.1f}" y1="{cy - band / 2 - 6:.1f}" y2="{cy + band / 2 + 6:.1f}" stroke="{theme["structure"]}" stroke-width="{theme.chart["markStroke"]}"/>')
        parts.append(_text(theme, x_at(med), cy - band / 2 - 10, fmt(med, theme, decimals=decimals, unit=unit, kind=kind), size=caption, anchor="middle", color="text-secondary", mono=True))
    return "".join(parts) + "</svg>"


def histogram(theme, values, *, id, bins=12, value_label="", width=720, height=360, decimals=0, unit="", kind="number",
              reference=None, reference_label=None, title="Histogram"):
    """A distribution of one variable. Counts per equal-width bin, zero baseline, optional reference line."""
    size, caption = theme.chart["label"], theme.chart["caption"]
    lo, hi = min(values), max(values)
    step = (hi - lo) / bins or 1
    edges = [lo + i * step for i in range(bins + 1)]
    counts = [0] * bins
    for v in values:
        idx = min(int((v - lo) / step), bins - 1)
        counts[idx] += 1
    yticks = _nice_ticks(0, max(counts))
    left = _label_width([str(int(t)) for t in yticks], caption) + 10
    top, right, bottom = 12, 14, caption * (3.2 if value_label else 1.8)
    plot_w, plot_h = width - left - right, height - top - bottom
    x_at = lambda v: left + plot_w * (v - edges[0]) / (edges[-1] - edges[0])
    y_at = lambda c: top + plot_h * (1 - c / yticks[-1])
    parts = [_open(theme, width, height, id, title, f"{len(values)} values in {bins} bins")]
    for t in yticks:
        y = y_at(t)
        parts.append(f'<line x1="{left:.1f}" x2="{left + plot_w:.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{theme["structure"]}" stroke-opacity="{theme.rule_opacity}"/>')
        parts.append(_text(theme, left - 8, y + caption * 0.34, str(int(t)), size=caption, anchor="end", color="text-secondary", mono=True))
    for i, c in enumerate(counts):
        x, w = x_at(edges[i]), x_at(edges[i + 1]) - x_at(edges[i])
        parts.append(f'<rect x="{x + 1:.1f}" y="{y_at(c):.1f}" width="{w - 2:.1f}" height="{top + plot_h - y_at(c):.1f}" fill="{theme["series-primary"]}"/>')
    for t in (edges[0], edges[bins // 2], edges[-1]):
        parts.append(_text(theme, x_at(t), top + plot_h + caption * 1.4, fmt(t, theme, decimals=decimals, unit=unit, kind=kind), size=caption, anchor="middle", color="text-secondary", mono=True))
    if reference is not None:
        parts.append(f'<line x1="{x_at(reference):.1f}" x2="{x_at(reference):.1f}" y1="{top:.1f}" y2="{top + plot_h:.1f}" stroke="{theme["emphasis-text"]}" stroke-width="{theme.chart["markStroke"]}" stroke-dasharray="5 4"/>')
        if reference_label:
            parts.append(_text(theme, x_at(reference) + 6, top + caption, reference_label, size=caption, color="emphasis-text", weight=600))
    parts.append(f'<line x1="{left:.1f}" x2="{left + plot_w:.1f}" y1="{top + plot_h:.1f}" y2="{top + plot_h:.1f}" stroke="{theme["structure"]}" stroke-width="{theme.chart["stroke"]}"/>')
    if value_label:
        parts.append(_text(theme, left + plot_w / 2, height - 2, value_label, size=caption, anchor="middle", color="text-secondary"))
    return "".join(parts) + "</svg>"


def heatmap(theme, row_labels, col_labels, values, *, id, diverging=False, decimals=1, unit="", kind="number",
            width=720, cell=48, annotate=True, vmin=None, vmax=None, legend_label="", title="Heatmap"):
    """A matrix of values, one cell per (row, col). values: [[...]] row-major. Diverging scales center on zero."""
    size, caption = theme.chart["label"], theme.chart["caption"]
    flat = [v for rowv in values for v in rowv if v is not None]
    hi = max(abs(v) for v in flat) if vmax is None else vmax
    lo = -hi if diverging else (min(flat) if vmin is None else vmin)
    hi = hi if diverging else (max(flat) if vmax is None else vmax)
    norm = lambda v: 0.5 if hi == lo else (v - lo) / (hi - lo)
    label_w = _label_width(row_labels, caption)
    top = caption * 2.2
    grid_w = len(col_labels) * cell
    legend_h = caption * 4.4
    width = max(width, label_w + grid_w + 16)
    height = top + len(row_labels) * cell + legend_h
    parts = [_open(theme, width, height, id, title, f"{len(row_labels)} by {len(col_labels)} matrix")]
    for c, cl in enumerate(col_labels):
        parts.append(_text(theme, label_w + c * cell + cell / 2, top - caption * 0.6, cl, size=caption, anchor="middle", color="text-secondary"))
    for r, rl in enumerate(row_labels):
        cy = top + r * cell
        parts.append(_text(theme, label_w - 8, cy + cell / 2 + caption * 0.34, rl, size=caption, anchor="end", color="text-primary"))
        for c in range(len(col_labels)):
            v = values[r][c]
            x = label_w + c * cell
            if v is None:
                parts.append(f'<rect x="{x:.1f}" y="{cy:.1f}" width="{cell}" height="{cell}" fill="{theme["well"]}" stroke="{theme["canvas"]}" stroke-width="2"/>')
                continue
            bg = ramp(theme, norm(v), diverging=diverging)
            parts.append(f'<rect x="{x:.1f}" y="{cy:.1f}" width="{cell}" height="{cell}" fill="{bg}" stroke="{theme["canvas"]}" stroke-width="2"/>')
            if annotate:
                parts.append(_text(theme, x + cell / 2, cy + cell / 2 + caption * 0.34, fmt(v, theme, decimals=decimals, unit=unit, kind=kind),
                                   size=caption, anchor="middle", mono=True).replace(f'fill="{theme["text-primary"]}"', f'fill="{on(theme, bg)}"'))
    # legend ramp
    ly = top + len(row_labels) * cell + caption * 1.4
    steps = 32
    seg = grid_w / steps
    for i in range(steps):
        parts.append(f'<rect x="{label_w + i * seg:.1f}" y="{ly:.1f}" width="{seg + 1:.1f}" height="{caption:.1f}" fill="{ramp(theme, i / (steps - 1), diverging=diverging)}"/>')
    parts.append(_text(theme, label_w, ly + caption * 2.1, fmt(lo, theme, decimals=decimals, unit=unit, kind=kind), size=caption, color="text-secondary", mono=True))
    parts.append(_text(theme, label_w + grid_w, ly + caption * 2.1, fmt(hi, theme, decimals=decimals, unit=unit, kind=kind), size=caption, anchor="end", color="text-secondary", mono=True))
    if legend_label:
        parts.append(_text(theme, label_w + grid_w / 2, ly + caption * 2.1, legend_label, size=caption, anchor="middle", color="text-secondary"))
    return "".join(parts) + "</svg>"


def small_multiples(theme, x_labels, panels, *, id, columns=3, decimals=0, unit="", kind="number",
                    y_min=None, y_max=None, width=720, panel_h=132, gap=20, title="Small multiples"):
    """A grid of mini line charts on one shared y-scale. panels: [(name, [values])] aligned to x_labels.

    Each panel marks its own last value. Shared scale is the honest default for comparison.
    """
    size, caption = theme.chart["label"], theme.chart["caption"]
    allv = [v for _, vals in panels for v in vals if v is not None]
    ticks = _nice_ticks(min(allv) if y_min is None else y_min, max(allv) if y_max is None else y_max, count=3)
    lo, hi = ticks[0], ticks[-1]
    rows = (len(panels) + columns - 1) // columns
    panel_w = (width - gap * (columns - 1)) / columns
    left = _label_width([fmt(t, theme, decimals=decimals, unit=unit, kind=kind) for t in ticks], caption) + 6
    head, foot = caption * 1.8, caption * 1.6
    plot_h = panel_h - head - foot
    height = rows * panel_h + (rows - 1) * gap
    parts = [_open(theme, width, height, id, title, "; ".join(n for n, _ in panels))]
    for idx, (name, vals) in enumerate(panels):
        r, c = divmod(idx, columns)
        ox, oy = c * (panel_w + gap), r * (panel_h + gap)
        px0, pw = ox + left, panel_w - left
        py0 = oy + head
        x_at = lambda i: px0 + pw * i / max(len(x_labels) - 1, 1)
        y_at = lambda v: py0 + plot_h * (1 - (v - lo) / (hi - lo))
        parts.append(_text(theme, ox, oy + caption, name, size=caption, color="text-primary", weight=600))
        for t in (lo, hi):
            parts.append(f'<line x1="{px0:.1f}" x2="{ox + panel_w:.1f}" y1="{y_at(t):.1f}" y2="{y_at(t):.1f}" stroke="{theme["structure"]}" stroke-opacity="{theme.rule_opacity}"/>')
            parts.append(_text(theme, px0 - 6, y_at(t) + caption * 0.34, fmt(t, theme, decimals=decimals, unit=unit, kind=kind), size=caption, anchor="end", color="text-secondary", mono=True))
        parts.append(f'<path d="{_line_path(vals, x_at, y_at)}" fill="none" stroke="{theme["series-primary"]}" stroke-width="{theme.chart["stroke"]}" stroke-linejoin="round" stroke-linecap="round"/>')
        last = max(i for i, v in enumerate(vals) if v is not None)
        parts.append(f'<circle cx="{x_at(last):.1f}" cy="{y_at(vals[last]):.1f}" r="4" fill="{theme["emphasis"]}" stroke="{theme["structure"]}" stroke-width="{theme.chart["stroke"]}"/>')
        parts.append(_text(theme, ox + panel_w, oy + caption, fmt(vals[last], theme, decimals=decimals, unit=unit, kind=kind), size=caption, anchor="end", color="text-secondary", mono=True))
        parts.append(_text(theme, px0, oy + panel_h - 2, str(x_labels[0]), size=caption, color="text-secondary"))
        parts.append(_text(theme, ox + panel_w, oy + panel_h - 2, str(x_labels[-1]), size=caption, anchor="end", color="text-secondary"))
    return "".join(parts) + "</svg>"


def band_chart(theme, x_labels, median, bands, *, id, width=720, height=360, decimals=0, unit="", kind="number",
               y_min=None, y_max=None, reference=None, reference_label=None, band_labels=None,
               point=None, tick_every=1, title="Range chart"):
    """A median line inside one or more interval ribbons. bands: [(low[], high[])], widest first.

    Use for percentile fans and bootstrap bands. point: (index, value, label) to mark one value.
    """
    size, caption = theme.chart["label"], theme.chart["caption"]
    allv = [v for lo, hi in bands for seq in (lo, hi) for v in seq if v is not None] + [v for v in median if v is not None]
    if reference is not None:
        allv.append(reference)
    ticks = _nice_ticks(min(allv) if y_min is None else y_min, max(allv) if y_max is None else y_max)
    lo_t, hi_t = ticks[0], ticks[-1]
    left = _label_width([fmt(t, theme, decimals=decimals, unit=unit, kind=kind) for t in ticks], caption) + 10
    top, right, bottom = 12, 16, caption * 1.8
    plot_w, plot_h = width - left - right, height - top - bottom
    x_at = lambda i: left + plot_w * i / max(len(x_labels) - 1, 1)
    y_at = lambda v: top + plot_h * (1 - (v - lo_t) / (hi_t - lo_t))
    parts = [_open(theme, width, height, id, title, "; ".join(f"{x} {fmt(v, theme, decimals=decimals, unit=unit, kind=kind)}" for x, v in zip(x_labels, median) if v is not None))]
    for t in ticks:
        parts.append(f'<line x1="{left:.1f}" x2="{left + plot_w:.1f}" y1="{y_at(t):.1f}" y2="{y_at(t):.1f}" stroke="{theme["structure"]}" stroke-opacity="{theme.rule_opacity}"/>')
        parts.append(_text(theme, left - 8, y_at(t) + caption * 0.34, fmt(t, theme, decimals=decimals, unit=unit, kind=kind), size=caption, anchor="end", color="text-secondary", mono=True))
    for i, label in enumerate(x_labels):
        if i % tick_every == 0 or i == len(x_labels) - 1:
            parts.append(_text(theme, x_at(i), height - 4, label, size=caption, anchor="middle", color="text-secondary"))
    for band_i, (low, high) in enumerate(bands):
        pts_top = [f"{x_at(i):.1f},{y_at(v):.1f}" for i, v in enumerate(high) if v is not None]
        pts_bot = [f"{x_at(i):.1f},{y_at(v):.1f}" for i, v in reversed(list(enumerate(low))) if v is not None]
        opacity = round(0.10 + 0.12 * band_i, 3)
        parts.append(f'<polygon points="{" ".join(pts_top + pts_bot)}" fill="{theme["series-primary"]}" fill-opacity="{opacity}"/>')
    if reference is not None:
        parts.append(f'<line x1="{left:.1f}" x2="{left + plot_w:.1f}" y1="{y_at(reference):.1f}" y2="{y_at(reference):.1f}" stroke="{theme["structure"]}" stroke-width="{theme.chart["stroke"]}" stroke-dasharray="4 4"/>')
        if reference_label:
            parts.append(_text(theme, left + plot_w, y_at(reference) - 6, reference_label, size=caption, anchor="end", color="text-secondary"))
    path, pen = [], "M"
    for i, v in enumerate(median):
        if v is None:
            pen = "M"
            continue
        path.append(f"{pen}{x_at(i):.1f},{y_at(v):.1f}")
        pen = "L"
    parts.append(f'<path d="{" ".join(path)}" fill="none" stroke="{theme["series-primary"]}" stroke-width="{theme.chart["markStroke"]}" stroke-linejoin="round" stroke-linecap="round"/>')
    if band_labels:
        last = max(i for i, v in enumerate(median) if v is not None)
        for (low, high), text in zip(bands, band_labels):
            parts.append(_text(theme, x_at(last) - 4, y_at(high[last]) + caption * 0.34, text, size=caption, anchor="end", color="text-secondary"))
    if point is not None:
        i, v, label = point
        parts.append(f'<circle cx="{x_at(i):.1f}" cy="{y_at(v):.1f}" r="6" fill="{theme["emphasis"]}" stroke="{theme["structure"]}" stroke-width="{theme.chart["stroke"]}"/>')
        parts.append(_text(theme, x_at(i), y_at(v) - 12, label, size=caption, anchor="middle", color="text-primary", weight=600))
    return "".join(parts) + "</svg>"


def _segment_fills(theme, n):
    return [theme[role] for role in SEGMENT_ROLES[:n]] if n <= len(SEGMENT_ROLES) else [ramp(theme, i / (n - 1)) for i in range(n)]


def stacked_bar(theme, rows, segments, *, id, width=720, decimals=0, unit="", kind="number", normalize=False,
                direct_labels=True, title="Stacked bar"):
    """Part-to-whole bars. rows: [(label, [values per segment])]; segments: [names]. normalize=True for 100% bars."""
    size, caption, row_h, bar = theme.chart["label"], theme.chart["caption"], 56, 32
    fills = _segment_fills(theme, len(segments))
    label_w = _label_width([r[0] for r in rows], size)
    totals = [sum(v for v in vals) for _, vals in rows]
    peak = max(totals) or 1
    plot_w = width - label_w - 16
    legend_h = caption * 2.4
    height = row_h * len(rows) + legend_h
    parts = [_open(theme, width, height, id, title, "; ".join(f"{l}: " + ", ".join(f"{s} {fmt(v, theme, decimals=decimals, unit=unit, kind=kind)}" for s, v in zip(segments, vals)) for l, vals in rows))]
    lx = label_w
    for name, fill in zip(segments, fills):
        parts.append(f'<rect x="{lx:.1f}" y="0" width="14" height="14" fill="{fill}"/>')
        parts.append(_text(theme, lx + 20, 12, name, size=caption, color="text-secondary"))
        lx += 34 + len(name) * caption * 0.6
    for i, (label, vals) in enumerate(rows):
        y = legend_h + i * row_h + (row_h - bar) / 2
        total = totals[i] or 1
        full = plot_w if normalize else plot_w * totals[i] / peak
        parts.append(_text(theme, label_w - 12, y + bar / 2 + size * 0.34, label, anchor="end"))
        x = label_w
        for s, (value, fill) in enumerate(zip(vals, fills)):
            w = full * value / total
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{bar}" fill="{fill}"/>')
            shown = fmt(value * 100 / total if normalize else value, theme, decimals=1 if normalize else decimals, unit="%" if normalize else unit, kind="percent" if normalize else kind)
            if direct_labels and w > len(shown) * caption * 0.62 + 10:
                parts.append(_text(theme, x + w / 2, y + bar / 2 + caption * 0.34, shown, size=caption, anchor="middle", mono=True).replace(f'fill="{theme["text-primary"]}"', f'fill="{on(theme, fill)}"'))
            x += w
    return "".join(parts) + "</svg>"


def waterfall(theme, start, steps, *, id, end_label="Total", width=720, height=360, decimals=0, unit="", kind="number",
              start_label="Start", title="Waterfall"):
    """A running total built from signed steps. start: opening value; steps: [(label, delta)]. Ends on the total."""
    size, caption = theme.chart["label"], theme.chart["caption"]
    running = start
    bars = [(start_label, 0, start, True)]
    for label, delta in steps:
        nxt = running + delta
        bars.append((label, running, nxt, False))
        running = nxt
    bars.append((end_label, 0, running, True))
    vals = [0, start, running] + [b for _, a, b, _ in bars for b in (a, b)]
    yticks = _nice_ticks(min(vals), max(vals))
    lo, hi = yticks[0], yticks[-1]
    left = _label_width([fmt(t, theme, decimals=decimals, unit=unit, kind=kind) for t in yticks], caption) + 10
    top, bottom = 14, caption * 2.6
    plot_w, plot_h = width - left - 16, height - top - bottom
    n = len(bars)
    slot = plot_w / n
    bar_w = slot * 0.64
    y_at = lambda v: top + plot_h * (1 - (v - lo) / (hi - lo))
    parts = [_open(theme, width, height, id, title, "; ".join(f"{l}: {fmt(b - a if not t else b, theme, decimals=decimals, unit=unit, kind=kind, sign=not t)}" for l, a, b, t in bars))]
    for t in yticks:
        parts.append(f'<line x1="{left:.1f}" x2="{left + plot_w:.1f}" y1="{y_at(t):.1f}" y2="{y_at(t):.1f}" stroke="{theme["structure"]}" stroke-opacity="{theme.rule_opacity}"/>')
        parts.append(_text(theme, left - 8, y_at(t) + caption * 0.34, fmt(t, theme, decimals=decimals, unit=unit, kind=kind), size=caption, anchor="end", color="text-secondary", mono=True))
    for i, (label, a, b, total) in enumerate(bars):
        cx = left + slot * i + slot / 2
        top_v, bot_v = max(a, b), min(a, b)
        fill = theme["series-primary"] if total else (theme["outcome-positive"] if b >= a else theme["emphasis-text"])
        parts.append(f'<rect x="{cx - bar_w / 2:.1f}" y="{y_at(top_v):.1f}" width="{bar_w:.1f}" height="{max(y_at(bot_v) - y_at(top_v), 1):.1f}" fill="{fill}"/>')
        if i < n - 1:
            parts.append(f'<line x1="{cx + bar_w / 2:.1f}" x2="{left + slot * (i + 1) + slot / 2 - bar_w / 2:.1f}" y1="{y_at(b):.1f}" y2="{y_at(b):.1f}" stroke="{theme["structure"]}" stroke-opacity="0.4" stroke-dasharray="3 3"/>')
        shown = fmt(b if total else b - a, theme, decimals=decimals, unit=unit, kind=kind, sign=not total)
        parts.append(_text(theme, cx, y_at(top_v) - 6, shown, size=caption, anchor="middle", color="text-secondary", mono=True))
        parts.append(_text(theme, cx, top + plot_h + caption * 1.4, label, size=caption, anchor="middle", color="text-secondary"))
    parts.append(f'<line x1="{left:.1f}" x2="{left + plot_w:.1f}" y1="{y_at(max(lo, 0)):.1f}" y2="{y_at(max(lo, 0)):.1f}" stroke="{theme["structure"]}" stroke-width="{theme.chart["stroke"]}"/>')
    return "".join(parts) + "</svg>"


def sparkline(theme, values, *, width=132, height=36, reference=None, mark_last=True):
    """A tiny inline trend line, no axes. For KPI tiles and dense tables."""
    seq = [v for v in values if v is not None]
    lo, hi = min(seq), max(seq)
    pad = (hi - lo) * 0.12 or 1
    lo, hi = lo - pad, hi + pad
    x_at = lambda i: 2 + (width - 4) * i / max(len(values) - 1, 1)
    y_at = lambda v: 3 + (height - 6) * (1 - (v - lo) / (hi - lo))
    parts = [f'<svg class="wp-sparkline" viewBox="0 0 {width} {height}" width="{width}" height="{height}" aria-hidden="true" focusable="false">']
    if reference is not None:
        parts.append(f'<line x1="2" x2="{width - 2}" y1="{y_at(reference):.1f}" y2="{y_at(reference):.1f}" stroke="{theme["context"]}" stroke-width="1" stroke-dasharray="3 3"/>')
    parts.append(f'<path d="{_line_path(values, x_at, y_at)}" fill="none" stroke="{theme["series-primary"]}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
    if mark_last:
        last = max(i for i, v in enumerate(values) if v is not None)
        parts.append(f'<circle cx="{x_at(last):.1f}" cy="{y_at(values[last]):.1f}" r="3" fill="{theme["emphasis"]}" stroke="{theme["structure"]}" stroke-width="1.5"/>')
    return "".join(parts) + "</svg>"


def kpi_tiles(theme, tiles):
    """A grid of headline numbers. tiles: [{value, label, delta?, delta_kind?, trend?}]. Returns HTML, not SVG."""
    cells = []
    for tile in tiles:
        delta = ""
        if tile.get("delta") is not None:
            d = tile["delta"]
            good = (d >= 0) if tile.get("higher_is_better", True) else (d <= 0)
            color = "outcome-positive-text" if good else "emphasis-text"
            text = fmt(d, theme, decimals=tile.get("delta_decimals", 1), unit=tile.get("delta_unit", ""), kind=tile.get("delta_kind", "number"), sign=True)
            delta = f'<p class="kpi-delta" style="color:var(--{color})">{_esc(text)}</p>'
        spark = sparkline(theme, tile["trend"]) if tile.get("trend") else ""
        value = tile["value"] if isinstance(tile["value"], str) else fmt(tile["value"], theme, decimals=tile.get("decimals", 0), unit=tile.get("unit", ""), kind=tile.get("kind", "number"))
        cells.append(f'<div class="kpi-tile"><p class="kpi-label">{_esc(tile["label"])}</p><p class="kpi-value">{_esc(value)}</p>{delta}{spark}</div>')
    return f'<div class="kpi-grid">{"".join(cells)}</div>'


# Page furniture --------------------------------------------------------------------------

def figure(title, subtitle, svg, source, *, note=None, wide=False):
    """The figure anatomy: finding, measure, plot, source. All text stays selectable HTML.

    The finding names the figure for assistive technology; the source line stays the visible caption.
    """
    key = "fig-" + hashlib.sha1(f"{title}\n{subtitle}".encode()).hexdigest()[:8]
    note_html = f'<p class="wp-figure-note">{_esc(note)}</p>' if note else ""
    wide_class = " wp-figure-wide" if wide else ""
    return (f'<figure class="wp-figure{wide_class}" aria-labelledby="{key}"><p class="wp-figure-title" id="{key}">{_esc(title)}</p>'
            f'<p class="wp-figure-subtitle">{_esc(subtitle)}</p><div class="wp-figure-plot" tabindex="0" role="region" '
            f'aria-label="{_esc(title)}">{svg}</div>{note_html}<figcaption>{_esc(source)}</figcaption></figure>')


def table(columns, rows, *, numeric=(), caption=None, focus_row=None, label="Data table"):
    """A data table. columns: header strings with units; numeric: indexes to right-align."""
    numeric = set(numeric)
    num = ' class="num"'
    head = "".join(f'<th scope="col"{num if i in numeric else ""}>{_esc(c)}</th>' for i, c in enumerate(columns))
    body = []
    for r, row in enumerate(rows):
        cells = "".join((f'<th scope="row">{_esc(v)}</th>' if i == 0 else
                         f'<td{num if i in numeric else ""}>{_esc(v)}</td>') for i, v in enumerate(row))
        focus = ' class="focus"' if r == focus_row else ""
        body.append(f'<tr{focus}>{cells}</tr>')
    cap = f"<caption>{_esc(caption)}</caption>" if caption else ""
    return (f'<div class="table-scroll" tabindex="0" role="region" aria-label="{_esc(label)}"><table class="wp-table">{cap}'
            f'<thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>')


# matplotlib ------------------------------------------------------------------------------

def mplstyle(profile):
    """A matplotlib style generated from the profile. Use with plt.style.use("warm-precision.mplstyle")."""
    t = Theme(profile)
    hexes = lambda role: t[role].lstrip("#")
    cycle = ", ".join(f"'{hexes(role)}'" for role in profile["data"]["seriesOrder"])
    doc = profile["media"]["document"]
    lines = [
        f"# Generated from Warm Precision tokens.json ({profile['name']} {profile['version']}). Do not edit; rebuild instead.",
        "# Put titles, subtitles and source lines in the page or paper caption, not inside the image.",
        f"figure.facecolor: {hexes('canvas')}", f"axes.facecolor: {hexes('canvas')}", f"savefig.facecolor: {hexes('canvas')}",
        f"text.color: {hexes('text-primary')}", f"axes.labelcolor: {hexes('text-secondary')}", f"axes.edgecolor: {hexes('structure')}",
        f"xtick.color: {hexes('text-secondary')}", f"ytick.color: {hexes('text-secondary')}",
        f"axes.prop_cycle: cycler('color', [{cycle}])",
        "axes.linewidth: 1", "axes.spines.top: False", "axes.spines.right: False",
        "axes.grid: True", "axes.grid.axis: y", f"grid.color: {hexes('structure')}", f"grid.alpha: {t.rule_opacity}", "grid.linewidth: 0.8",
        "axes.axisbelow: True", "axes.titlelocation: left", "axes.titleweight: semibold", "axes.titlepad: 12",
        "font.family: sans-serif", f"font.sans-serif: {profile['typography']['body']['family']}, Arial, DejaVu Sans",
        f"font.monospace: SF Mono, Menlo, DejaVu Sans Mono",
        f"font.size: {doc['body']}", f"axes.titlesize: {doc['lede']}", f"axes.labelsize: {doc['body']}",
        f"xtick.labelsize: {doc['caption'] + 1}", f"ytick.labelsize: {doc['caption'] + 1}", f"legend.fontsize: {doc['caption'] + 1}",
        "legend.frameon: False", "lines.linewidth: 2", "lines.solid_capstyle: round", "lines.markersize: 6",
        "patch.linewidth: 0", "axes.unicode_minus: True",
        "figure.constrained_layout.use: True", "figure.figsize: 6.4, 4.0",
        "savefig.dpi: 200", "savefig.bbox: tight", "savefig.pad_inches: 0.2",
        "svg.fonttype: none", "pdf.fonttype: 42",
    ]
    return "\n".join(lines) + "\n"
