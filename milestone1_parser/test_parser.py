"""
test_parser.py - Unit tests for CSS Parser verifying correctness and edge cases.
"""

import unittest
from css_parser import parse_css, parse_css_file


class TestCSSParser(unittest.TestCase):

    def test_basic_rule_parsing(self):
        css = "h1 { color: red; font-size: 24px; }"
        res = parse_css(css)
        self.assertEqual(res["summary"]["total_rules"], 1)
        self.assertEqual(res["rules"][0]["selectors"], ["h1"])
        self.assertEqual(res["rules"][0]["declarations"]["color"], "red")
        self.assertEqual(res["rules"][0]["declarations"]["font-size"], "24px")

    def test_multiple_grouped_selectors(self):
        css = "h1, h2, .title, a:hover { color: blue; }"
        res = parse_css(css)
        self.assertEqual(res["rules"][0]["selectors"], ["h1", "h2", ".title", "a:hover"])

    def test_edge_case_url_with_semicolon_and_colons(self):
        # Naive split(';') or split(':') will corrupt this URL
        css = "div { background: url('https://example.com/api?id=1;format=json'); }"
        res = parse_css(css)
        self.assertEqual(
            res["rules"][0]["declarations"]["background"],
            "url('https://example.com/api?id=1;format=json')"
        )

    def test_edge_case_comments_stripped_safely(self):
        css = """
        /* Top-level comment */
        .box {
            /* Property comment */
            padding: 10px; /* Inline comment */
            margin: 20px;
        }
        """
        res = parse_css(css)
        self.assertEqual(res["summary"]["total_rules"], 1)
        self.assertEqual(res["rules"][0]["declarations"], {"padding": "10px", "margin": "20px"})

    def test_edge_case_missing_trailing_semicolon(self):
        # Valid CSS allows omitting the semicolon on the last declaration before '}'
        css = "p { color: green; font-weight: bold }"
        res = parse_css(css)
        self.assertEqual(res["rules"][0]["declarations"]["color"], "green")
        self.assertEqual(res["rules"][0]["declarations"]["font-weight"], "bold")

    def test_nested_media_query(self):
        css = """
        @media (max-width: 600px) {
            .mobile-hide { display: none; }
            .mobile-full { width: 100%; }
        }
        """
        res = parse_css(css)
        self.assertEqual(len(res["rules"]), 1)
        self.assertEqual(res["rules"][0]["type"], "at-rule")
        self.assertEqual(res["rules"][0]["name"], "@media (max-width: 600px)")
        self.assertEqual(len(res["rules"][0]["rules"]), 2)
        self.assertEqual(res["rules"][0]["rules"][0]["selectors"], [".mobile-hide"])
        self.assertEqual(res["rules"][0]["rules"][0]["declarations"]["display"], "none")

    def test_css_variables_and_summary_stats(self):
        css = """
        :root {
            --primary: #ff0000;
            --secondary: #00ff00;
        }
        button {
            background-color: var(--primary);
        }
        """
        res = parse_css(css)
        self.assertEqual(res["summary"]["total_rules"], 2)
        self.assertIn("--primary", res["summary"]["css_variables_found"])
        self.assertIn("--secondary", res["summary"]["css_variables_found"])


if __name__ == "__main__":
    unittest.main()
