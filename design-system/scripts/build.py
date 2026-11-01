#!/usr/bin/env python3
"""Build Warm Precision's portable handbook from the brand and style kit.

Standard library only.
"""

import argparse
import base64
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import re
import sys
import urllib.request
import zipfile

PACKAGE = Path(__file__).resolve().parents[1]
PROJECT = PACKAGE.parent
PROFILE_DIR = PACKAGE / "profiles/warm-precision"  # the selected profile; copy the folder to make your own
PROFILE = PROFILE_DIR / "tokens.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import figures  # noqa: E402
import specimens  # noqa: E402
import examples  # noqa: E402

FONT_URL = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400;1,6..72,500&display=swap"
DOCS = [PACKAGE / "README.md", PACKAGE / "PHILOSOPHY.md", PACKAGE / "VOICE.md", PACKAGE / "DOCUMENTS.md",
        PROFILE_DIR / "INTEGRATION.md",
        *(PACKAGE / "adapters" / f"{name}.md" for name in ("web", "documents", "slides", "diagrams", "data", "motion", "scenes")),
        PACKAGE / "patterns/README.md",
        *(PACKAGE / "templates" / f"{name}.md" for name in
          ("ARTIFACT_BRIEF", "SCENE_BRIEF", "PROJECT_CONTEXT", "AGENT_INSTRUCTIONS", "REVIEW_RECEIPT")),
        PACKAGE / "SOURCES.md"]
if (PROJECT / "BRAND_KIT.md").exists():
    DOCS.insert(2, PROJECT / "BRAND_KIT.md")
LABELS = {"README.md": "Getting started", "PHILOSOPHY.md": "Principles", "BRAND_KIT.md": "Brand",
          "VOICE.md": "Voice", "DOCUMENTS.md": "Documents", str(PROFILE_DIR.relative_to(PACKAGE) / "INTEGRATION.md"): "Integration",
          "SOURCES.md": "Sources", "patterns/README.md": "Patterns"}
LOCAL_PAGES = PROJECT / "reviews"  # project-local designed pages; rendered into the build, never bundled
SCENES = PACKAGE / "scenes"  # HyperFrames compositions (one folder each) plus the in-page scene lab
VENDOR = PACKAGE / "vendor"
SCENE_FONTS = {("Newsreader", "normal", "600"), ("Inter", "normal", "400"), ("Inter", "normal", "600")}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def json_text(value):
    return json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def rgb(hex_value):
    return [int(hex_value[i:i + 2], 16) / 255 for i in (1, 3, 5)]


def luminance(channels):
    return sum(weight * (v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4)
               for weight, v in zip((.2126, .7152, .0722), channels))


def contrast(foreground, background):
    a, b = sorted((luminance(foreground), luminance(background)))
    return (b + .05) / (a + .05)


def resolved(profile):
    return {role: profile["colors"][name] for role, name in profile["roles"].items()}


def mix(foreground, background, opacity):
    return [opacity * a + (1 - opacity) * b for a, b in zip(foreground, background)]


def validate_profile(profile):
    assert profile["schema"] == "warm-precision-profile/1"
    assert all(re.fullmatch(r"#[0-9A-F]{6}", value) for value in profile["colors"].values())
    assert set(profile["roles"].values()) <= set(profile["colors"])
    assert profile["spacing"]["scale"] == sorted(set(profile["spacing"]["scale"]))
    assert all(n % profile["spacing"]["base"] == 0 for n in profile["spacing"]["scale"])
    assert set(profile["data"]["seriesOrder"]) <= set(profile["roles"])
    roles = resolved(profile)
    required = [("text-primary", "canvas"), ("text-secondary", "canvas"), ("link", "canvas"), ("kicker", "canvas"),
                ("emphasis-text", "canvas"), ("outcome-positive-text", "canvas"),
                ("on-structure", "structure"), ("on-emphasis", "emphasis"), ("on-positive", "outcome-positive")]
    for fg, bg in required:
        assert contrast(rgb(roles[fg]), rgb(roles[bg])) >= profile["contract"]["textContrast"], (fg, bg)
    for role in ("structure", "focus", "series-primary", "context", "series-context"):
        assert contrast(rgb(roles[role]), rgb(roles["canvas"])) >= profile["contract"]["essentialMarkContrast"], role


