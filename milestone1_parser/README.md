# Milestone 1: Structured CSS Parser

A lightweight, zero-dependency CSS parser in Python that transforms raw CSS into clean, structured JSON format.

---

## 📝 Written Submission 

> **What we chose to extract and why:**  
> We extracted normalized rule-sets (individual selectors grouped cleanly as arrays), property-value declaration mappings, recursive at-rules (e.g., `@media`), and an aggregated metadata summary (including detected CSS custom properties `--*`). This enables downstream tools to easily query specific selectors, validate design tokens, calculate specificity, or perform dead-code analysis without dealing with raw string parsing.
>
> **Edge Case Thought About:**  
> A critical edge case handled is string literals containing semicolons or colons—specifically inside `url(...)` definitions (e.g. `background: url('https://example.com/asset?a=1;b=2')`). A naive parser splitting on `;` or `:` breaks such URLs into invalid properties; our state-aware token scanner tracks quote and URL scopes to prevent splitting inside literal values. Additionally, it cleanly strips comments (`/* ... */`) and handles rules where the final semicolon before a closing brace `}` is omitted.

---

## 🚀 How to Run

### 1. Run Parser on Sample File
```bash
python css_parser.py sample.css
```

### 2. Run Automated Unit Tests
```bash
python test_parser.py
```
*(Runs 7 comprehensive test cases verifying selectors, declarations, URLs, comments, media queries, and missing semicolons)*

---

## 📊 Sample Output Structure
```json
{
  "summary": {
    "total_rules": 6,
    "total_declarations": 19,
    "unique_selectors_count": 9,
    "unique_selectors": [".button:focus", ".card", ":root", "body", "html"],
    "css_variables_found": ["--brand-primary", "--brand-secondary", "--card-radius"]
  },
  "rules": [
    {
      "type": "rule",
      "selectors": [".card", ".panel"],
      "declarations": {
        "padding": "24px",
        "border": "1px solid #e2e8f0"
      }
    }
  ]
}
```
