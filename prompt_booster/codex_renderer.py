from __future__ import annotations

from collections.abc import Mapping

from .prompt_renderer import PromptRenderer


class CodexPromptRenderer(PromptRenderer):
    def render(self, prompt_ir: Mapping[str, object]) -> str:
        intent = self._mapping(prompt_ir.get("intent"))
        context = self._mapping(prompt_ir.get("context"))
        output_spec = self._mapping(prompt_ir.get("outputSpec"))

        requirements = self._compact_requirements(self._mapping_items(prompt_ir.get("requirements")))
        constraints = self._compact_constraints(self._mapping_items(prompt_ir.get("constraints")))
        output_sections = self._compact_output_sections(self._mapping_items(output_spec.get("sections")))
        validation_rules = self._compact_validation_rules(self._mapping_items(prompt_ir.get("validationRules")))

        sections = [
            ("Task Objective", self._task_objective_lines(prompt_ir, intent, context)),
            ("Implementation Scope", self._requirement_lines(requirements)),
            ("File Change Expectations", self._file_change_expectation_lines()),
            ("Constraints", self._codex_constraint_lines(constraints)),
            ("Expected Output", self._output_format_lines(output_sections)),
            ("Verification Steps", self._verification_lines(validation_rules)),
            ("Operational Risk Notes", self._operational_risk_lines(intent, context)),
        ]

        lines = ["# Codex Task Prompt"]
        for title, section_lines in sections:
            if not section_lines:
                continue
            lines.extend(("", f"## {title}", *section_lines))
        return "\n".join(lines)

    def _task_objective_lines(
        self,
        prompt_ir: Mapping[str, object],
        intent: Mapping[str, object],
        context: Mapping[str, object],
    ) -> tuple[str, ...]:
        return self._unique_non_empty(
            [
                self._prefix_with_tag(intent.get("summary"), "objective"),
                self._prefix_with_tag(prompt_ir.get("sourceText"), "source"),
                self._prefix_with_tag(context.get("audience"), "role"),
            ]
        )

    def _file_change_expectation_lines(self) -> tuple[str, ...]:
        return (
            "- 변경 전에 관련 파일, 테스트, 기존 구조를 먼저 확인합니다.",
            "- Prompt IR 요구사항과 제약조건에 필요한 파일만 변경합니다.",
            "- 비즈니스 로직이 불명확하면 구현을 추측하지 않고 질문합니다.",
        )

    def _codex_constraint_lines(self, constraints: tuple[Mapping[str, object], ...]) -> tuple[str, ...]:
        return self._unique_non_empty(
            (
                *self._constraint_lines(constraints),
                "- [security] secret 또는 credential 값을 코드, 로그, 예시에 노출하지 않습니다.",
            )
        )

    def _verification_lines(self, rules: tuple[Mapping[str, object], ...]) -> tuple[str, ...]:
        return self._unique_non_empty(
            (
                *self._validation_lines(rules),
                "- [test] 관련 테스트와 정적 검사를 실행하고 결과를 보고합니다.",
                "- [risk] 실행할 수 없는 검증은 이유와 남은 위험을 명시합니다.",
            )
        )

    def _operational_risk_lines(
        self,
        intent: Mapping[str, object],
        context: Mapping[str, object],
    ) -> tuple[str, ...]:
        primary_domain = self._text(intent.get("primaryDomain"))
        tech_stack = " ".join(self._text_items(context.get("techStack"))).casefold()
        if primary_domain not in {"backend", "devops"} and not any(
            signal in tech_stack for signal in ("api", "deployment", "ci", "observability")
        ):
            return ()

        lines = [
            "- config와 secret 주입 경로를 코드와 분리합니다.",
            "- observability, 오류 응답, failure mode를 검토합니다.",
        ]
        if primary_domain == "devops":
            lines.append("- 배포 변경에는 rollback 절차와 상태 확인 방법을 포함합니다.")
        else:
            lines.append("- 배포 또는 인증 흐름 변경이 포함되면 rollback 영향을 별도로 적습니다.")
        return tuple(lines)
