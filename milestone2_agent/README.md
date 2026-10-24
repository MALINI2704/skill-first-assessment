# Milestone 2: Tool-Grounded AI Agent

A deterministic AI agent that answers queries using verified function tools (order database, inventory lookups, shipping calculator) rather than internal parametric knowledge.

---

## 📝 Written Submission 

> **How we make sure it doesn't make up an answer when it genuinely doesn't have data:**  
> We enforce strict grounding by decoupling data retrieval from answer synthesis. The agent is governed by system-level constraints and an execution guardrail that only allows facts directly present in the tool's JSON output to appear in the answer. If a tool returns an error, null, or missing record (e.g. non-existent Order ID), or if the query falls outside registered tool capabilities, the agent triggers a deterministic fallback refusal stating that verified data is unavailable, explicitly forbidding extrapolation.
>
> **How we check it gives the same answer twice in a row:**  
> We enforce determinism by pinning model generation parameters (`temperature=0.0` for greedy token decoding, fixed random `seed=42`, and a static tool registry). To verify consistency programmatically, we run an automated evaluation test suite (`test_agent.py`) that sends identical prompts across consecutive executions and asserts exact string equality (`res1["answer"] == res2["answer"]`) alongside matching tool call metadata.

---

## 🛠️ Registered Tools
1. `get_order_status(order_id)`: Fetches order status, carrier, tracking number, and delivery date.
2. `check_product_inventory(sku)`: Fetches product price, stock availability, and warehouse location.
3. `calculate_shipping_cost(weight_kg, distance_km)`: Calculates logistics delivery fee based on parcel metrics.

---

## 🚀 How to Run

### 1. Run Interactive Agent Demo
```bash
python agent.py
```
*(Demonstrates tool dispatch, stock lookup, hallucination refusal on missing data, and out-of-scope query rejection)*

### 2. Run Automated Tests & Consistency Verifications
```bash
python test_agent.py
```
*(Runs 5 automated tests checking tool execution, anti-hallucination guardrail, and multi-run output determinism)*
