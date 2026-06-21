from pathlib import Path
import unittest

from prompt_booster import CodexPromptRenderer, optimize_prompt


SNAPSHOT_DIR = Path(__file__).resolve().parent / "snapshots"


class CodexPromptRendererTest(unittest.TestCase):
    def assert_snapshot(self, name: str, rendered_prompt: str):
        expected = (SNAPSHOT_DIR / name).read_text(encoding="utf-8").rstrip()
        self.assertEqual(expected, rendered_prompt)

    def test_codex_backend_prompt_matches_snapshot(self):
        result = optimize_prompt("JWT 로그인 구현해줘", target="codex")

        self.assertTrue(result.ok)
        self.assertIn("## Task Objective", result.rendered_prompt)
        self.assertIn("## Implementation Scope", result.rendered_prompt)
        self.assertIn("## Constraints", result.rendered_prompt)
        self.assertIn("## Expected Output", result.rendered_prompt)
        self.assertIn("## Verification Steps", result.rendered_prompt)
        self.assert_snapshot("codex_renderer_backend.md", result.rendered_prompt)

    def test_codex_devops_prompt_matches_snapshot(self):
        result = optimize_prompt("GitHub Actions CI 배포 만들어줘", target="codex")
        rendered_prompt = result.rendered_prompt.casefold()

        self.assertTrue(result.ok)
        self.assertIn("rollback", rendered_prompt)
        self.assertIn("config", rendered_prompt)
        self.assertIn("observability", rendered_prompt)
        self.assertIn("secret", rendered_prompt)
        self.assertIn("failure mode", rendered_prompt)
        self.assert_snapshot("codex_renderer_devops.md", result.rendered_prompt)

    def test_codex_refactoring_prompt_matches_snapshot(self):
        result = optimize_prompt("서비스 코드 리팩토링 해줘", target="codex")

        self.assertTrue(result.ok)
        self.assertIn("기존 구조를 먼저 확인합니다", result.rendered_prompt)
        self.assertIn("노출하지 않습니다", result.rendered_prompt)
        self.assert_snapshot("codex_renderer_refactoring.md", result.rendered_prompt)

    def test_neutral_renderer_remains_separate_from_codex_renderer(self):
        neutral_result = optimize_prompt("JWT 로그인 구현해줘")
        codex_result = optimize_prompt("JWT 로그인 구현해줘", target="codex")

        self.assertTrue(neutral_result.ok)
        self.assertTrue(codex_result.ok)
        self.assertTrue(neutral_result.rendered_prompt.startswith("# Optimized Prompt"))
        self.assertTrue(codex_result.rendered_prompt.startswith("# Codex Task Prompt"))
        self.assertNotIn("## Task Objective", neutral_result.rendered_prompt)

    def test_codex_renderer_is_deterministic_for_same_ir(self):
        prompt_ir = optimize_prompt("서비스 코드 리팩토링 해줘", target="codex").prompt_ir
        renderer = CodexPromptRenderer()

        self.assertEqual(renderer.render(prompt_ir), renderer.render(prompt_ir))


if __name__ == "__main__":
    unittest.main()
