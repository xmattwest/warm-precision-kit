"""Meaningful failure checks and a clean-room portable-package build."""

import copy
import importlib.util
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("warm_precision_build", Path(__file__).with_name("build.py"))
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class DocumentStructure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.text = []
        self.ids = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a":
            self.links.append(attrs["href"])
        if tag not in {"input", "br"}:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        self.assert_balanced(tag)

    def assert_balanced(self, tag):
        assert self.stack and self.stack.pop() == tag, f"Unbalanced document tag: {tag}"

    def handle_data(self, data):
        if data.strip():
            self.text.append((data.strip(), tuple(self.stack)))


class MarkdownDocuments(unittest.TestCase):
    def test_nested_release_steps_preserve_list_relationships(self):
        text = "1. Publish research.\n2. Explain it:\n   - Share a figure.\n   - Link the evidence.\n3. Invite replication."
        structure = DocumentStructure()
        structure.feed(build.markdown(text, build.PROJECT / "example.md", {}))
        self.assertEqual([value for value, _ in structure.text],
                         ["Publish research.", "Explain it:", "Share a figure.", "Link the evidence.", "Invite replication."])
        self.assertIn(("Share a figure.", ("ol", "li", "ul", "li", "p")), structure.text)
        self.assertIn(("Invite replication.", ("ol", "li", "p")), structure.text)
        self.assertEqual(structure.stack, [])

    def test_quoted_requirements_checklists_and_literal_html_survive(self):
        text = '> Preserve search access.\n\n- [ ] Verify indexing.\n- [x] Read the plan.\n\n<https://example.com/work>\n\n<script>alert("unsafe")</script>'
        rendered = build.markdown(text, build.PROJECT / "example.md", {})
        structure = DocumentStructure()
        structure.feed(rendered)
        self.assertIn(("Preserve search access.", ("blockquote", "p")), structure.text)
        self.assertEqual(rendered.count('type="checkbox"'), 2)
        self.assertIn("disabled checked", rendered)
        self.assertIn("https://example.com/work", structure.links)
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)

    def test_navigation_has_unique_heading_targets_and_a_source_download(self):
        path = build.PROJECT / "example.md"
        text = "# Example guide\n\n## Same section\n\nFirst.\n\n## Same section\n\nSecond."
        rendered = build.workspace_document(text, path, {})
        structure = DocumentStructure()
        structure.feed(rendered)
        self.assertEqual(len(structure.ids), len(set(structure.ids)))
        for link in structure.links:
            if link.startswith("#"):
                self.assertIn(link[1:], structure.ids)
        self.assertIn("example.md", structure.links)
        self.assertIn('download="example.md"', rendered)
        self.assertLess(rendered.index("Example guide"), rendered.index("On this page"))