def contrast_receipt(profile):
    roles = resolved(profile)
    pairs = [("text-primary", "canvas"), ("text-secondary", "canvas"), ("kicker", "canvas"),
             ("emphasis-text", "canvas"), ("outcome-positive-text", "canvas"),
             ("structure", "canvas"), ("context", "canvas"), ("emphasis", "canvas"), ("outcome-positive", "canvas"),
             ("on-structure", "structure"), ("on-emphasis", "emphasis"), ("on-positive", "outcome-positive")]
    receipt = [{"foreground": a, "background": b, "ratio": round(contrast(rgb(roles[a]), rgb(roles[b])), 4)}
               for a, b in pairs]
    fg, bg = rgb(roles["structure"]), rgb(roles["canvas"])
    for name, key in (("decorative-rule", "decorativeOpacity"), ("track", "trackOpacity")):
        opacity = profile["stroke"][key]
        receipt.append({"foreground": name, "background": "canvas", "opacity": opacity,
                        "ratio": round(contrast(mix(fg, bg, opacity), bg), 4), "essential": False})
    return {"schema": "warm-precision-contrast/1", "profile": profile["version"], "pairs": receipt,
            "note": "Orange/sage on Ivory require dark essential support. Rules and tracks are decorative, never structural."}


def tokens_css(profile):
    values = {**profile["colors"], **resolved(profile)}
    for role, data in profile["typography"].items():
        values[f"font-{role}"] = figures.font_stack(data)
        values[f"weight-{role}"] = str(data["weight"])
        values[f"tracking-{role}"] = f'{data.get("tracking", 0)}em'
    values["case-kicker"] = profile["typography"]["kicker"].get("case", "none")
    values.update({f"space-{n}": f"{n}px" for n in profile["spacing"]["scale"]})
    for group in ("radius", "stroke"):
        for key, value in profile[group].items():
            if key != "unit":
                values[f"{group}-{key}"] = str(value) if key.endswith("Opacity") else f"{value}{profile[group]['unit']}"
    for medium, data in profile["media"].items():
        for key, value in data.items():
            if key == "unit":
                continue
            suffix = "" if key == "lineHeight" else "ch" if key == "measureCh" else "mm" if key == "marginMm" else data["unit"]
            values[f"{medium}-{key}"] = f"{value}{suffix}"
    values["motion-duration"] = f"{profile['motion']['durationMs']}ms"
    values["motion-easing"] = profile["motion"]["easing"]
    rule = " ".join(str(round(c * 255)) for c in rgb(resolved(profile)["structure"]))
    values["rule-decorative"] = f"rgb({rule} / {profile['stroke']['decorativeOpacity']})"
    values["track"] = f"rgb({rule} / {profile['stroke']['trackOpacity']})"
    return f"/* Generated from profiles/{profile['slug']}/tokens.json. */\n:root {{\n" + "".join(
        f"  --{key}: {value};\n" for key, value in values.items()) + "}\n"


COLOR_MEANINGS = {"ivory": "Canvas and open space", "onyx": "Primary text", "blue-slate": "Structure, links, buttons, primary data",
                  "golden-orange": "The one focus; fill only, with an outline", "sage-green": "Secondary series or positive cue; fill only",
                  "slate-deep": "Secondary text and kickers", "copper-deep": "Text-safe accent",
                  "sage-deep": "Text-safe positive cue", "parchment": "Detail wells, never a second canvas",
                  "slate-mist": "Context series and reference lines; marks only"}


def signed(value):
    return str(value).replace("-", "\u2212")


