from pathlib import Path
import unittest

from prompt_booster import PromptRenderer, optimize_prompt


SNAPSHOT_DIR = Path(__file__).resolve().parent / "snapshots"


class PromptRendererTest(unittest.TestCase):
    def assert_snapshot(self, name: str, rendered_prompt: str):
        expected = (SNAPSHOT_DIR / name).read_text(encoding="utf-8").rstrip()
        self.assertEqual(expected, rendered_prompt)

    def test_backend_prompt_matches_snapshot(self):
        result = optimize_prompt("JWT 로그인 구현해줘")

        self.assertTrue(result.ok)
        self.assert_snapshot("prompt_renderer_backend.md", result.rendered_prompt)

    def test_frontend_prompt_matches_snapshot(self):
        result = optimize_prompt("React 대시보드 만들어줘")

        self.assertTrue(result.ok)
        self.assert_snapshot("prompt_renderer_frontend.md", result.rendered_prompt)

    def test_ai_prompt_matches_snapshot(self):
        result = optimize_prompt("RAG 챗봇 구현해줘")

        self.assertTrue(result.ok)
        self.assert_snapshot("prompt_renderer_ai.md", result.rendered_prompt)

    def test_renderer_is_deterministic_for_same_ir(self):
        prompt_ir = optimize_prompt("RAG 챗봇 구현해줘").prompt_ir
        renderer = PromptRenderer()

        self.assertEqual(renderer.render(prompt_ir), renderer.render(prompt_ir))

    def test_renderer_does_not_emit_target_specific_assumption(self):
        result = optimize_prompt("JWT 로그인 구현해줘", target="codex")

        self.assertTrue(result.ok)
        self.assertIn("target=codex", result.prompt_ir["context"]["assumptions"])
        self.assertNotIn("codex", result.rendered_prompt.casefold())

    def test_renderer_omits_empty_sections_and_deduplicates_lines(self):
        rendered_prompt = PromptRenderer().render(
            {
                "intent": {"summary": "중복 없는 렌더링을 검증합니다."},
                "context": {"audience": ""},
                "requirements": [
                    {"description": "동일 요구사항", "priority": "must", "acceptanceCriteria": ["", "기준"]},
                    {"description": "동일 요구사항", "priority": "must", "acceptanceCriteria": ["기준"]},
                ],
                "constraints": [
                    {"scope": "testing", "description": ""},
                    {"scope": "testing", "description": "테스트 제약"},
                    {"scope": "testing", "description": "테스트 제약"},
                ],
                "outputSpec": {"sections": []},
                "validationRules": [],
            }
        )

        self.assertNotIn("## Role", rendered_prompt)
        self.assertNotIn("## Output Format", rendered_prompt)
        self.assertNotIn("## Validation", rendered_prompt)
        self.assertEqual(1, rendered_prompt.count("- [must] 동일 요구사항"))
        self.assertEqual(1, rendered_prompt.count("  - 기준"))
        self.assertEqual(1, rendered_prompt.count("- [testing] 테스트 제약"))


if __name__ == "__main__":
    unittest.main()
