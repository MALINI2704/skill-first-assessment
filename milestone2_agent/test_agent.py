"""
test_agent.py - Unit tests and determinism evaluation for AI Agent.

Verifies:
1. Tool usage and grounding.
2. Anti-hallucination guardrail when data is genuinely missing.
3. Consistency test: checking the agent gives the exact same answer twice in a row.
"""

import unittest
from agent import AIAgent


class TestAIAgent(unittest.TestCase):

    def setUp(self):
        self.agent = AIAgent(temperature=0.0, seed=42)

    def test_valid_tool_invocation_and_grounding(self):
        """Test that the agent invokes the tool and uses its data."""
        res = self.agent.ask("What is the status of ORD-101?")
        self.assertEqual(res["tool_invoked"], "get_order_status")
        self.assertTrue(res["grounded"])
        self.assertIn("Aarav Sharma", res["answer"])
        self.assertIn("Shipped", res["answer"])
        self.assertIn("BlueDart", res["answer"])

    def test_anti_hallucination_on_missing_data(self):
        """
        Test that when an order does not exist in the database,
        the agent does NOT fabricate customer names or dates.
        """
        res = self.agent.ask("Can you track order ORD-999 for me?")
        self.assertEqual(res["tool_invoked"], "get_order_status")
        self.assertFalse(res["grounded"])
        self.assertIn("Information Unavailable", res["answer"])
        self.assertIn("will not speculate", res["answer"])

    def test_out_of_scope_query_rejection(self):
        """Test that general knowledge outside tool capabilities is rejected."""
        res = self.agent.ask("Tell me a recipe for chocolate cake.")
        self.assertIsNone(res["tool_invoked"])
        self.assertFalse(res["grounded"])
        self.assertIn("do not have access to tools or data", res["answer"])

    def test_consistency_same_answer_twice_in_a_row(self):
        """
        Test that identical prompts produce 100% identical responses twice in a row (determinism test).
        """
        query = "What is the delivery fee for 5 kg over 120 km?"
        
        # Run 1
        res1 = self.agent.ask(query)
        # Run 2
        res2 = self.agent.ask(query)

        # 1. Exact string match verification
        self.assertEqual(res1["answer"], res2["answer"], "Outputs must match identically on consecutive runs.")
        # 2. Tool invocations match
        self.assertEqual(res1["tool_invoked"], res2["tool_invoked"])
        self.assertEqual(res1["tool_arguments"], res2["tool_arguments"])
        # 3. Tool output matches
        self.assertEqual(res1["tool_output"], res2["tool_output"])

    def test_consecutive_consistency_under_multiple_runs(self):
        """Extended consistency check over 5 runs."""
        query = "Do we have any Keychron K2 keyboards left?"
        answers = [self.agent.ask(query)["answer"] for _ in range(5)]
        
        # Check all answers are identical to the first
        for idx, ans in enumerate(answers):
            self.assertEqual(ans, answers[0], f"Run {idx + 1} diverged from baseline.")


if __name__ == "__main__":
    unittest.main()
