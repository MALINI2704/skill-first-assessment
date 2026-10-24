"""
css_parser.py - A lightweight, robust CSS parser that extracts structured information.

What it extracts:
1. Selectors: Cleaned and normalized list of selectors per rule block (e.g., ['h1', 'h2.title']).
2. Declarations: Key-value dictionary of style properties and values (e.g., {'color': '#333'}).
3. At-rules: Nested blocks such as @media, @supports, preserving rule hierarchy.
4. Summary Insights: Rule counts, unique selectors, and extracted CSS design tokens/variables (--*).

Edge cases handled:
- Comments (/* ... */) cleanly stripped without breaking quoted strings.
- URLs and quoted strings containing colons or semicolons (e.g., background: url('https://domain.com/img.png?a=1;b=2')).
- Missing trailing semicolons on final declarations before closing brace.
- Grouped/comma-separated selectors with whitespace trimmed.
- Nested media query blocks parsed recursively.
"""

import json
import re
import sys
from typing import Dict, List, Any, Tuple


class CSSParser:
    """Parses CSS text into structured data structures."""

    def __init__(self, css_text: str):
        self.raw_css = css_text
        self.clean_css = self._remove_comments(css_text)

    @staticmethod
    def _remove_comments(text: str) -> str:
        """
        Removes CSS comments (/* ... */) while protecting strings containing comment-like markers.
        """
        pattern = r'(/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')'

        def replace_fn(match):
            token = match.group(0)
            if token.startswith("/*"):
                return " "
            return token

        return re.sub(pattern, replace_fn, text)

    def _split_declarations(self, block: str) -> Dict[str, str]:
        """
        Parses the content between braces into property: value pairs.
        Handles semicolons and colons inside quotes and url() properly.
        """
        declarations: Dict[str, str] = {}
        in_single_quote = False
        in_double_quote = False
        in_url = False
        current_token: List[str] = []
        tokens: List[str] = []

        i = 0
        while i < len(block):
            ch = block[i]

            # Track quotes
            if ch == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
            elif ch == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
            elif not in_single_quote and not in_double_quote:
                if block[i:i+4].lower() == "url(":
                    in_url = True
                elif in_url and ch == ")":
                    in_url = False

            # Semicolon separates declarations when outside quotes/url
            if ch == ";" and not in_single_quote and not in_double_quote and not in_url:
                decl_str = "".join(current_token).strip()
                if decl_str:
                    tokens.append(decl_str)
                current_token = []
            else:
                current_token.append(ch)
            i += 1

        # Catch trailing declaration missing a semicolon
        remaining = "".join(current_token).strip()
        if remaining:
            tokens.append(remaining)

        for token in tokens:
            if ":" in token:
                prop, val = token.split(":", 1)
                prop_clean = prop.strip()
                val_clean = val.strip()
                if prop_clean and val_clean:
                    declarations[prop_clean] = val_clean

        return declarations

    def _split_selectors(self, selector_text: str) -> List[str]:
        """
        Splits comma-separated selectors, respecting commas within pseudo-class parentheses.
        Example: "h1, div.card, a:is(.active, .hover)" -> ['h1', 'div.card', 'a:is(.active, .hover)']
        """
        selectors: List[str] = []
        current: List[str] = []
        paren_depth = 0
        in_single = False
        in_double = False

        for ch in selector_text:
            if ch == "'" and not in_double:
                in_single = not in_single
            elif ch == '"' and not in_single:
                in_double = not in_double
            elif not in_single and not in_double:
                if ch == "(":
                    paren_depth += 1
                elif ch == ")":
                    paren_depth = max(0, paren_depth - 1)
                elif ch == "," and paren_depth == 0:
                    sel = "".join(current).strip()
                    if sel:
                        selectors.append(sel)
                    current = []
                    continue
            current.append(ch)

        final_sel = "".join(current).strip()
        if final_sel:
            selectors.append(final_sel)

        return selectors

    def _parse_blocks(self, content: str) -> List[Dict[str, Any]]:
        """
        Extracts rule blocks and nested at-rules (@media, @supports, etc.).
        """
        rules: List[Dict[str, Any]] = []
        i = 0
        length = len(content)

        while i < length:
            # Skip leading whitespace
            while i < length and content[i].isspace():
                i += 1
            if i >= length:
                break

            # Find the opening brace '{'
            header_chars = []
            while i < length and content[i] != "{":
                header_chars.append(content[i])
                i += 1

            if i >= length:
                # Trailing content without opening brace (e.g. malformed or standalone at-rule like @charset)
                header = "".join(header_chars).strip()
                if header.startswith("@") and header.endswith(";"):
                    rules.append({
                        "type": "directive",
                        "raw": header
                    })
                break

            header = "".join(header_chars).strip()
            i += 1  # step over '{'

            # Now find matching closing brace '}' considering nested blocks and quotes
            brace_depth = 1
            body_chars = []
            in_single = False
            in_double = False

            while i < length and brace_depth > 0:
                ch = content[i]
                if ch == "'" and not in_double:
                    in_single = not in_single
                elif ch == '"' and not in_single:
                    in_double = not in_double
                elif not in_single and not in_double:
                    if ch == "{":
                        brace_depth += 1
                    elif ch == "}":
                        brace_depth -= 1
                        if brace_depth == 0:
                            i += 1
                            break
                body_chars.append(ch)
                i += 1

            body = "".join(body_chars).strip()

            # Process block according to header type
            if header.startswith("@"):
                # Nested at-rule (like @media, @supports, @keyframes)
                rules.append({
                    "type": "at-rule",
                    "name": header,
                    "rules": self._parse_blocks(body)
                })
            else:
                selectors = self._split_selectors(header)
                declarations = self._split_declarations(body)
                if selectors or declarations:
                    rules.append({
                        "type": "rule",
                        "selectors": selectors,
                        "declarations": declarations
                    })

        return rules

    def parse(self) -> Dict[str, Any]:
        """
        Parses CSS and returns structured data and meta summary.
        """
        structured_rules = self._parse_blocks(self.clean_css)

        # Collect summary analytics
        all_selectors = []
        custom_props = set()
        total_declarations = 0

        def inspect_rules(rule_list):
            nonlocal total_declarations
            count = 0
            for r in rule_list:
                if r.get("type") == "rule":
                    count += 1
                    all_selectors.extend(r.get("selectors", []))
                    decls = r.get("declarations", {})
                    total_declarations += len(decls)
                    for prop in decls.keys():
                        if prop.startswith("--"):
                            custom_props.add(prop)
                elif r.get("type") == "at-rule":
                    nested_count = inspect_rules(r.get("rules", []))
                    count += nested_count
            return count

        total_rules = inspect_rules(structured_rules)
        unique_selectors = sorted(list(set(all_selectors)))

        return {
            "summary": {
                "total_rules": total_rules,
                "total_declarations": total_declarations,
                "unique_selectors_count": len(unique_selectors),
                "unique_selectors": unique_selectors,
                "css_variables_found": sorted(list(custom_props))
            },
            "rules": structured_rules
        }


def parse_css(css_text: str) -> Dict[str, Any]:
    """Helper function to parse raw CSS string."""
    return CSSParser(css_text).parse()


def parse_css_file(file_path: str) -> Dict[str, Any]:
    """Helper function to parse a CSS file from disk."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return parse_css(content)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        result = parse_css_file(target_file)
        print(json.dumps(result, indent=2))
    else:
        # Quick demonstration
        demo_css = """
        /* Main Application Theme */
        :root {
            --primary-color: #4f46e5;
            --font-stack: 'Inter', -apple-system, sans-serif;
        }

        body, html {
            margin: 0;
            padding: 0;
            background: url('https://example.com/asset?a=1;b=2');
        }

        @media (max-width: 768px) {
            .container, .card {
                padding: 12px;
                display: block
            }
        }
        """
        output = parse_css(demo_css)
        print(json.dumps(output, indent=2))
