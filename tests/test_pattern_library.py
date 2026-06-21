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
EXPECTED_BACKEND_PATTERN_IDS = {
    "backend.spring-rest-api",
    "backend.spring-security",
    "backend.jwt-auth",
    "backend.oauth2-login",
    "backend.batch-processing",
    "backend.scheduler",
}


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

    def test_backend_pattern_templates_exist_with_matching_metadata(self):
        library = PatternLibrary.load_default()
        pattern_ids = {pattern.id for pattern in library.patterns}

        self.assertTrue(EXPECTED_BACKEND_PATTERN_IDS <= pattern_ids)
        for pattern_id in EXPECTED_BACKEND_PATTERN_IDS:
            with self.subTest(pattern=pattern_id):
                pattern = library.get(pattern_id)

                self.assertEqual("backend", pattern.category)
                self.assertTrue(pattern.keywords)
                self.assertTrue(pattern.matching_metadata.intent_hints)
                self.assertTrue(pattern.matching_metadata.domain_signals)
                self.assertGreaterEqual(pattern.matching_metadata.confidence_weight, 1)
                self.assertLessEqual(pattern.matching_metadata.confidence_weight, 5)

    def test_jwt_and_auth_patterns_include_security_requirements(self):
        library = PatternLibrary.load_default()

        for pattern_id in ("backend.jwt-auth", "backend.spring-security", "backend.oauth2-login"):
            with self.subTest(pattern=pattern_id):
                defaults = library.get(pattern_id).to_prompt_defaults().to_dict()
                serialized = json.dumps(defaults, ensure_ascii=False).casefold()

                self.assertIn("secret", serialized)
                self.assertTrue("error" in serialized or "오류" in serialized or "실패" in serialized)
        jwt_defaults = json.dumps(library.get("backend.jwt-auth").to_prompt_defaults().to_dict(), ensure_ascii=False).casefold()
        self.assertIn("만료", jwt_defaults)
        self.assertIn("refresh strategy", jwt_defaults)

    def test_rest_api_pattern_includes_contract_validation_persistence_and_tests(self):
        defaults = PatternLibrary.load_default().get("backend.spring-rest-api").to_prompt_defaults().to_dict()
        serialized = json.dumps(defaults, ensure_ascii=False).casefold()

        self.assertIn("api contract", serialized)
        self.assertIn("검증", serialized)
        self.assertIn("영속성", serialized)
        self.assertIn("테스트", serialized)

    def test_default_pattern_matches_analyzer_result(self):
        text = "Implement JWT login API"
        library = PatternLibrary.load_default()

        matches = library.match(text, analyze_intent(text))
        pattern_ids = {match.pattern.id for match in matches}

        self.assertIn("backend.jwt-auth", pattern_ids)
        jwt_match = next(match for match in matches if match.pattern.id == "backend.jwt-auth")
        self.assertIn("jwt", jwt_match.matched_keywords)

    def test_optimizer_loads_default_patterns_and_returns_matches(self):
        result = optimize_prompt("Implement JWT login API", target="codex")
        payload = result.to_dict()

        self.assertTrue(result.ok)
        self.assertIn("match_patterns", result.pipeline_steps)
        pattern_ids = {match.pattern.id for match in result.pattern_matches}
        payload_ids = {match["id"] for match in payload["patternMatches"]}
        self.assertIn("backend.jwt-auth", pattern_ids)
        self.assertIn("backend.jwt-auth", payload_ids)

    def test_ambiguous_jwt_prompt_is_augmented_by_backend_pattern_defaults(self):
        result = optimize_prompt("JWT 로그인 만들어줘")
        jwt_match = next(match for match in result.pattern_matches if match.pattern.id == "backend.jwt-auth")
        defaults = jwt_match.pattern.to_prompt_defaults().to_dict()
        serialized = json.dumps(defaults, ensure_ascii=False)

        self.assertTrue(result.ok)
        self.assertIn("Access Token", serialized)
        self.assertIn("Refresh Token", serialized)
        self.assertIn("secret", serialized)
        self.assertIn("토큰 만료", serialized)

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
