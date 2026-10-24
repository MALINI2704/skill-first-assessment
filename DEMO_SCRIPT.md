# 🎬 Demo Video Walkthrough Script (2–3 Minutes)

This script is designed for your screen-recording demo video submission to **products@skillfirstlabs.com**.

> **Recommended Tool**: Use [Loom](https://www.loom.com/) (free) or OBS Studio or Windows Game Bar (`Win + Alt + R`).
> Keep your code editor and terminal open side-by-side.

---

### ⏱️ Timeline & Script

#### 1. Introduction (15 Seconds)
- **On Screen**: Show the project folder structure in your editor/terminal.
- **What to Say**:
  > *"Hi team, this is my submission for the Skill First Labs technical assessment. Today I'll quickly walk you through Milestone 1, our structured CSS parser, and Milestone 2, our tool-grounded AI agent."*

---

#### 2. Milestone 1: CSS Parser Walkthrough (45–60 Seconds)
- **On Screen**: 
  1. Open `milestone1_parser/css_parser.py` briefly.
  2. Run the command: `python test_parser.py` (shows 7 tests passing).
  3. Run the command: `python css_parser.py sample.css` (shows the formatted JSON output).
- **What to Say**:
  > *"For Milestone 1, instead of just splitting text naively, the parser constructs a clean AST. We extract three key things: first, individual normalized selectors grouped in an array; second, property-value declaration dictionaries; and third, nested at-rules like media queries, alongside design token metadata like CSS variables.*
  > 
  > *Why extract this? Because downstream tools can immediately query selectors, calculate specificity, or validate design tokens without regex parsing.*
  > 
  > *For edge cases, a major challenge in CSS is URLs containing semicolons or colons—such as background URLs with query parameters—and multi-line comments. Naive splitters break on these. Our parser uses a state-aware scanner that respects quote scopes and URL boundaries, and also handles omitted trailing semicolons before closing braces. As you can see, all 7 unit tests pass."*

---

#### 3. Milestone 2: AI Agent with Tools Walkthrough (60 Seconds)
- **On Screen**:
  1. Open `milestone2_agent/agent.py` and `tools.py`.
  2. Run the command: `python test_agent.py` (shows 5 tests passing).
  3. Run the command: `python agent.py` (shows the live demo output).
- **What to Say**:
  > *"For Milestone 2, we built an AI agent connected to three real functions: an order status lookup, an inventory checker, and a shipping calculator. The agent does not guess from internal parametric memory; it acts only on verified tool outputs.*
  > 
  > *To answer the two specific evaluation questions:*
  > *First, how do we make sure it doesn't make up an answer when data is missing? We enforce strict tool grounding. The synthesis layer is constrained to facts present in the tool's JSON return. When an order doesn't exist—like order ORD-999—the tool flags it as not found, and the agent triggers an explicit refusal stating information is unavailable rather than hallucinating.*
  > 
  > *Second, how do we check it gives the same answer twice in a row? We ensure determinism by pinning temperature to 0.0 and setting a fixed random seed. In test_agent.py, we have an automated consistency test that runs identical prompts back-to-back and asserts exact string equality across runs. As shown in the terminal, all 5 agent test cases pass."*

---

#### 4. Conclusion (15 Seconds)
- **On Screen**: Show the clean GitHub repository or master README.
- **What to Say**:
  > *"Both milestones are fully modular, zero-dependency, and well-tested. Thank you for your time and looking forward to the next steps!"*

---

### 📩 Submission Checklist
1. **GitHub URL**: The GitHub repository link (to be submitted via the URL Skill First Labs provides tomorrow).
2. **Video Email**: Send Loom link or attached video to `products@skillfirstlabs.com` before **8:00 PM today**.
