import importlib.util
from pathlib import Path
import unittest

from prompt_booster import Category, IntentType, optimize_prompt


def load_schema_validator():
    module_path = Path(__file__).resolve().parents[1] / "tools" / "validate_prompt_ir_examples.py"
    spec = importlib.util.spec_from_file_location("validate_prompt_ir_examples", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PromptOptimizerTest(unittest.TestCase):
    def test_optimizer_generates_ir_and_rendered_prompt(self):
        result = optimize_prompt("Implement JWT login API", target="codex")

        self.assertTrue(result.ok)
        self.assertEqual((), result.errors)
        self.assertEqual(
            (
                "validate_input",
                "analyze_intent",
                "generate_clarification_questions",
                "generate_rif",
                "match_patterns",
                "inject_constraints",
                "render_prompt",
            ),
            result.pipeline_steps,
        )
        self.assertEqual(IntentType.CODE_GENERATION, result.analysis.intent)
        self.assertEqual(Category.BACKEND, result.analysis.category)
        self.assertEqual("1.0.0", result.prompt_ir["schemaVersion"])
        self.assertEqual("implement", result.prompt_ir["intent"]["action"])
        self.assertEqual("backend", result.prompt_ir["intent"]["primaryDomain"])
        self.assertIn("clarificationQuestions", result.to_dict())
        self.assertEqual("backend.jwt-auth", result.pattern_matches[0].pattern.id)
        self.assertIn("target=codex", result.prompt_ir["context"]["assumptions"])
        self.assertIn("## Role", result.rendered_prompt)
        self.assertIn("## Validation", result.rendered_prompt)

    def test_optimizer_uses_system_design_and_architecture_classification(self):
        result = optimize_prompt("Design Clean Architecture module boundaries")

        self.assertTrue(result.ok)
        self.assertEqual(IntentType.ARCHITECTURE, result.analysis.intent)
        self.assertEqual(Category.ARCHITECTURE, result.analysis.category)
        self.assertEqual("design", result.prompt_ir["intent"]["action"])
        self.assertEqual("architecture", result.prompt_ir["intent"]["primaryDomain"])

    def test_empty_input_returns_validation_error(self):
        result = optimize_prompt("  ")

        self.assertFalse(result.ok)
        self.assertEqual("empty_input", result.errors[0].code)
        self.assertIsNone(result.prompt_ir)
        self.assertIsNone(result.rendered_prompt)
        self.assertEqual(("validate_input",), result.pipeline_steps)

    def test_too_short_input_returns_validation_error(self):
        result = optimize_prompt("go")

        self.assertFalse(result.ok)
        self.assertEqual("too_short_input", result.errors[0].code)
        self.assertIsNone(result.prompt_ir)

    def test_unclassified_input_returns_recovery_response(self):
        result = optimize_prompt("Please help with something complicated")

        self.assertFalse(result.ok)
        self.assertEqual("no_supported_signal", result.errors[0].code)
        self.assertIsNone(result.prompt_ir)
        self.assertIn("Prompt-Booster Recovery", result.rendered_prompt)
        self.assertEqual(("validate_input", "analyze_intent"), result.pipeline_steps)

    def test_result_is_serializable_dict(self):
        payload = optimize_prompt("Implement RAG chatbot").to_dict()

        self.assertEqual("ai", payload["analysis"]["category"])
        self.assertIn("promptIr", payload)
        self.assertIn("renderedPrompt", payload)
        self.assertIn("patternMatches", payload)
        self.assertIn("sourceQualityScore", payload)
        self.assertIn("optimizedQualityScore", payload)
        self.assertEqual([], payload["errors"])

    def test_generated_prompt_ir_matches_schema_contract(self):
        validator = load_schema_validator()
        schema = validator.load_json(validator.SCHEMA_PATH)
        result = optimize_prompt("Implement JWT login API", target="codex")

        validator.validate_against_schema(schema, result.prompt_ir)


if __name__ == "__main__":
    unittest.main()
