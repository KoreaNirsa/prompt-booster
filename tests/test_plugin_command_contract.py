import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "tests" / "fixtures" / "plugin_command_contract.json"
DOC_PATH = ROOT / "docs" / "codex-plugin-commands.md"
EXPECTED_COMMANDS = {
    "prompt.optimize",
    "prompt.score",
    "prompt.explain",
    "prompt.patterns",
    "prompt.executionPlan",
}
EXPECTED_ERRORS = {"empty_input", "invalid_options", "unsupported_target"}


def load_contract():
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


class PluginCommandContractTest(unittest.TestCase):
    def test_contract_defines_required_commands(self):
        contract = load_contract()

        self.assertEqual("1.0.0", contract["schemaVersion"])
        self.assertEqual(EXPECTED_COMMANDS, {command["name"] for command in contract["commands"]})

    def test_each_command_has_documented_input_output_and_errors(self):
        contract = load_contract()
        known_errors = {error["code"] for error in contract["errors"]}

        for command in contract["commands"]:
            with self.subTest(command=command["name"]):
                self.assertTrue(command["description"])
                self.assertIn("required", command["input"])
                self.assertIn("optional", command["input"])
                self.assertIn("required", command["output"])
                self.assertIn("optional", command["output"])
                self.assertTrue(command["output"]["required"])
                self.assertTrue(set(command["errors"]) <= known_errors)
                for field in (*command["input"]["required"], *command["input"]["optional"]):
                    self.assertTrue(field["name"])
                    self.assertTrue(field["type"])
                    self.assertTrue(field["description"])

    def test_optimize_command_returns_required_prompt_booster_outputs(self):
        command = self.command_by_name("prompt.optimize")
        output_fields = set(command["output"]["required"])
        optional_fields = set(command["output"]["optional"])

        self.assertEqual(["sourceText"], [field["name"] for field in command["input"]["required"]])
        self.assertTrue(
            {
                "renderedPrompt",
                "promptIrSummary",
                "matchedPatterns",
                "clarificationQuestions",
            }
            <= output_fields
        )
        self.assertIn("qualityScore", optional_fields)
        self.assertIn("promptIr", optional_fields)

    def test_error_contract_covers_required_failure_modes(self):
        contract = load_contract()
        errors = {error["code"]: error for error in contract["errors"]}

        self.assertEqual(EXPECTED_ERRORS, set(errors))
        self.assertTrue(errors["empty_input"]["recoverable"])
        self.assertTrue(errors["invalid_options"]["recoverable"])
        self.assertTrue(errors["unsupported_target"]["recoverable"])
        self.assertEqual(["neutral", "codex", "claude_code"], contract["supportedTargets"])

    def test_patterns_command_does_not_require_source_text(self):
        command = self.command_by_name("prompt.patterns")
        optional_fields = {field["name"] for field in command["input"]["optional"]}

        self.assertEqual([], command["input"]["required"])
        self.assertEqual({"category", "includeDefaults", "locale"}, optional_fields)
        self.assertEqual(["invalid_options"], command["errors"])

    def test_execution_plan_command_defines_auto_execute_contract(self):
        command = self.command_by_name("prompt.executionPlan")
        optional_fields = {field["name"] for field in command["input"]["optional"]}

        self.assertEqual(["sourceText"], [field["name"] for field in command["input"]["required"]])
        self.assertEqual({"target", "executionMode", "clarificationAnswers"}, optional_fields)
        self.assertEqual(["executionPlan"], command["output"]["required"])
        self.assertEqual(["empty_input", "invalid_options", "unsupported_target"], command["errors"])

    def test_command_document_lists_all_contract_names_and_errors(self):
        document = DOC_PATH.read_text(encoding="utf-8")

        for command_name in EXPECTED_COMMANDS:
            with self.subTest(command=command_name):
                self.assertIn(command_name, document)
        for error_code in EXPECTED_ERRORS:
            with self.subTest(error=error_code):
                self.assertIn(error_code, document)

    def command_by_name(self, name):
        return next(command for command in load_contract()["commands"] if command["name"] == name)


if __name__ == "__main__":
    unittest.main()
