import unittest

from prompt_booster import AdaptiveGrillMe, analyze_intent, optimize_prompt


class AdaptiveGrillMeTest(unittest.TestCase):
    def test_broad_default_requests_do_not_generate_questions(self):
        for text in ("쇼핑몰 만들어줘", "게시판 만들어줘"):
            with self.subTest(text=text):
                result = optimize_prompt(text)

                self.assertTrue(result.ok)
                self.assertEqual((), result.clarification_questions)
                self.assertEqual([], result.to_dict()["clarificationQuestions"])

    def test_high_impact_backend_uncertainties_generate_limited_questions(self):
        result = optimize_prompt("쇼핑몰 결제 외부 연동 배포까지 구현해줘")
        topics = [question.topic for question in result.clarification_questions]

        self.assertTrue(result.ok)
        self.assertLessEqual(len(result.clarification_questions), 3)
        self.assertEqual(["payment", "deployment", "external_integration"], topics)
        for question in result.clarification_questions:
            self.assertTrue(question.question)
            self.assertTrue(question.reason)
            self.assertGreaterEqual(len(question.examples), 2)

    def test_framework_and_persistence_questions_use_detected_category(self):
        analysis = analyze_intent("API 데이터 저장 구현해줘")
        questions = AdaptiveGrillMe().generate("API 데이터 저장 구현해줘", analysis)

        self.assertEqual("backend", analysis.category.value)
        self.assertEqual(["framework", "persistence"], [question.topic for question in questions])
        self.assertIn("backend", questions[0].reason)

    def test_auth_scope_question_is_specific_and_structured(self):
        result = optimize_prompt("JWT 로그인 구현해줘")

        self.assertTrue(result.ok)
        self.assertEqual(("auth_scope",), tuple(question.topic for question in result.clarification_questions))
        payload = result.to_dict()["clarificationQuestions"][0]
        self.assertEqual("Q-AUTH-SCOPE", payload["id"])
        self.assertIn("API 범위", payload["question"])
        self.assertIn("로그인과 토큰 발급만 포함", payload["examples"])

    def test_questions_are_generated_before_rendering(self):
        result = optimize_prompt("쇼핑몰 결제 기능 구현해줘")

        self.assertLess(
            result.pipeline_steps.index("generate_clarification_questions"),
            result.pipeline_steps.index("render_prompt"),
        )
        self.assertEqual("payment", result.clarification_questions[0].topic)

    def test_unclassified_input_does_not_generate_questions(self):
        result = optimize_prompt("Please help with something complicated")

        self.assertFalse(result.ok)
        self.assertEqual((), result.clarification_questions)


if __name__ == "__main__":
    unittest.main()
