import unittest

from prompt_booster import PromptQualityScorer, analyze_intent, optimize_prompt


EXPECTED_CRITERIA = (
    "role",
    "requirement",
    "constraint",
    "context",
    "outputFormat",
    "validation",
    "technicalSpecificity",
)


class PromptQualityScorerTest(unittest.TestCase):
    def setUp(self):
        self.scorer = PromptQualityScorer()

    def score_source(self, source_text):
        return self.scorer.score_source_text(source_text, analyze_intent(source_text))

    def test_quality_score_uses_required_criteria(self):
        report = self.score_source("Implement JWT login API with tests")

        self.assertEqual(EXPECTED_CRITERIA, tuple(criterion.name for criterion in report.criteria))
        self.assertEqual(100, report.max)
        for criterion in report.criteria:
            self.assertGreaterEqual(criterion.score, 0)
            self.assertLessEqual(criterion.score, criterion.max)

    def test_low_quality_prompt_score_includes_missing_diagnostics(self):
        report = self.score_source("Build app")

        self.assertLessEqual(report.total, 39)
        self.assertGreaterEqual(report.total, 0)
        missing_fields = {diagnostic.field for diagnostic in report.diagnostics if diagnostic.severity == "missing"}
        self.assertIn("role", missing_fields)
        self.assertIn("constraint", missing_fields)
        self.assertIn("outputFormat", missing_fields)
        self.assertIn("validation", missing_fields)

    def test_medium_quality_prompt_score_has_partial_breakdown(self):
        report = self.score_source("Implement JWT login API with tests and error handling")

        self.assertGreaterEqual(report.total, 40)
        self.assertLessEqual(report.total, 79)
        weak_fields = {diagnostic.field for diagnostic in report.diagnostics if diagnostic.severity == "weak"}
        self.assertIn("context", weak_fields)
        self.assertIn("technicalSpecificity", weak_fields)

    def test_high_quality_prompt_score_reaches_high_boundary(self):
        report = self.score_source(
            "As a backend developer, implement a Spring Boot JWT login API with "
            "Access Token, Refresh Token, SecurityFilterChain, UserDetailsService, "
            "Controller, Service, Repository, DTO, exception handling, unit tests, "
            "integration tests, and return Markdown sections for project structure, "
            "core code, tests, and validation checklist."
        )

        self.assertGreaterEqual(report.total, 80)
        self.assertLessEqual(report.total, 100)
        self.assertEqual(10, self.criterion(report, "role").score)
        self.assertEqual(10, self.criterion(report, "outputFormat").score)
        self.assertEqual(10, self.criterion(report, "validation").score)

    def test_optimizer_scores_source_and_optimized_prompt(self):
        result = optimize_prompt("Implement JWT login API", target="codex")
        payload = result.to_dict()

        self.assertTrue(result.ok)
        self.assertIsNotNone(result.source_quality_score)
        self.assertIsNotNone(result.optimized_quality_score)
        self.assertGreater(result.optimized_quality_score.total, result.source_quality_score.total)
        self.assertEqual(result.optimized_quality_score.total, result.prompt_ir["qualityScore"]["total"])
        self.assertNotIn("diagnostics", result.prompt_ir["qualityScore"])
        self.assertIn("diagnostics", payload["sourceQualityScore"])
        self.assertIn("diagnostics", payload["optimizedQualityScore"])

    def criterion(self, report, name):
        for criterion in report.criteria:
            if criterion.name == name:
                return criterion
        self.fail(f"{name} criterion was not found")


if __name__ == "__main__":
    unittest.main()