def brand_reference(profile):
    lines = ["| Color | Exact value | Role |", "| --- | --- | --- |"]
    lines += [f"| {name.replace('-', ' ').title()} | `{value}` | {COLOR_MEANINGS[name]} |" for name, value in profile["colors"].items()]
    lines += ["", "| Typography | Family | Weight | Tracking |", "| --- | --- | --- | --- |"]
    lines += [f"| {name.title()} | {data['family']} | {data['weight']} | {signed(data.get('tracking', 0))} em |"
              for name, data in profile["typography"].items()]
    lines += ["", "| Medium | Body / primary labels | Supporting text |", "| --- | --- | --- |"]
    for name, data in profile["media"].items():
        main = data.get("body", data.get("label"))
        lines.append(f"| {name.title()} | {main} {data['unit']} | {data['caption']} {data['unit']} |")
    lines += ["", f"Container radii: {profile['radius']['small']}–{profile['radius']['container']} px. "
              f"Structural and focus strokes: {profile['stroke']['structural']}/{profile['stroke']['emphasis']} px. "
              f"Decorative rules: {profile['stroke']['decorative']} px at {profile['stroke']['decorativeOpacity']:.0%} Blue Slate; "
              f"tracks at {profile['stroke']['trackOpacity']:.0%}."]
    return "\n".join(lines)


def update_brand(profile):
    path = PROJECT / "BRAND_KIT.md"
    text = path.read_text(encoding="utf-8")
    pattern = r"(<!-- profile-tokens:start -->\n).*?(\n<!-- profile-tokens:end -->)"
    changed, count = re.subn(pattern, lambda m: m[1] + brand_reference(profile) + m[2], text, flags=re.S)
    assert count == 1, "BRAND_KIT.md must have exactly one generated reference block"
    write(path, changed)


