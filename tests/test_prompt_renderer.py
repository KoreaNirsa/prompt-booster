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

    def test_neutral_renderer_does_not_emit_target_specific_assumption(self):
        result = optimize_prompt("JWT 로그인 구현해줘")

        self.assertTrue(result.ok)
        self.assertIn("target=neutral", result.prompt_ir["context"]["assumptions"])
        self.assertNotIn("target=neutral", result.rendered_prompt)
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

    def test_renderer_compacts_duplicate_structured_items_before_rendering(self):
        rendered_prompt = PromptRenderer().render(
            {
                "intent": {"summary": "토큰 최적화 렌더링을 검증합니다."},
                "context": {"audience": "테스트 엔지니어"},
                "requirements": [
                    {
                        "description": "중복 요구사항",
                        "priority": "should",
                        "acceptanceCriteria": ["기준 A", "기준 B"],
                    },
                    {
                        "description": "중복 요구사항",
                        "priority": "must",
                        "acceptanceCriteria": ["기준 B", "기준 C"],
                    },
                ],
                "constraints": [
                    {"scope": "security", "description": "중복 제약"},
                    {"scope": "testing", "description": "중복 제약"},
                ],
                "outputSpec": {
                    "sections": [
                        {"title": "중복 섹션", "description": "첫 번째 설명", "required": True},
                        {"title": "중복 섹션", "description": "두 번째 설명", "required": True},
                    ]
                },
                "validationRules": [
                    {"severity": "warning", "description": "중복 검증"},
                    {"severity": "error", "description": "중복 검증"},
                ],
            }
        )

        self.assertEqual(1, rendered_prompt.count("- [must] 중복 요구사항"))
        self.assertNotIn("- [should] 중복 요구사항", rendered_prompt)
        self.assertEqual(1, rendered_prompt.count("  - 기준 A"))
        self.assertEqual(1, rendered_prompt.count("  - 기준 B"))
        self.assertEqual(1, rendered_prompt.count("  - 기준 C"))
        self.assertIn("- [security, testing] 중복 제약", rendered_prompt)
        self.assertEqual(1, rendered_prompt.count("- 중복 섹션:"))
        self.assertIn("첫 번째 설명; 두 번째 설명", rendered_prompt)
        self.assertEqual(1, rendered_prompt.count("- [error] 중복 검증"))


if __name__ == "__main__":
    unittest.main()
