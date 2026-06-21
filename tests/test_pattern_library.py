import copy
import json
from pathlib import Path
import unittest

from prompt_booster import (
    PatternLibrary,
    PatternLibraryValidationError,
    analyze_intent,
    optimize_prompt,
)


ROOT = Path(__file__).resolve().parents[1]
PATTERN_PATH = ROOT / "patterns" / "core.json"
SCHEMA_PATH = ROOT / "schemas" / "prompt-pattern.schema.json"
EXPECTED_CATEGORIES = {"backend", "frontend", "ai", "devops", "architecture"}


def load_default_payload():
    return json.loads(PATTERN_PATH.read_text(encoding="utf-8"))


class PatternLibraryTest(unittest.TestCase):
    def test_schema_supports_required_categories(self):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

        self.assertEqual(EXPECTED_CATEGORIES, set(schema["$defs"]["PatternCategory"]["enum"]))

    def test_default_pattern_loads_and_resolves_prompt_defaults(self):
        library = PatternLibrary.load_default()
        pattern = library.get("backend.jwt-auth")
        defaults = pattern.to_prompt_defaults()

        self.assertEqual("backend", pattern.category)
        self.assertIn("jwt", pattern.keywords)
        self.assertEqual("mixed", defaults.output_spec["format"])
        self.assertGreaterEqual(len(defaults.requirements), 1)
        self.assertGreaterEqual(len(defaults.constraints), 1)
        self.assertGreaterEqual(len(defaults.validation_rules), 1)

    def test_default_pattern_matches_analyzer_result(self):
        text = "Implement JWT login API"
        library = PatternLibrary.load_default()

        matches = library.match(text, analyze_intent(text))

        self.assertEqual(1, len(matches))
        self.assertEqual("backend.jwt-auth", matches[0].pattern.id)
        self.assertIn("jwt", matches[0].matched_keywords)

    def test_optimizer_loads_default_patterns_and_returns_matches(self):
        result = optimize_prompt("Implement JWT login API", target="codex")
        payload = result.to_dict()

        self.assertTrue(result.ok)
        self.assertIn("match_patterns", result.pipeline_steps)
        self.assertEqual("backend.jwt-auth", result.pattern_matches[0].pattern.id)
        self.assertEqual("backend.jwt-auth", payload["patternMatches"][0]["id"])

    def test_pattern_definition_fails_fast_without_keywords(self):
        payload = load_default_payload()
        del payload["patterns"][0]["keywords"]

        with self.assertRaisesRegex(PatternLibraryValidationError, "keywords"):
            PatternLibrary.from_dict(payload)

    def test_pattern_definition_fails_fast_for_unknown_text_ref(self):
        payload = copy.deepcopy(load_default_payload())
        payload["patterns"][0]["defaultRequirements"][0]["descriptionRef"] = "missing.ref"

        with self.assertRaisesRegex(PatternLibraryValidationError, "missing.ref"):
            PatternLibrary.from_dict(payload)


if __name__ == "__main__":
    unittest.main()
