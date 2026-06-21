import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINT_PATH = ROOT / "plugins" / "prompt-booster" / "scripts" / "prompt_booster_command.py"
PLUGIN_MANIFEST_PATH = ROOT / "plugins" / "prompt-booster" / ".codex-plugin" / "plugin.json"
PLUGIN_README_PATH = ROOT / "plugins" / "prompt-booster" / "README.md"


def load_entrypoint():
    spec = importlib.util.spec_from_file_location("prompt_booster_command", ENTRYPOINT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PluginEntrypointTest(unittest.TestCase):
    def test_plugin_manifest_uses_expected_metadata_without_local_paths(self):
        manifest = json.loads(PLUGIN_MANIFEST_PATH.read_text(encoding="utf-8"))
        serialized_manifest = json.dumps(manifest, ensure_ascii=False)
        readme = PLUGIN_README_PATH.read_text(encoding="utf-8")

        self.assertEqual("prompt-booster", manifest["name"])
        self.assertEqual("0.1.0", manifest["version"])
        self.assertEqual("./skills/", manifest["skills"])
        self.assertEqual("Prompt Booster", manifest["interface"]["displayName"])
        self.assertNotIn("C:/Users", serialized_manifest)
        self.assertNotIn("C:\\Users", serialized_manifest)
        self.assertNotIn("C:/Users", readme)
        self.assertNotIn("C:\\Users", readme)

    def test_optimize_command_returns_prompt_contract_payload(self):
        entrypoint = load_entrypoint()

        response = entrypoint.run_command(
            "prompt.optimize",
            {"sourceText": "JWT 로그인 만들어줘", "target": "codex"},
        )

        self.assertTrue(response["ok"])
        self.assertEqual("prompt.optimize", response["command"])
        self.assertIn("JWT", response["data"]["renderedPrompt"])
        self.assertIn("promptIrSummary", response["data"])
        self.assertTrue(
            any(pattern["id"] == "backend.jwt-auth" for pattern in response["data"]["matchedPatterns"])
        )
        self.assertIsNotNone(response["data"]["qualityScore"])
        self.assertIsNone(response["data"]["promptIr"])

    def test_cli_runs_sample_optimize_command(self):
        payload = json.dumps({"sourceText": "JWT 로그인 만들어줘", "target": "codex"}, ensure_ascii=False)

        completed = subprocess.run(
            [sys.executable, str(ENTRYPOINT_PATH), "prompt.optimize", "--input-json", payload],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        response = json.loads(completed.stdout)

        self.assertTrue(response["ok"])
        self.assertEqual("prompt.optimize", response["command"])
        self.assertIn("backend.jwt-auth", json.dumps(response["data"]["matchedPatterns"], ensure_ascii=False))

    def test_entrypoint_returns_contract_errors(self):
        entrypoint = load_entrypoint()

        empty_response = entrypoint.run_command("prompt.optimize", {"sourceText": " "})
        missing_response = entrypoint.run_command("prompt.optimize", {})
        target_response = entrypoint.run_command("prompt.optimize", {"sourceText": "JWT 로그인", "target": "unknown"})
        option_response = entrypoint.run_command("prompt.patterns", {"category": "unknown"})

        self.assertFalse(empty_response["ok"])
        self.assertEqual("empty_input", empty_response["error"]["code"])
        self.assertFalse(missing_response["ok"])
        self.assertEqual("empty_input", missing_response["error"]["code"])
        self.assertFalse(target_response["ok"])
        self.assertEqual("unsupported_target", target_response["error"]["code"])
        self.assertFalse(option_response["ok"])
        self.assertEqual("invalid_options", option_response["error"]["code"])

    def test_cli_returns_invalid_options_for_invalid_json_payload(self):
        completed = subprocess.run(
            [sys.executable, str(ENTRYPOINT_PATH), "prompt.optimize", "--input-json", "{invalid"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        response = json.loads(completed.stdout)

        self.assertEqual(1, completed.returncode)
        self.assertFalse(response["ok"])
        self.assertEqual("invalid_options", response["error"]["code"])

    def test_patterns_command_can_include_defaults(self):
        entrypoint = load_entrypoint()

        response = entrypoint.run_command(
            "prompt.patterns",
            {"category": "backend", "includeDefaults": True},
        )

        self.assertTrue(response["ok"])
        self.assertTrue(response["data"]["patterns"])
        self.assertTrue(all(pattern["category"] == "backend" for pattern in response["data"]["patterns"]))
        self.assertIn("promptDefaults", response["data"]["patterns"][0])


if __name__ == "__main__":
    unittest.main()
