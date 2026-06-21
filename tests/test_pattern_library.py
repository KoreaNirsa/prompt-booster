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
EXPECTED_FRONTEND_PATTERN_IDS = {
    "frontend.react-spa",
    "frontend.nextjs",
    "frontend.dashboard",
    "frontend.admin-page",
}
EXPECTED_AI_PATTERN_IDS = {
    "ai.rag",
    "ai.agent",
    "ai.chatbot",
    "ai.embedding",
    "ai.vector-database",
}
EXPECTED_DEVOPS_PATTERN_IDS = {
    "devops.docker",
    "devops.kubernetes",
    "devops.github-actions",
    "devops.aws-deployment",
}
EXPECTED_ARCHITECTURE_PATTERN_IDS = {
    "architecture.clean",
    "architecture.hexagonal",
    "architecture.ddd",
    "architecture.msa",
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

    def test_frontend_pattern_templates_exist_with_matching_metadata(self):
        library = PatternLibrary.load_default()
        pattern_ids = {pattern.id for pattern in library.patterns}

        self.assertTrue(EXPECTED_FRONTEND_PATTERN_IDS <= pattern_ids)
        for pattern_id in EXPECTED_FRONTEND_PATTERN_IDS:
            with self.subTest(pattern=pattern_id):
                pattern = library.get(pattern_id)

                self.assertEqual("frontend", pattern.category)
                self.assertTrue(pattern.keywords)
                self.assertTrue(pattern.matching_metadata.intent_hints)
                self.assertTrue(pattern.matching_metadata.domain_signals)
                self.assertGreaterEqual(pattern.matching_metadata.confidence_weight, 1)
                self.assertLessEqual(pattern.matching_metadata.confidence_weight, 5)

    def test_frontend_patterns_include_ui_and_output_expectations(self):
        library = PatternLibrary.load_default()

        for pattern_id in EXPECTED_FRONTEND_PATTERN_IDS:
            with self.subTest(pattern=pattern_id):
                defaults = library.get(pattern_id).to_prompt_defaults().to_dict()
                serialized = json.dumps(defaults, ensure_ascii=False).casefold()

                self.assertIn("routing", serialized)
                self.assertIn("loading/error/empty states", serialized)
                self.assertIn("component organization", serialized)
                self.assertIn("file structure", serialized)
                self.assertIn("components", serialized)
                self.assertIn("tests", serialized)
                self.assertIn("styling approach", serialized)
                self.assertIn("responsive layout", serialized)
                self.assertTrue("accessibility" in serialized or "접근성" in serialized)

    def test_ai_pattern_templates_exist_with_matching_metadata(self):
        library = PatternLibrary.load_default()
        pattern_ids = {pattern.id for pattern in library.patterns}

        self.assertTrue(EXPECTED_AI_PATTERN_IDS <= pattern_ids)
        for pattern_id in EXPECTED_AI_PATTERN_IDS:
            with self.subTest(pattern=pattern_id):
                pattern = library.get(pattern_id)

                self.assertEqual("ai", pattern.category)
                self.assertTrue(pattern.keywords)
                self.assertTrue(pattern.matching_metadata.intent_hints)
                self.assertTrue(pattern.matching_metadata.domain_signals)
                self.assertGreaterEqual(pattern.matching_metadata.confidence_weight, 1)
                self.assertLessEqual(pattern.matching_metadata.confidence_weight, 5)

    def test_ai_patterns_include_required_operational_criteria(self):
        library = PatternLibrary.load_default()
        rag_defaults = json.dumps(library.get("ai.rag").to_prompt_defaults().to_dict(), ensure_ascii=False).casefold()
        agent_defaults = json.dumps(library.get("ai.agent").to_prompt_defaults().to_dict(), ensure_ascii=False).casefold()
        vector_defaults = json.dumps(
            library.get("ai.vector-database").to_prompt_defaults().to_dict(),
            ensure_ascii=False,
        ).casefold()

        for term in ("retrieval strategy", "chunking", "source handling", "fallback behavior", "evaluation criteria"):
            self.assertIn(term, rag_defaults)
        for term in ("tool boundary", "error handling", "idempotency", "safety constraints"):
            self.assertIn(term, agent_defaults)
        for term in ("indexing", "metadata", "similarity search", "update/delete"):
            self.assertIn(term, vector_defaults)

    def test_devops_pattern_templates_exist_with_matching_metadata(self):
        library = PatternLibrary.load_default()
        pattern_ids = {pattern.id for pattern in library.patterns}

        self.assertTrue(EXPECTED_DEVOPS_PATTERN_IDS <= pattern_ids)
        for pattern_id in EXPECTED_DEVOPS_PATTERN_IDS:
            with self.subTest(pattern=pattern_id):
                pattern = library.get(pattern_id)

                self.assertEqual("devops", pattern.category)
                self.assertTrue(pattern.keywords)
                self.assertTrue(pattern.matching_metadata.intent_hints)
                self.assertTrue(pattern.matching_metadata.domain_signals)
                self.assertGreaterEqual(pattern.matching_metadata.confidence_weight, 1)
                self.assertLessEqual(pattern.matching_metadata.confidence_weight, 5)

    def test_devops_patterns_include_secret_and_operational_constraints(self):
        library = PatternLibrary.load_default()

        for pattern_id in EXPECTED_DEVOPS_PATTERN_IDS:
            with self.subTest(pattern=pattern_id):
                defaults = library.get(pattern_id).to_prompt_defaults().to_dict()
                serialized = json.dumps(defaults, ensure_ascii=False).casefold()

                self.assertIn("secret handling", serialized)
                self.assertIn("environment variable", serialized)
                self.assertIn("observability", serialized)
        for pattern_id in ("devops.docker", "devops.kubernetes", "devops.aws-deployment"):
            with self.subTest(deployment_pattern=pattern_id):
                serialized = json.dumps(
                    library.get(pattern_id).to_prompt_defaults().to_dict(),
                    ensure_ascii=False,
                ).casefold()

                self.assertIn("rollback", serialized)
                self.assertIn("health check", serialized)
                self.assertIn("failure-mode expectations", serialized)
        ci_defaults = json.dumps(library.get("devops.github-actions").to_prompt_defaults().to_dict(), ensure_ascii=False)
        self.assertIn("재현 가능한 명령", ci_defaults)
        self.assertIn("실패 진단", ci_defaults)

    def test_architecture_pattern_templates_exist_with_matching_metadata(self):
        library = PatternLibrary.load_default()
        pattern_ids = {pattern.id for pattern in library.patterns}

        self.assertTrue(EXPECTED_ARCHITECTURE_PATTERN_IDS <= pattern_ids)
        for pattern_id in EXPECTED_ARCHITECTURE_PATTERN_IDS:
            with self.subTest(pattern=pattern_id):
                pattern = library.get(pattern_id)

                self.assertEqual("architecture", pattern.category)
                self.assertTrue(pattern.keywords)
                self.assertTrue(pattern.matching_metadata.intent_hints)
                self.assertTrue(pattern.matching_metadata.domain_signals)
                self.assertGreaterEqual(pattern.matching_metadata.confidence_weight, 1)
                self.assertLessEqual(pattern.matching_metadata.confidence_weight, 5)

    def test_architecture_patterns_include_boundary_dependency_and_tradeoff(self):
        library = PatternLibrary.load_default()

        for pattern_id in EXPECTED_ARCHITECTURE_PATTERN_IDS:
            with self.subTest(pattern=pattern_id):
                defaults = library.get(pattern_id).to_prompt_defaults().to_dict()
                serialized = json.dumps(defaults, ensure_ascii=False).casefold()

                self.assertIn("module boundary", serialized)
                self.assertIn("dependency rule", serialized)
                self.assertIn("tradeoff analysis", serialized)
                self.assertIn("validation criteria", serialized)
                self.assertTrue("diagram" in serialized or "구조화된 목록" in serialized)
        msa_defaults = json.dumps(library.get("architecture.msa").to_prompt_defaults().to_dict(), ensure_ascii=False).casefold()
        for term in ("service boundary", "data ownership", "communication style", "failure-mode"):
            self.assertIn(term, msa_defaults)

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

    def test_frontend_prompts_are_augmented_by_pattern_defaults(self):
        cases = (
            ("React SPA 만들어줘", "frontend.react-spa", ("routing", "state", "loading/error/empty states")),
            ("dashboard 화면 만들어줘", "frontend.dashboard", ("filter", "chart", "responsive layout")),
        )

        for source_text, pattern_id, expected_terms in cases:
            with self.subTest(pattern=pattern_id):
                result = optimize_prompt(source_text)
                match = next(match for match in result.pattern_matches if match.pattern.id == pattern_id)
                defaults = match.pattern.to_prompt_defaults().to_dict()
                serialized = json.dumps(defaults, ensure_ascii=False).casefold()

                self.assertTrue(result.ok)
                for term in expected_terms:
                    self.assertIn(term, serialized)

    def test_ai_prompt_is_augmented_with_validation_criteria(self):
        result = optimize_prompt("RAG 챗봇 만들어줘")
        rag_match = next(match for match in result.pattern_matches if match.pattern.id == "ai.rag")
        defaults = rag_match.pattern.to_prompt_defaults().to_dict()
        serialized = json.dumps(defaults, ensure_ascii=False).casefold()

        self.assertTrue(result.ok)
        self.assertIn("validation criteria", serialized)
        self.assertIn("evaluation criteria", serialized)
        self.assertIn("citation", serialized)
        self.assertIn("fallback behavior", serialized)

    def test_devops_prompt_is_augmented_with_operational_constraints(self):
        result = optimize_prompt("GitHub Actions CI 만들어줘")
        ci_match = next(match for match in result.pattern_matches if match.pattern.id == "devops.github-actions")
        defaults = ci_match.pattern.to_prompt_defaults().to_dict()
        serialized = json.dumps(defaults, ensure_ascii=False)

        self.assertTrue(result.ok)
        self.assertIn("secret handling", serialized.casefold())
        self.assertIn("environment variable", serialized.casefold())
        self.assertIn("재현 가능한 명령", serialized)
        self.assertIn("실패 진단", serialized)

    def test_architecture_prompt_is_augmented_by_pattern_defaults(self):
        result = optimize_prompt("Clean Architecture module boundary 설계해줘")
        clean_match = next(match for match in result.pattern_matches if match.pattern.id == "architecture.clean")
        defaults = clean_match.pattern.to_prompt_defaults().to_dict()
        serialized = json.dumps(defaults, ensure_ascii=False).casefold()

        self.assertTrue(result.ok)
        self.assertIn("module boundary", serialized)
        self.assertIn("dependency rule", serialized)
        self.assertIn("tradeoff analysis", serialized)
        self.assertIn("validation criteria", serialized)

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
