# Skill First Labs — Technical Assessment Submission

This repository contains the complete implementation and test suites for both shortlisting milestones:
- **Milestone 1**: Structured CSS Parser
- **Milestone 2**: Tool-Grounded AI Agent

---

## 📁 Repository Structure
```
skill-first-assessment/
├── milestone1_parser/
│   ├── css_parser.py       # Main CSS parser implementation
│   ├── sample.css          # Real-world stylesheet for testing
│   ├── test_parser.py      # 7 unit tests covering edge cases
│   └── README.md           # Milestone 1 written answers & documentation
├── milestone2_agent/
│   ├── agent.py            # AI agent implementation with grounding
│   ├── tools.py            # Tool definitions (Order, Inventory, Shipping)
│   ├── test_agent.py       # 5 unit tests verifying grounding & consistency
│   └── README.md           # Milestone 2 written answers & documentation
├── DEMO_SCRIPT.md          # 2-3 minute walkthrough script for demo video
└── README.md               # Master project overview
```

---

## ⚡ Quick Start

### Milestone 1: CSS Parser
```bash
cd milestone1_parser
python test_parser.py            # Runs all 7 unit tests
python css_parser.py sample.css  # Parses sample.css to structured JSON
```

### Milestone 2: AI Agent
```bash
cd ../milestone2_agent
python test_agent.py             # Runs all 5 tests (including consistency tests)
python agent.py                  # Runs interactive demonstration of queries & guardrails
```

---

## 📋 Summary of Written Deliverables

### Milestone 1 — Parser
- **What was extracted and why**: We extracted normalized rule blocks (clean arrays of individual selectors), key-value declaration maps, recursive at-rules (`@media`), and aggregated metadata (including custom CSS `--*` variables). This allows downstream tools to analyze design tokens, calculate selector specificity, and perform dead-code detection without dealing with messy raw text.
- **Edge cases handled**: Handled quoted strings and URLs containing semicolons and colons (e.g., `background: url('https://example.com/asset?a=1;b=2')`), stripping of multi-line comments (`/* ... */`), grouped selector trimming, and optional omitted semicolons before the closing brace `}`.

### Milestone 2 — Agent
- **Preventing hallucination when data is missing**: Grounding is enforced by restricting answer synthesis exclusively to verified tool return payloads. If a tool returns an error or empty result (e.g., non-existent Order ID), or if the query falls outside tool capabilities, the agent invokes an explicit refusal fallback and declines to speculate.
- **Ensuring the same answer twice in a row (consistency)**: We pin model parameters to `temperature=0.0` (greedy token decoding), set a fixed random seed (`seed=42`), and maintain deterministic tool execution. Consistency is validated via automated test assertions (`res1["answer"] == res2["answer"]`) run consecutively across identical prompts.