def font_assets(out, embed):
    if not embed:
        return f'@import url("{FONT_URL}");\n', {"mode": "web", "stylesheet": FONT_URL,
                 "fallback": "Inter unavailable: profile system stacks; verify before publishing"}
    css_path, receipt_path = out / "fonts.css", out / "font-receipt.json"
    if css_path.exists() and receipt_path.exists():
        receipt = read_json(receipt_path)
        if receipt.get("mode") == "embedded" and receipt.get("stylesheet") == FONT_URL:
            text = css_path.read_text(encoding="utf-8")
            if hashlib.sha256(text.encode()).hexdigest() == receipt.get("css_sha256"):
                return text, receipt
    request = urllib.request.Request(FONT_URL, headers={"User-Agent": "WarmPrecision/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        css = response.read().decode()
    assets = []
    for url in dict.fromkeys(re.findall(r"url\((https://[^)]+)\)", css)):
        if not url.startswith("https://fonts.gstatic.com/"):
            raise ValueError(f"Unexpected font asset host: {url}")
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read()
            mime = response.headers.get_content_type()
        css = css.replace(url, f"data:{mime};base64,{base64.b64encode(data).decode()}")
        assets.append({"url": url, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    assert assets and "@font-face" in css
    return css, {"mode": "embedded", "stylesheet": FONT_URL, "assets": assets,
                 "css_sha256": hashlib.sha256(css.encode()).hexdigest(),
                  "families": {"Inter": [400, 500, 600], "Newsreader": [400, 500, 600]},
                 "note": "Public Google Fonts, embedded for offline viewing. See font-license links on the handbook."}


NAV = (("Examples", "examples/index.html"), ("Brand", "handbook/brand-kit.html"), ("Voice", "handbook/VOICE.html"),
       ("Documents", "handbook/DOCUMENTS.html"), ("Data", "handbook/adapters-data.html"))
DESCRIPTION = "The Warm Precision brand and style kit: colors, type, voice, document shapes and data presentation."


def page(title, body, kind="", prefix="", font_mode="embedded", styles=(), motion=False, description=DESCRIPTION, scripts=()):
    page_title = title if title == "Warm Precision" else f"{title} · Warm Precision"
    extra_styles = "".join(f'<link rel="stylesheet" href="{prefix}{html.escape(name, quote=True)}">' for name in styles)
    motion_css = f'<link rel="stylesheet" href="{prefix}motion.css">' if motion else ""
    motion_js = f'<script src="{prefix}motion.js" defer></script>' if motion else ""
    motion_js += "".join(f'<script src="{prefix}{html.escape(name, quote=True)}" defer></script>' for name in scripts)
    nav = "".join(f'<a href="{prefix}{href}">{label}</a>' for label, href in NAV)
    meta = html.escape(description, quote=True)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(page_title)}</title><meta name="description" content="{meta}"><meta property="og:title" content="{html.escape(page_title, quote=True)}"><meta property="og:description" content="{meta}"><meta property="og:type" content="website"><meta name="twitter:card" content="summary"><link rel="icon" href="{prefix}favicon.svg"><link rel="stylesheet" href="{prefix}tokens.css"><link rel="stylesheet" href="{prefix}fonts.css"><link rel="stylesheet" href="{prefix}layout.css">{motion_css}{extra_styles}</head>
<body class="{kind}"><a class="skip" href="#main">Skip to content</a>
<header class="masthead"><a href="{prefix}index.html" class="wordmark">warm precision.<span>Design handbook</span></a><nav aria-label="Primary">{nav}</nav></header>
<main id="main">{body}</main><footer class="site-footer"><p>Warm Precision profile</p><a href="{prefix}warm-precision-kit.zip">Download the kit</a><a href="{prefix}warm-precision.mplstyle" download>matplotlib style</a><a href="{prefix}handbook/SOURCES.html">Sources</a></footer>{motion_js}</body></html>'''


def doc_slug(path):
    if path.parent == PROJECT:
        return path.stem.lower().replace("_", "-") + ".html"
    return "-".join(path.relative_to(PACKAGE).with_suffix("").parts) + ".html"


def markdown(text, source, doc_map, headings=None):
    """Render the package's deliberately small Markdown vocabulary, escaping HTML."""
    headings = [] if headings is None else headings
    heading_ids = set()
    def inline(value):
        slots = []
        def stash(body):
            slots.append(body)
            return f"\x00{len(slots) - 1}\x00"
        value = re.sub(r"`([^`]+)`", lambda m: stash(f"<code>{html.escape(m[1])}</code>"), value)
        def link(match):
            label, target = match.groups()
            if target.startswith(("https://", "http://", "#")):
                url = target
            else:
                target, separator, fragment = target.partition("#")
                candidate = (source.parent / target).resolve()
                if candidate in doc_map:
                    url = doc_map[candidate] + (separator + fragment if separator else "")
                elif candidate.is_dir():
                    url = "../index.html#handbook"
                else:
                    return stash(html.escape(label))
            return stash(f'<a href="{html.escape(url, quote=True)}">{html.escape(label)}</a>')
        value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, value)
        value = re.sub(r"<((?:https?://|mailto:)[^<>\s]+)>",
                       lambda m: stash(f'<a href="{html.escape(m[1], quote=True)}">{html.escape(m[1])}</a>'), value)
        value = html.escape(value)
        value = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", value)
        return re.sub(r"\x00(\d+)\x00", lambda m: slots[int(m[1])], value)
    lines = text.splitlines()
    output, paragraph = [], []
    def flush():
        if paragraph:
            body = "".join(inline(line.strip()) + ("<br>" if line.endswith("  ") else " ")
                           for line in paragraph).strip()
            output.append("<p>" + body + "</p>")
            paragraph.clear()
    list_pattern = r"^(\s*)([-+*]|\d+\.)\s+(.*)$"
    def render_list(start):
        first = re.match(list_pattern, lines[start])
        indent = len(first[1])
        kind = "ol" if first[2][0].isdigit() else "ul"
        attrs = f' start="{int(first[2][:-1])}"' if kind == "ol" and first[2] != "1." else ""
        items = [f"<{kind}{attrs}>"]
        index = start
        while index < len(lines):
            match = re.match(list_pattern, lines[index])
            if not match or len(match[1]) != indent or ("ol" if match[2][0].isdigit() else "ul") != kind:
                break
            content_indent = len(match[1]) + len(match[2]) + 1
            item = [match[3]]
            index += 1
            while index < len(lines):
                line = lines[index]
                if line.strip() and len(line) - len(line.lstrip()) < content_indent:
                    break
                item.append(line[content_indent:] if line.strip() else "")
                index += 1
            task = re.match(r"^\[([ xX])\]\s+(.*)$", item[0])
            if task:
                item[0] = task[2]
                checked = " checked" if task[1].lower() == "x" else ""
                control = f'<input type="checkbox" disabled{checked} aria-label="{html.escape(task[2], quote=True)}">'
                items.append('<li class="task-item">' + control + markdown("\n".join(item), source, doc_map) + '</li>')
            else:
                items.append("<li>" + markdown("\n".join(item), source, doc_map) + "</li>")
        items.append(f"</{kind}>")
        return "\n".join(items), index
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            flush()
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(lines[i]); i += 1
            output.append("<pre><code>" + html.escape("\n".join(block)) + "</code></pre>")
        elif re.match(r"^#{1,6} ", line):
            flush()
            level = len(line.split(" ", 1)[0])
            title = line[level + 1:]
            plain = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", title).replace("`", "").replace("*", "")
            base = re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-") or "section"
            anchor, suffix = base, 2
            while anchor in heading_ids:
                anchor = f"{base}-{suffix}"; suffix += 1
            heading_ids.add(anchor)
            headings.append((level, plain, anchor))
            output.append(f'<h{level} id="{anchor}">{inline(title)}</h{level}>')
        elif line.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            output.append('<div class="table-scroll" tabindex="0" role="region" aria-label="Reference table"><table>')
            output.append("<thead><tr>" + "".join(f'<th scope="col">{inline(c)}</th>' for c in rows[0]) + "</tr></thead><tbody>")
            for row in rows[1:]:
                output.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
            output.append("</tbody></table></div>")
            continue
        elif re.match(list_pattern, line):
            flush()
            rendered, i = render_list(i)
            output.append(rendered)
            continue
        elif line.startswith(">"):
            flush()
            quote = []
            while i < len(lines) and lines[i].startswith(">"):
                quote.append(re.sub(r"^> ?", "", lines[i])); i += 1
            output.append("<blockquote>" + markdown("\n".join(quote), source, doc_map) + "</blockquote>")
            continue
        elif not line.strip() or line == "---":
            flush()
        elif line.startswith("<!--"):
            pass
        else:
            paragraph.append(line)
        i += 1
    flush()
    return "\n".join(output)


def workspace_document(text, path, doc_map, specimen=""):
    headings = []
    content = markdown(text, path, doc_map, headings)
    first_section = re.search(r"<h2\b", content)
    intro = content[:first_section.start()] if first_section else content
    content = content[first_section.start():] if first_section else ""
    links = "".join(f'<li><a href="#{anchor}">{html.escape(title)}</a></li>'
                    for level, title, anchor in headings if level == 2)
    navigation = f'<aside class="document-outline"><nav aria-label="On this page"><p class="context">On this page</p><ol>{links}</ol></nav></aside>' if links else ""
    source = doc_slug(path).replace(".html", ".md")
    header = f'<header class="wrap document document-intro">{intro}<p class="document-tools"><a href="{source}" download="{html.escape(path.name, quote=True)}">Download Markdown source</a></p></header>'
    showcase = f'<div class="wrap specimens">{specimen}</div>' if specimen else ""
    return header + showcase + (f'<div class="wrap document-layout">{navigation}<article class="document document-content">{content}</article></div>' if content else "")


def overlay(profile):
    roles = resolved(profile)
    mappings = {"paper / paper-2": "canvas", "ink / ink-strong": "text-primary", "muted / soft / link": "structure",
                "focal fill": "emphasis", "focal text": "on-emphasis", "essential connector / outline": "structure"}
    name = profile["name"]
    text = (f'# Generated {name} profile → Diagram Design overlay\n\nThis is adaptation guidance, not a complete vendor profile. '
            f'See profiles/{profile["slug"]}/INTEGRATION.md.\n\n| Vendor role/use | {name} role | Value |\n| --- | --- | --- |\n')
    text += "".join(f'| {vendor} | {role} | `{roles[role]}` |\n' for vendor, role in mappings.items())
    text += f'\nTitle: {profile["typography"]["display"]["family"]} {profile["typography"]["display"]["weight"]}. Names, prose, and callouts: {profile["typography"]["body"]["family"]}. Kickers: {profile["typography"]["kicker"]["family"]} {profile["typography"]["kicker"]["weight"]}, uppercase with wide tracking, in the kicker role.\n'
    text += '\nSplit accent roles explicitly: orange fill with dark text and essential outline. Orange cannot serve as the vendor’s universal text/stroke accent on Ivory. Use canvas rather than decorative accent tints. Resolve type sizes and geometry from the destination adapter.\n'
    return text


def artifacts(profile, fonts, mode):
    colors = resolved(profile)
    outputs = {
        "favicon.svg": f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" fill="{colors["canvas"]}"/><path d="M5 7 L10 25 L16 13 L22 25 L27 7" fill="none" stroke="{colors["structure"]}" stroke-width="3" stroke-linejoin="round"/></svg>',
        "tokens.css": tokens_css(profile),
        "tokens.resolved.json": json_text({"profile": profile, "resolvedRoles": resolved(profile)}),
        "contrast.json": json_text(contrast_receipt(profile)),
        "layout.css": (PACKAGE / "assets/layout.css").read_text(encoding="utf-8"),
        "motion.css": (PACKAGE / "assets/motion.css").read_text(encoding="utf-8"),
        "motion.js": (PACKAGE / "assets/motion.js").read_text(encoding="utf-8"),
        "warm-precision.mplstyle": figures.mplstyle(profile),
        "diagram-design-overlay.md": overlay(profile),
    }
    doc_map = {path.resolve(): doc_slug(path) for path in DOCS}
    assert len(set(doc_map.values())) == len(doc_map), "Document filenames produce duplicate page URLs"
    groups = {"Foundations": [], "Media": [], "Practice": []}
    for path in DOCS:
        text = path.read_text(encoding="utf-8")
        title = next(line[2:] for line in text.splitlines() if line.startswith("# "))
        slug = doc_slug(path)
        key = str(path.relative_to(PACKAGE)) if path.is_relative_to(PACKAGE) else path.name
        specimen, options = specimens.for_document(key, profile, text)
        body = workspace_document(text, path, doc_map, specimen)
        outputs[f"handbook/{slug}"] = page(title, body, prefix="../", font_mode=mode, **options)
        outputs[f"handbook/{slug.replace('.html', '.md')}"] = text
        group = ("Media" if path.parent.name == "adapters"
                 else "Practice" if path.parent.name in {"patterns", "templates"} or path.name == "SOURCES.md" else "Foundations")
        groups[group].append((LABELS.get(key, title), f"handbook/{slug}"))
    choosing = (PACKAGE / "DOCUMENTS.md").read_text(encoding="utf-8")
    outputs["index.html"] = page("Warm Precision", specimens.home(profile, groups, choosing), font_mode=mode)
    outputs.update(example_outputs(profile, choosing, mode))
    outputs.update(scene_outputs(profile, fonts))
    return outputs


def example_outputs(profile, documents_text, mode):
    """Finished artifacts with their decision notes, under examples/."""
    outputs = {"examples.css": (PACKAGE / "assets/examples.css").read_text(encoding="utf-8"),
               "examples.js": (PACKAGE / "assets/examples.js").read_text(encoding="utf-8")}
    for slug, (title, body, description) in examples.pages(profile, documents_text).items():
        outputs[f"examples/{slug}"] = page(title, body, kind="examples", prefix="../", font_mode=mode, styles=("examples.css",),
                                           scripts=("examples.js",), description=description)
    return outputs


def scene_css(profile):
    """Tokens for HyperFrames scenes: colors, the video scale, and font stacks HyperFrames can resolve offline."""
    t = profile["typography"]
    values = {**profile["colors"], **resolved(profile)}
    values["scene-display"] = f'"{t["display"]["family"]}", serif'
    values["scene-body"] = f'"{t["body"]["family"]}", sans-serif'
    values.update({f"video-{key}": f"{value}px" for key, value in profile["media"]["video"].items() if key != "unit"})
    rule = " ".join(str(round(c * 255)) for c in rgb(resolved(profile)["structure"]))
    values["rule-decorative"] = f"rgb({rule} / {profile['stroke']['decorativeOpacity']})"
    head = f"/* Generated from profiles/{profile['slug']}/tokens.json for scene projects. */\n:root {{\n" + "".join(
        f"  --{key}: {value};\n" for key, value in values.items()) + "}\n"
    k, d, w = t["kicker"], t["display"], t["wordmark"]
    return head + f"""html, body {{ margin: 0; background: var(--canvas); }}
[data-composition-id] {{ position: relative; overflow: hidden; background: var(--canvas); color: var(--text-primary);
  font-family: var(--scene-body); font-size: var(--video-body); line-height: 1.3; }}
.scene-text {{ position: absolute; margin: 0; }}
.scene-layer {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; overflow: visible; }}
.scene-kicker {{ font-family: var(--scene-body); font-weight: {k["weight"]}; font-size: var(--video-kicker); letter-spacing: {k["tracking"]}em;
  text-transform: uppercase; color: var(--kicker); }}
.scene-title {{ font-family: var(--scene-display); font-weight: {d["weight"]}; letter-spacing: {d["tracking"]}em; line-height: 1.08;
  color: var(--text-primary); text-wrap: balance; }}
.scene-wordmark {{ font-family: var(--scene-display); font-weight: {w["weight"]}; letter-spacing: {w["tracking"]}em; color: var(--text-primary); }}
"""


def scene_fonts(fonts):
    """Only the faces scenes use, so each scene project stays small and self-contained."""
    if "@font-face" not in fonts:  # web mode: HyperFrames fetches and caches the Google families itself
        return fonts
    keep = []
    for block in re.findall(r"@font-face\s*\{[^}]*\}", fonts):
        family = re.search(r"font-family:\s*['\"]?([^;'\"]+)", block)[1]
        style = re.search(r"font-style:\s*(\w+)", block)[1]
        weight = re.search(r"font-weight:\s*(\d+)", block)[1]
        if (family, style, weight) in SCENE_FONTS:
            keep.append(block)
    assert len(keep) >= len(SCENE_FONTS), "Scene fonts missing from fonts.css"
    return "/* Newsreader 600 and Inter 400/600, from the handbook's fonts.css. */\n" + "\n".join(keep) + "\n"


def scene_outputs(profile, fonts):
    """Each scene folder becomes a self-contained HyperFrames project; the lab serves the Scenes page."""
    outputs = {"scenes/lab.js": (SCENES / "lab.js").read_text(encoding="utf-8"),
               "scenes/lab.css": (SCENES / "lab.css").read_text(encoding="utf-8")}
    for script in specimens.SCENE_SCRIPTS:
        if script.startswith("scenes/vendor/"):
            outputs[script] = (VENDOR / script.removeprefix("scenes/vendor/")).read_text(encoding="utf-8")
    shared = {"fonts.css": scene_fonts(fonts), "scene.css": scene_css(profile),
              "player.js": (SCENES / "player.js").read_text(encoding="utf-8")}
    for source in sorted(SCENES.glob("*/index.html")):
        name = source.parent.name
        text = source.read_text(encoding="utf-8")
        outputs[f"scenes/{name}/index.html"] = text
        for ref in sorted(set(re.findall(r'(?:href|src)="assets/([^"]+)"', text))):
            vendored = VENDOR / "gsap" / ref
            assert ref in shared or vendored.is_file(), f"Scene {name} references unknown asset: {ref}"
            outputs[f"scenes/{name}/assets/{ref}"] = shared.get(ref) or vendored.read_text(encoding="utf-8")
    return outputs


def check(profile, out):
    validate_profile(profile)
    fonts = (out / "fonts.css").read_text(encoding="utf-8")
    receipt = read_json(out / "font-receipt.json")
    if receipt["mode"] == "embedded":
        assert hashlib.sha256(fonts.encode()).hexdigest() == receipt["css_sha256"]
        assert not re.search(r'url\(["\']?https?://', fonts)
    expected = artifacts(profile, fonts, receipt["mode"])
    for name, content in expected.items():
        assert (out / name).read_text(encoding="utf-8") == content, f"Stale generated output: {name}"
    # Check all generated relative links, including handbook navigation and downloads.
    for name, content in expected.items():
        if not name.endswith(".html"):
            continue
        for link in re.findall(r'(?:href|src)="([^"]+)"', content):
            if link.startswith(("https://", "http://", "data:", "#")):
                continue
            target = (out / name).parent / link.split("#", 1)[0]
            assert target.exists(), f"Broken link: {name} → {link}"
    brand = PROJECT / "BRAND_KIT.md"
    if brand.exists() and "<!-- profile-tokens:start -->" in brand.read_text():
        assert brand_reference(profile) in brand.read_text(), "Stale brand reference; use --write-brand"
    print(f"OK: profile contrast/roles, {len(expected)} generated artifacts, local links.")


def bundle(out):
    directories = ("profiles", "adapters", "patterns", "templates", "scripts", "assets", "scenes", "vendor")
    paths = [PACKAGE / name for name in ("README.md", "PHILOSOPHY.md", "VOICE.md", "DOCUMENTS.md", "SOURCES.md")]
    for directory in directories:
        paths.extend(p for p in (PACKAGE / directory).rglob("*") if p.is_file() and "__pycache__" not in p.parts and not p.name.startswith("."))
    with zipfile.ZipFile(out / "warm-precision-kit.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for path in paths:
            archive.write(path, "design-system/" + str(path.relative_to(PACKAGE)))
        brand = PROJECT / "BRAND_KIT.md"
        if brand.exists():
            archive.write(brand, "BRAND_KIT.md")
        license_file = PROJECT / "LICENSE"
        if license_file.exists():
            archive.write(license_file, "LICENSE")


def local_pages(out, mode):
    """Render project-local designed pages (reviews/*.py with a render(out, build, mode) function)."""
    rendered = []
    if not LOCAL_PAGES.is_dir():
        return rendered
    for script in sorted(LOCAL_PAGES.glob("*.py")):
        spec = importlib.util.spec_from_file_location(f"local_page_{script.stem}", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "render"):
            rendered.extend(module.render(out, sys.modules[__name__], mode) or [])
    return rendered


def sources():
    roots = [PACKAGE, PROJECT / "BRAND_KIT.md", LOCAL_PAGES]
    files = []
    for root in roots:
        if root.is_file():
            files.append(root)
        elif root.is_dir():
            files.extend(p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts and not p.name.startswith("."))
    return {p: p.stat().st_mtime for p in files}


def run(args, profile):
    if args.write_brand:
        update_brand(profile)
    args.out.mkdir(parents=True, exist_ok=True)
    fonts, receipt = font_assets(args.out, args.embed_fonts)
    write(args.out / "fonts.css", fonts)
    write(args.out / "font-receipt.json", json_text(receipt))
    for name, content in artifacts(profile, fonts, receipt["mode"]).items():
        write(args.out / name, content)
    bundle(args.out)
    check(profile, args.out)
    for path in local_pages(args.out, receipt["mode"]):
        print(f"Local page: {path}")
    print(f"Built: {args.out.resolve() / 'index.html'}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=PROJECT / "handbook")
    parser.add_argument("--embed-fonts", action="store_true", help="Fetch once and embed the actual brand fonts; reuse verified output cache")
    parser.add_argument("--write-brand", action="store_true", help="Refresh only the marked generated brand reference")
    parser.add_argument("--check", action="store_true", help="Validate existing output without regenerating it")
    parser.add_argument("--watch", action="store_true", help="Rebuild whenever a source file changes; stop with Ctrl+C")
    args = parser.parse_args()
    profile = read_json(PROFILE)
    validate_profile(profile)
    if args.check:
        if args.write_brand or args.watch:
            parser.error("--check is read-only; run it separately")
        check(profile, args.out)
        return
    run(args, profile)
    if not args.watch:
        return
    import importlib
    import time
    print("Watching design-system/, BRAND_KIT.md and reviews/ for changes. Ctrl+C to stop.")
    seen = sources()
    try:
        while True:
            time.sleep(1)
            current = sources()
            if current == seen:
                continue
            seen = current
            try:
                importlib.reload(figures)
                importlib.reload(specimens)
                importlib.reload(examples)
                run(args, read_json(PROFILE))
            except (AssertionError, ValueError, OSError, SyntaxError, KeyError) as exc:
                print(f"Build/validation failed: {exc}", file=sys.stderr)
            seen = sources()
    except KeyboardInterrupt:
        print("Stopped watching.")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, ValueError, OSError) as exc:
        print(f"Build/validation failed: {exc}", file=sys.stderr)
        sys.exit(1)
