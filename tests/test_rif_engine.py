import unittest

from prompt_booster import Category, IntentType, RifEngine, analyze_intent, optimize_prompt


class RifEngineTest(unittest.TestCase):
    def test_code_generation_uses_backend_role_and_implementation_format(self):
        analysis = analyze_intent("JWT 로그인 구현해줘")
        rif = RifEngine().generate("JWT 로그인 구현해줘", analysis)

        self.assertEqual(IntentType.CODE_GENERATION, analysis.intent)
        self.assertEqual(Category.BACKEND, analysis.category)
        self.assertEqual("백엔드 개발자", rif.role.title)
        self.assertIn("구현", rif.role.description)
        self.assertIn("Controller, Service, Repository", rif.instruction.expectations[1])
        self.assertEqual(
            ["구현 목표", "핵심 변경 사항", "검증 계획"],
            [section.title for section in rif.format_sections],
        )

    def test_system_design_uses_architecture_role_and_design_format(self):
        analysis = analyze_intent("게시판 설계해줘")
        rif = RifEngine().generate("게시판 설계해줘", analysis)

        self.assertEqual(IntentType.SYSTEM_DESIGN, analysis.intent)
        self.assertEqual(Category.ARCHITECTURE, analysis.category)
        self.assertEqual("소프트웨어 아키텍트", rif.role.title)
        self.assertIn("시스템 설계", rif.instruction.objective)
        self.assertEqual(
            ["설계 목표", "구성 요소", "데이터 흐름", "검증 기준"],
            [section.title for section in rif.format_sections],
        )

    def test_refactoring_preserves_behavior_in_instruction_and_format(self):
        analysis = analyze_intent("서비스 코드 리팩토링 해줘")
        rif = RifEngine().generate("서비스 코드 리팩토링 해줘", analysis)

        self.assertEqual(IntentType.REFACTORING, analysis.intent)
        self.assertEqual(Category.BACKEND, analysis.category)
        self.assertIn("기존 동작을 보존", rif.role.responsibilities[1])
        self.assertIn("변경 전후의 동작 보존 조건", rif.instruction.expectations[2])
        self.assertEqual(
            ["리팩토링 목표", "변경 범위", "단계별 변경", "회귀 검증"],
            [section.title for section in rif.format_sections],
        )

    def test_rif_output_is_structured_before_rendering(self):
        analysis = analyze_intent("RAG 챗봇 구현해줘")
        payload = RifEngine().generate("RAG 챗봇 구현해줘", analysis).to_dict()

        self.assertEqual("AI 애플리케이션 개발자", payload["role"]["title"])
        self.assertIn("objective", payload["instruction"])
        self.assertIn("expectations", payload["instruction"])
        self.assertIn("sections", payload["format"])
        self.assertNotIn("Codex", str(payload))

    def test_optimizer_maps_structured_rif_to_prompt_ir(self):
        result = optimize_prompt("서비스 코드 리팩토링 해줘")

        self.assertTrue(result.ok)
        self.assertEqual("백엔드 개발자", result.prompt_ir["context"]["audience"])
        self.assertTrue(
            any(
                "변경 전후의 동작 보존 조건" in criterion
                for criterion in result.prompt_ir["requirements"][0]["acceptanceCriteria"]
            )
        )
        self.assertEqual(
            ["리팩토링 목표", "변경 범위", "단계별 변경", "회귀 검증"],
            [section["title"] for section in result.prompt_ir["outputSpec"]["sections"]],
        )
        self.assertIn("변경 전후의 동작 보존 조건", result.rendered_prompt)


if __name__ == "__main__":
    unittest.main()