class KitIntegrity(unittest.TestCase):
    def setUp(self):
        self.profile = build.read_json(build.PROFILE)

    def test_unsafe_accent_text_is_rejected(self):
        profile = copy.deepcopy(self.profile)
        profile["roles"]["text-primary"] = "golden-orange"
        with self.assertRaises(AssertionError):
            build.validate_profile(profile)

    def test_token_outputs_derive_from_profile(self):
        css = build.tokens_css(self.profile)
        for name, value in self.profile["colors"].items():
            self.assertIn(value, css)
        receipt = build.contrast_receipt(self.profile)
        self.assertEqual(receipt["schema"], "warm-precision-contrast/1")
        text_primary = next(pair for pair in receipt["pairs"] if pair["foreground"] == "text-primary")
        self.assertGreaterEqual(text_primary["ratio"], self.profile["contract"]["textContrast"])
        reference = build.brand_reference(self.profile)
        for value in self.profile["colors"].values():
            self.assertIn(value, reference)

    def test_package_builds_in_clean_room(self):
        import zipfile
        with tempfile.TemporaryDirectory(prefix="warm-precision-") as directory:
            root = Path(directory)
            build.bundle(root)
            with zipfile.ZipFile(root / "warm-precision-kit.zip") as archive:
                names = archive.namelist()
                self.assertIn("design-system/PHILOSOPHY.md", names)
                self.assertIn("BRAND_KIT.md", names)
                for forbidden in ("examples/", "documents/", "tools/", "playbooks/"):
                    self.assertFalse(any(forbidden in name for name in names), forbidden)
                archive.extractall(root / "clean-room")
            clean = root / "clean-room"
            result = subprocess.run([sys.executable, "design-system/scripts/build.py", "--out", "preview"],
                                    cwd=clean, text=True, capture_output=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("OK: profile contrast/roles", result.stdout)
            self.assertTrue((clean / "preview/index.html").exists())
            for path in build.DOCS:
                self.assertTrue((clean / "preview/handbook" / build.doc_slug(path)).exists())
            self.assertFalse((clean / "preview/evidence.json").exists())


class Figures(unittest.TestCase):
    """The data standard's number and chart rules, checked on the helpers directly."""

    def setUp(self):
        self.theme = build.figures.Theme(build.read_json(build.PROFILE))

    def test_numbers_follow_the_data_standard(self):
        fmt = build.figures.fmt
        self.assertEqual(fmt(1234567, self.theme), "1,234,567")
        self.assertEqual(fmt(-3.2, self.theme, decimals=1), "\u22123.2")
        self.assertEqual(fmt(-0.04, self.theme, decimals=1), "0.0")
        self.assertEqual(fmt(2.1, self.theme, decimals=1, kind="pp"), "+2.1 pp")
        self.assertEqual(fmt(None, self.theme), "n/a")
        self.assertEqual(fmt(float("nan"), self.theme), "n/a")

    def test_currency_puts_the_sign_before_the_symbol(self):
        fmt = build.figures.fmt
        self.assertEqual(fmt(1250.5, self.theme, decimals=2, kind="currency"), "$1,250.50")
        self.assertEqual(fmt(-3.2, self.theme, decimals=2, kind="currency"), "\u2212$3.20")
        self.assertEqual(fmt(4, self.theme, kind="currency", prefix="\u20ac"), "\u20ac4")

    def test_median_handles_even_and_odd_groups(self):
        median = build.figures._median
        self.assertEqual(median([3, 1, 2]), 2)
        self.assertAlmostEqual(median([0.62, 0.66, 0.68, 0.70, 0.64, 0.71]), 0.67)
        svg = build.figures.strip_plot(self.theme, {"Group": [1, 2, 3, 4]}, id="t-strip")
        self.assertIn("median 2.5", svg)

    def test_lines_break_at_missing_values(self):
        sparkline = build.figures.sparkline(self.theme, [None, 1, 2, None, 3])
        path = re.search(r'<path d="([^"]+)"', sparkline)[1]
        self.assertTrue(path.startswith("M"), path)
        self.assertEqual(path.count("M"), 2, path)
        line = build.figures.line_chart(self.theme, ["a", "b", "c", "d"], {"x": [1, None, 2, 3]}, id="t-line", focus="x")
        self.assertEqual(re.search(r'<path d="([^"]+)"', line)[1].count("M"), 2)

    def test_figure_is_named_by_its_finding_not_its_source(self):
        html_text = build.figures.figure("Feed leads", "Share of use, %", "<svg></svg>", "Source: USDA")
        structure = DocumentStructure()
        structure.feed(html_text)
        figure_label = re.search(r'<figure[^>]*aria-labelledby="([^"]+)"', html_text)[1]
        self.assertIn(figure_label, structure.ids)
        self.assertIn(f'id="{figure_label}">Feed leads<', html_text)
        self.assertEqual(html_text, build.figures.figure("Feed leads", "Share of use, %", "<svg></svg>", "Source: USDA"))

    def test_table_marks_numeric_columns_and_focus_row(self):
        rendered = build.figures.table(["Week", "Sales (t)"], [("W1", "10"), ("W2", "12")], numeric=(1,), focus_row=1)
        self.assertEqual(rendered.count('class="num"'), 3)  # the header cell and both body cells
        self.assertIn('<tr class="focus"><th scope="row">W2</th>', rendered)


if __name__ == "__main__":
    unittest.main()
