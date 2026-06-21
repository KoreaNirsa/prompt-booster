import unittest

from prompt_booster import Category, IntentType, analyze_intent


class IntentAnalyzerTest(unittest.TestCase):
    def assert_classification(self, text, intent, category):
        result = analyze_intent(text)

        self.assertEqual(intent, result.intent)
        self.assertEqual(category, result.category)
        self.assertGreater(result.confidence, 0)
        self.assertFalse(result.fallback.used)
        self.assertTrue(result.matched_signals)

    def test_korean_implementation_trigger_maps_to_code_generation(self):
        self.assert_classification(
            "JWT 로그인 구현해줘",
            IntentType.CODE_GENERATION,
            Category.BACKEND,
        )

    def test_korean_make_trigger_maps_to_code_generation(self):
        self.assert_classification(
            "React 대시보드 만들어줘",
            IntentType.CODE_GENERATION,
            Category.FRONTEND,
        )

    def test_korean_design_trigger_maps_to_system_design(self):
        self.assert_classification(
            "게시판 설계해줘",
            IntentType.SYSTEM_DESIGN,
            Category.ARCHITECTURE,
        )

    def test_korean_refactoring_trigger_maps_to_refactoring(self):
        self.assert_classification(
            "서비스 코드 리팩토링 해줘",
            IntentType.REFACTORING,
            Category.BACKEND,
        )

    def test_english_representative_requests_are_classified(self):
        cases = [
            ("Fix API error handling bug", IntentType.DEBUGGING, Category.BACKEND),
            ("Write unit tests for login API", IntentType.TEST_GENERATION, Category.BACKEND),
            ("Deploy Docker service with GitHub Actions", IntentType.DEVOPS, Category.DEVOPS),
            ("Design Clean Architecture module boundaries", IntentType.ARCHITECTURE, Category.ARCHITECTURE),
            ("Implement RAG chatbot", IntentType.CODE_GENERATION, Category.AI),
        ]

        for text, intent, category in cases:
            with self.subTest(text=text):
                self.assert_classification(text, intent, category)

    def test_output_contains_serializable_analysis_fields(self):
        payload = analyze_intent("RAG 챗봇 구현해줘").to_dict()

        self.assertEqual("code_generation", payload["intent"])
        self.assertEqual("ai", payload["category"])
        self.assertIn("matchedSignals", payload)
        self.assertIn("confidence", payload)
        self.assertIn("fallback", payload)

    def test_ambiguous_input_returns_safe_fallback(self):
        result = analyze_intent("해주세요")

        self.assertIsNone(result.intent)
        self.assertIsNone(result.category)
        self.assertEqual(0.0, result.confidence)
        self.assertTrue(result.fallback.used)
        self.assertEqual("no_supported_signal", result.fallback.reason)
        self.assertEqual((), result.matched_signals)


if __name__ == "__main__":
    unittest.main()
