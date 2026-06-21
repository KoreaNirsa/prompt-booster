import json
from pathlib import Path
import unittest

from prompt_booster import analyze_intent, optimize_prompt


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "core_samples.json"
REQUIRED_FIXTURE_IDS = {
    "jwt-login",
    "board-design",
    "rag-chatbot",
    "generic-refactoring",
    "shopping-mall",
}


def load_core_fixtures():
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return payload["fixtures"]


class CoreSampleFixtureTest(unittest.TestCase):
    def test_core_fixture_file_contains_required_samples(self):
        fixtures = load_core_fixtures()

        self.assertEqual(REQUIRED_FIXTURE_IDS, {fixture["id"] for fixture in fixtures})

    def test_core_fixtures_document_expected_behavior(self):
        for fixture in load_core_fixtures():
            with self.subTest(fixture=fixture["id"]):
                self.assertTrue(fixture["name"])
                self.assertTrue(fixture["expectedBehavior"])
                self.assertTrue(fixture["minimumSections"])

    def test_core_fixtures_match_expected_intent_and_category(self):
        for fixture in load_core_fixtures():
            with self.subTest(fixture=fixture["id"]):
                result = analyze_intent(fixture["sourceText"])

                self.assertFalse(result.fallback.used)
                self.assertEqual(fixture["expectedIntent"], result.intent.value)
                self.assertEqual(fixture["expectedCategory"], result.category.value)

    def test_core_fixtures_keep_minimum_rendered_sections(self):
        for fixture in load_core_fixtures():
            with self.subTest(fixture=fixture["id"]):
                result = optimize_prompt(fixture["sourceText"])

                self.assertTrue(result.ok)
                self.assertEqual(fixture["expectedIntent"], result.analysis.intent.value)
                self.assertEqual(fixture["expectedCategory"], result.analysis.category.value)
                for section in fixture["minimumSections"]:
                    self.assertIn(f"## {section}", result.rendered_prompt)


if __name__ == "__main__":
    unittest.main()
