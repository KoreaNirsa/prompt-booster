import unittest

from prompt_booster import plan_prompt_execution


class ExecutionPlanTest(unittest.TestCase):
    def test_render_only_mode_exposes_rendered_prompt_without_execution_input(self):
        plan = plan_prompt_execution("JWT 로그인 만들어줘", target="codex")
        payload = plan.to_dict()

        self.assertEqual("render_only", payload["mode"])
        self.assertEqual("render_only", payload["status"])
        self.assertFalse(payload["executionReady"])
        self.assertIsInstance(payload["renderedPrompt"], str)
        self.assertIsNone(payload["executionInput"])
        self.assertEqual([], payload["requiredQuestions"])

    def test_auto_execute_blocks_when_business_scope_answer_is_missing(self):
        plan = plan_prompt_execution("쇼핑몰 만들어줘", target="codex", mode="auto_execute")
        payload = plan.to_dict()

        self.assertEqual("blocked", payload["status"])
        self.assertFalse(payload["executionReady"])
        self.assertIsNone(payload["renderedPrompt"])
        self.assertIsNone(payload["executionInput"])
        self.assertEqual("required_clarification_missing", payload["blockedReasons"][0]["code"])
        self.assertEqual(["business_scope"], [question["topic"] for question in payload["requiredQuestions"]])
        self.assertGreaterEqual(len(payload["requiredQuestions"][0]["examples"]), 2)

    def test_auto_execute_blocks_existing_high_impact_questions(self):
        plan = plan_prompt_execution("JWT 로그인 구현해줘", target="codex", mode="auto_execute")
        payload = plan.to_dict()

        self.assertEqual("blocked", payload["status"])
        self.assertEqual(["auth_scope"], [question["topic"] for question in payload["requiredQuestions"]])
        self.assertIn("로그인과 토큰 발급만 포함", payload["requiredQuestions"][0]["examples"])

    def test_auto_execute_returns_agent_execution_input_when_required_answers_exist(self):
        plan = plan_prompt_execution(
            "쇼핑몰 만들어줘",
            target="codex",
            mode="auto_execute",
            clarification_answers={"business_scope": "주문 생성까지 포함하고 결제는 제외"},
        )
        payload = plan.to_dict()
        execution_input = payload["executionInput"]

        self.assertEqual("ready", payload["status"])
        self.assertTrue(payload["executionReady"])
        self.assertIsNone(payload["renderedPrompt"])
        self.assertEqual([], payload["requiredQuestions"])
        self.assertEqual("codex", execution_input["target"])
        self.assertIn("Codex", execution_input["prompt"])
        self.assertIn("주문 생성까지 포함하고 결제는 제외", execution_input["prompt"])
        self.assertEqual("forbidden", execution_input["executionPolicy"]["businessLogicGuessing"])
        self.assertTrue(execution_input["executionPolicy"]["requiresAllRequiredClarifications"])
        self.assertEqual("business_scope", execution_input["clarificationAnswers"][0]["topic"])

    def test_auto_execute_limits_questions(self):
        plan = plan_prompt_execution("쇼핑몰 결제 외부 연동 배포까지 구현해줘", target="codex", mode="auto_execute")
        payload = plan.to_dict()

        self.assertEqual("blocked", payload["status"])
        self.assertLessEqual(len(payload["requiredQuestions"]), 3)
        self.assertEqual(
            ["payment", "deployment", "external_integration"],
            [question["topic"] for question in payload["requiredQuestions"]],
        )


if __name__ == "__main__":
    unittest.main()
