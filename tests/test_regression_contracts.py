import importlib.util
import json
from pathlib import Path
import unittest

from prompt_booster import optimize_prompt


ROOT = Path(__file__).resolve().parents[1]
CORE_FIXTURE_PATH = ROOT / "tests" / "fixtures" / "core_samples.json"
CONTRACT_PATH = ROOT / "tests" / "fixtures" / "plugin_command_contract.json"
ENTRYPOINT_PATH = ROOT / "plugins" / "prompt-booster" / "scripts" / "prompt_booster_command.py"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_entrypoint():
    spec = importlib.util.spec_from_file_location("prompt_booster_command", ENTRYPOINT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RegressionContractTest(unittest.TestCase):
    def test_core_samples_keep_minimum_ir_structure_and_quality_score(self):
        for fixture in load_json(CORE_FIXTURE_PATH)["fixtures"]:
            with self.subTest(fixture=fixture["id"]):
                result = optimize_prompt(fixture["sourceText"])
                rendered_sections = {
                    line.removeprefix("## ").strip()
                    for line in result.rendered_prompt.splitlines()
                    if line.startswith("## ")
                }

                self.assertTrue(result.ok)
                self.assertEqual(fixture["expectedIntent"], result.analysis.intent.value)
                self.assertEqual(fixture["expectedCategory"], result.analysis.category.value)
                self.assertGreaterEqual(result.optimized_quality_score.total, fixture["minimumOptimizedQualityScore"])
                self.assertGreaterEqual(len(result.prompt_ir["requirements"]), 3)
                self.assertGreaterEqual(len(result.prompt_ir["constraints"]), 3)
                self.assertGreaterEqual(len(result.prompt_ir["validationRules"]), 2)
                self.assertTrue(set(fixture["minimumSections"]) <= rendered_sections)

    def test_plugin_optimize_success_output_matches_contract_shape(self):
        contract = load_json(CONTRACT_PATH)
        optimize_contract = next(command for command in contract["commands"] if command["name"] == "prompt.optimize")
        required_output_fields = set(optimize_contract["output"]["required"])
        optional_output_fields = set(optimize_contract["output"]["optional"])
        entrypoint = load_entrypoint()

        response = entrypoint.run_command(
            "prompt.optimize",
            {"sourceText": "JWT 로그인 만들어줘", "target": "claude_code", "includePromptIr": True},
        )
        data = response["data"]

        self.assertTrue(response["ok"])
        self.assertEqual({"ok", "command", "data", "error"}, set(response))
        self.assertEqual("prompt.optimize", response["command"])
        self.assertIsNone(response["error"])
        self.assertTrue(required_output_fields <= set(data))
        self.assertTrue(optional_output_fields <= set(data))
        self.assertIsInstance(data["renderedPrompt"], str)
        self.assertTrue(data["renderedPrompt"].startswith("# Claude Code Task Prompt"))
        self.assertIsInstance(data["promptIrSummary"], dict)
        self.assertIsInstance(data["matchedPatterns"], list)
        self.assertIsInstance(data["clarificationQuestions"], list)
        self.assertIsInstance(data["qualityScore"], dict)
        self.assertIsInstance(data["promptIr"], dict)

    def test_plugin_failure_output_matches_contract_shape(self):
        entrypoint = load_entrypoint()

        response = entrypoint.run_command("prompt.optimize", {"sourceText": "JWT 로그인", "target": "unknown"})

        self.assertFalse(response["ok"])
        self.assertEqual({"ok", "command", "data", "error"}, set(response))
        self.assertIsNone(response["data"])
        self.assertEqual({"code", "message", "recoverable", "details"}, set(response["error"]))
        self.assertEqual("unsupported_target", response["error"]["code"])
        self.assertTrue(response["error"]["recoverable"])

    def test_snapshot_assets_cover_representative_renderer_targets(self):
        snapshot_names = {path.name for path in (ROOT / "tests" / "snapshots").glob("*.md")}

        self.assertTrue(
            {
                "prompt_renderer_backend.md",
                "prompt_renderer_frontend.md",
                "prompt_renderer_ai.md",
                "codex_renderer_backend.md",
                "codex_renderer_devops.md",
                "codex_renderer_refactoring.md",
            }
            <= snapshot_names
        )


if __name__ == "__main__":
    unittest.main()
