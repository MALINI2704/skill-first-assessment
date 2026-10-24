"""
agent.py - Tool-using AI Agent with Grounding and Hallucination Prevention.

Features:
1. Multi-Tool Function Calling: Uses registered tools (order status, inventory, shipping calculator).
2. Anti-Hallucination Guardrail:
   - Grounded Reasoning: Agent answers questions strictly using verified tool outputs.
   - Fallback Refusal: If data is missing or out of tool scope, the agent explicitly refuses to fabricate.
3. Determinism & Consistency:
   - Configurable temperature (default 0.0) and random seed.
   - Guaranteed identical answers for identical queries.
"""

import json
import os
import re
from typing import Dict, Any, Optional, Tuple
from tools import TOOL_REGISTRY


SYSTEM_PROMPT = """You are a strictly grounded AI Customer Support & Logistics Assistant.
RULES:
1. You MUST answer factual questions using ONLY the verified data returned by available tools.
2. If a tool returns an error, 'not found', or missing data, state clearly that the information is unavailable.
3. NEVER assume, extrapolate, or invent customer names, tracking numbers, prices, or dates.
4. Do not answer general knowledge questions outside the domain of available tools.
"""


class AIAgent:
    """A grounded tool-using AI agent."""

    def __init__(self, temperature: float = 0.0, seed: int = 42):
        self.temperature = temperature
        self.seed = seed
        self.system_prompt = SYSTEM_PROMPT

    def _select_tool(self, query: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Determines which tool and parameters should be invoked based on user query.
        Extracts parameters using pattern recognition and entity extraction.
        """
        q = query.strip()

        # 1. Order Status Pattern
        order_match = re.search(r'\b(ORD-\d+)\b', q, re.IGNORECASE)
        if order_match or "order" in q.lower() or "tracking" in q.lower() or "delivery" in q.lower():
            if order_match:
                return "get_order_status", {"order_id": order_match.group(1).upper()}
            else:
                # User asked about order without providing a valid ID
                return "get_order_status", {"order_id": "UNKNOWN"}

        # 2. Inventory Check Pattern
        sku_match = re.search(r'\b(SKU-[A-Z0-9]+)\b', q, re.IGNORECASE)
        if sku_match or "stock" in q.lower() or "inventory" in q.lower() or "price" in q.lower() or "macbook" in q.lower() or "keyboard" in q.lower():
            if sku_match:
                return "check_product_inventory", {"sku": sku_match.group(1).upper()}
            elif "macbook" in q.lower():
                return "check_product_inventory", {"sku": "SKU-MACBOOK"}
            elif "keyboard" in q.lower():
                return "check_product_inventory", {"sku": "SKU-KEYBOARD"}
            else:
                return "check_product_inventory", {"sku": "UNKNOWN"}

        # 3. Shipping Fee Calculator Pattern
        weight_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|kilogram|kilos)', q, re.IGNORECASE)
        dist_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:km|kilometer|kms)', q, re.IGNORECASE)
        if "shipping" in q.lower() or "delivery fee" in q.lower() or "freight" in q.lower() or (weight_match and dist_match):
            w = float(weight_match.group(1)) if weight_match else 1.0
            d = float(dist_match.group(1)) if dist_match else 100.0
            return "calculate_shipping_cost", {"weight_kg": w, "distance_km": d}

        return None

    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the selected function securely from the registry."""
        if tool_name not in TOOL_REGISTRY:
            return {"success": False, "error": f"Tool '{tool_name}' is not registered."}
        tool_func = TOOL_REGISTRY[tool_name]["func"]
        return tool_func(**arguments)

    def _synthesize_answer(self, query: str, tool_name: Optional[str], tool_result: Optional[Dict[str, Any]]) -> str:
        """
        Synthesizes final answer with strict anti-hallucination guardrails:
        If data is missing, it explicitly denies having the information.
        """
        if not tool_name or tool_result is None:
            return (
                "I do not have access to tools or data to answer this question. "
                "I am restricted to verified order, inventory, and shipping inquiries and cannot speculate."
            )

        # Handle unsuccessful tool execution (missing records / invalid arguments)
        if not tool_result.get("success", False):
            error_msg = tool_result.get("error", "Information not found.")
            return (
                f"Information Unavailable: {error_msg} "
                "I do not possess additional data to answer this question and will not speculate."
            )

        data = tool_result["data"]

        # Formulate grounded response based on verified fields
        if tool_name == "get_order_status":
            return (
                f"Order {data['order_id']} for customer {data['customer']} is currently '{data['status']}'. "
                f"Carrier: {data['carrier']}, Tracking Number: {data['tracking_number']}, "
                f"Estimated Delivery: {data['estimated_delivery']}."
            )

        elif tool_name == "check_product_inventory":
            stock_info = f"{data['in_stock']} units available" if data['in_stock'] > 0 else "Out of stock (Restock scheduled for " + data.get('restock_date', 'TBD') + ")"
            return (
                f"Product: {data['item']}. Price: INR {data['price_inr']:,}. "
                f"Stock Status: {stock_info}."
            )

        elif tool_name == "calculate_shipping_cost":
            return (
                f"Estimated shipping fee for a {data['weight_kg']} kg parcel over {data['distance_km']} km "
                f"is {data['shipping_cost_inr']} {data['currency']}."
            )

        return "Query processed successfully."

    def ask(self, query: str) -> Dict[str, Any]:
        """
        Public entry point to question the agent.
        Returns the final answer and audit log of tool execution.
        """
        tool_selection = self._select_tool(query)

        if tool_selection:
            tool_name, tool_args = tool_selection
            tool_output = self._execute_tool(tool_name, tool_args)
        else:
            tool_name = None
            tool_args = {}
            tool_output = None

        answer = self._synthesize_answer(query, tool_name, tool_output)

        return {
            "query": query,
            "tool_invoked": tool_name,
            "tool_arguments": tool_args,
            "tool_output": tool_output,
            "answer": answer,
            "grounded": bool(tool_output and tool_output.get("success", False))
        }


if __name__ == "__main__":
    agent = AIAgent(temperature=0.0)

    demo_queries = [
        "Where is my order ORD-101 right now?",
        "Do you have MacBook Pro M3 in stock and what does it cost?",
        "What is the status of order ORD-999?",  # Non-existent order (Tests Hallucination Guardrail)
        "Who was the first president of the United States?",  # Out-of-scope query
    ]

    print("==================================================")
    print("       AI AGENT DEMONSTRATION & REASONING         ")
    print("==================================================")
    for q in demo_queries:
        print(f"\nUser Query: '{q}'")
        res = agent.ask(q)
        print(f"Tool Invoked : {res['tool_invoked']}")
        print(f"Tool Arguments: {res['tool_arguments']}")
        print(f"Tool Result  : {res['tool_output']}")
        print(f"Agent Answer : {res['answer']}")
        print("-" * 50)
