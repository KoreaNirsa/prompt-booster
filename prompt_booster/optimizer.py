from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import hashlib
from os import PathLike

from .adaptive_grill import AdaptiveGrillMe, ClarificationQuestion
from .intent_analyzer import AnalyzerResult, Category, IntentAnalyzer, IntentType
from .pattern_library import PatternLibrary, PatternMatch
from .prompt_renderer import PromptRenderer
from .quality_score import PromptQualityReport, PromptQualityScorer
from .rif_engine import RifEngine, RifOutput


SUPPORTED_TARGETS = frozenset({"neutral", "codex"})


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "message": self.message,
        }


@dataclass(frozen=True)
class ConstraintOutput:
    constraints: tuple[dict[str, str], ...]
    validation_rules: tuple[dict[str, str], ...]


@dataclass(frozen=True)
class OptimizerResult:
    source_text: str
    target: str
    analysis: AnalyzerResult | None
    clarification_questions: tuple[ClarificationQuestion, ...]
    pattern_matches: tuple[PatternMatch, ...]
    source_quality_score: PromptQualityReport | None
    optimized_quality_score: PromptQualityReport | None
    prompt_ir: dict[str, object] | None
    rendered_prompt: str | None
    errors: tuple[ValidationIssue, ...]
    pipeline_steps: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict[str, object]:
        return {
            "sourceText": self.source_text,
            "target": self.target,
            "analysis": self.analysis.to_dict() if self.analysis else None,
            "clarificationQuestions": [question.to_dict() for question in self.clarification_questions],
            "patternMatches": [match.to_dict() for match in self.pattern_matches],
            "sourceQualityScore": self.source_quality_score.to_dict() if self.source_quality_score else None,
            "optimizedQualityScore": self.optimized_quality_score.to_dict() if self.optimized_quality_score else None,
            "promptIr": self.prompt_ir,
            "renderedPrompt": self.rendered_prompt,
            "errors": [error.to_dict() for error in self.errors],
            "pipelineSteps": list(self.pipeline_steps),
        }


class PromptOptimizer:
    def __init__(
        self,
        analyzer: IntentAnalyzer | None = None,
        rif_engine: RifEngine | None = None,
        renderer: PromptRenderer | None = None,
        adaptive_grill: AdaptiveGrillMe | None = None,
        quality_scorer: PromptQualityScorer | None = None,
        pattern_library: PatternLibrary | Mapping[str, object] | str | PathLike[str] | None = None,
    ) -> None:
        self._analyzer = analyzer or IntentAnalyzer()
        self._rif_engine = rif_engine or RifEngine()
        self._renderer = renderer or PromptRenderer()
        self._adaptive_grill = adaptive_grill or AdaptiveGrillMe()
        self._quality_scorer = quality_scorer or PromptQualityScorer()
        self._pattern_library = self._resolve_pattern_library(pattern_library)

    def optimize(self, source_text: str, target: str | None = None) -> OptimizerResult:
        selected_target = target or "neutral"
        validation_error = self._validate_input(source_text, selected_target)
        if validation_error:
            return OptimizerResult(
                source_text=source_text,
                target=selected_target,
                analysis=None,
                clarification_questions=(),
                pattern_matches=(),
                source_quality_score=None,
                optimized_quality_score=None,
                prompt_ir=None,
                rendered_prompt=None,
                errors=(validation_error,),
                pipeline_steps=("validate_input",),
            )

        pipeline_steps = ["validate_input", "analyze_intent"]
        analysis = self._analyzer.analyze(source_text)
        source_quality_score = self._quality_scorer.score_source_text(source_text, analysis)
        if analysis.fallback.used:
            return OptimizerResult(
                source_text=source_text,
                target=selected_target,
                analysis=analysis,
                clarification_questions=(),
                pattern_matches=(),
                source_quality_score=source_quality_score,
                optimized_quality_score=None,
                prompt_ir=None,
                rendered_prompt=self._render_recovery_prompt(source_text, analysis),
                errors=(
                    ValidationIssue(
                        code=analysis.fallback.reason or "unclassified_input",
                        message="지원하는 intent 또는 category 신호가 부족합니다.",
                    ),
                ),
                pipeline_steps=tuple(pipeline_steps),
            )

        pipeline_steps.append("generate_clarification_questions")
        clarification_questions = self._adaptive_grill.generate(source_text, analysis)

        pipeline_steps.append("generate_rif")
        rif = self._rif_engine.generate(source_text, analysis)

        pipeline_steps.append("match_patterns")
        pattern_matches = self._pattern_library.match(source_text, analysis)

        pipeline_steps.append("inject_constraints")
        constraint_output = self._inject_constraints(analysis)

        prompt_ir = self._build_prompt_ir(
            source_text=source_text,
            target=selected_target,
            analysis=analysis,
            rif=rif,
            constraint_output=constraint_output,
        )

        pipeline_steps.append("apply_pattern_defaults")
        prompt_ir = self._apply_pattern_defaults(prompt_ir, pattern_matches)

        optimized_quality_score = self._quality_scorer.score_prompt_ir(prompt_ir)
        prompt_ir["qualityScore"] = optimized_quality_score.to_prompt_ir_score()

        pipeline_steps.append("render_prompt")
        rendered_prompt = self._renderer.render(prompt_ir)

        return OptimizerResult(
            source_text=source_text,
            target=selected_target,
            analysis=analysis,
            clarification_questions=clarification_questions,
            pattern_matches=pattern_matches,
            source_quality_score=source_quality_score,
            optimized_quality_score=optimized_quality_score,
            prompt_ir=prompt_ir,
            rendered_prompt=rendered_prompt,
            errors=(),
            pipeline_steps=tuple(pipeline_steps),
        )

    def _validate_input(self, source_text: str, target: str) -> ValidationIssue | None:
        normalized = " ".join(source_text.split())
        if not normalized:
            return ValidationIssue(code="empty_input", message="원본 사용자 프롬프트가 비어 있습니다.")
        if len(normalized) < 4:
            return ValidationIssue(code="too_short_input", message="원본 사용자 프롬프트가 너무 짧습니다.")
        if target not in SUPPORTED_TARGETS:
            return ValidationIssue(code="unsupported_target", message=f"지원하지 않는 target입니다: {target}")
        return None

    def _inject_constraints(self, analysis: AnalyzerResult) -> ConstraintOutput:
        constraints = [
            {
                "id": "CON-1",
                "scope": "maintainability",
                "description": "최종 프롬프트를 렌더링하기 전까지 구조화된 IR 필드를 유지합니다.",
            },
            {
                "id": "CON-2",
                "scope": "testing",
                "description": "렌더링 결과에 자체 검증 항목을 포함합니다.",
            },
        ]

        if analysis.category == Category.BACKEND:
            constraints.append(
                {
                    "id": "CON-3",
                    "scope": "security",
                    "description": "인증, 입력 검증, 오류 처리 같은 백엔드 안전 조건을 고려합니다.",
                }
            )
        elif analysis.category == Category.FRONTEND:
            constraints.append(
                {
                    "id": "CON-3",
                    "scope": "style",
                    "description": "로딩, 오류, 빈 상태와 접근성을 함께 고려합니다.",
                }
            )
        elif analysis.category == Category.AI:
            constraints.append(
                {
                    "id": "CON-3",
                    "scope": "architecture",
                    "description": "모델 호출, 검색, fallback 경계를 분리합니다.",
                }
            )
        elif analysis.category == Category.DEVOPS:
            constraints.append(
                {
                    "id": "CON-3",
                    "scope": "deployment",
                    "description": "secret 노출 없이 rollback과 상태 확인을 고려합니다.",
                }
            )
        elif analysis.category == Category.ARCHITECTURE:
            constraints.append(
                {
                    "id": "CON-3",
                    "scope": "architecture",
                    "description": "모듈 경계, 의존성 방향, tradeoff를 명시합니다.",
                }
            )

        validation_rules = (
            {
                "id": "VAL-1",
                "description": "감지된 intent와 category가 최종 프롬프트 목표에 반영되어 있는지 확인합니다.",
                "severity": "error",
            },
            {
                "id": "VAL-2",
                "description": "요구사항, 제약조건, 출력 형식, 검증 항목이 누락되지 않았는지 확인합니다.",
                "severity": "error",
            },
        )
        return ConstraintOutput(constraints=tuple(constraints), validation_rules=validation_rules)

    def _build_prompt_ir(
        self,
        source_text: str,
        target: str,
        analysis: AnalyzerResult,
        rif: RifOutput,
        constraint_output: ConstraintOutput,
    ) -> dict[str, object]:
        action = self._prompt_ir_action_for(analysis.intent)
        primary_domain = self._prompt_ir_domain_for(analysis.category)
        return {
            "schemaVersion": "1.0.0",
            "id": self._stable_id(source_text, target),
            "sourceText": source_text,
            "intent": {
                "summary": f"{analysis.intent.value} 요청을 {analysis.category.value} 도메인으로 최적화합니다.",
                "action": action,
                "primaryDomain": primary_domain,
                "relatedDomains": self._related_domains_for(analysis.category),
            },
            "context": {
                "audience": rif.role.title,
                "projectState": "사용자 원문 요청을 Prompt-Booster 파이프라인에서 최적화하는 단계입니다.",
                "techStack": self._tech_stack_for(analysis.category),
                "assumptions": [
                    f"target={target}",
                    "Analyzer 결과를 RIF 생성, constraint 주입, 렌더링 순서로 처리합니다.",
                ],
            },
            "requirements": self._requirements_for(rif, analysis),
            "constraints": list(constraint_output.constraints),
            "outputSpec": {
                "format": "markdown",
                "sections": [section.to_dict() for section in rif.format_sections],
            },
            "validationRules": list(constraint_output.validation_rules),
        }

    def _requirements_for(self, rif: RifOutput, analysis: AnalyzerResult) -> list[dict[str, object]]:
        return [
            {
                "id": "REQ-1",
                "category": "functional",
                "description": rif.instruction.objective,
                "priority": "must",
                "acceptanceCriteria": list(rif.instruction.expectations),
            },
            {
                "id": "REQ-2",
                "category": "functional",
                "description": "Role, Instruction, Format 기반 프롬프트 구조를 생성합니다.",
                "priority": "must",
                "acceptanceCriteria": [
                    f"{section.title} 섹션은 {section.description}"
                    for section in rif.format_sections
                ],
            },
            {
                "id": "REQ-3",
                "category": "testing",
                "description": f"Analyzer confidence {analysis.confidence} 결과를 검증 정보로 유지합니다.",
                "priority": "should",
                "acceptanceCriteria": [
                    "분석 결과와 렌더링 결과를 테스트에서 함께 확인할 수 있습니다.",
                ],
            },
        ]

    def _apply_pattern_defaults(
        self,
        prompt_ir: dict[str, object],
        pattern_matches: tuple[PatternMatch, ...],
    ) -> dict[str, object]:
        if not pattern_matches:
            return prompt_ir

        merged = dict(prompt_ir)
        context = dict(self._mapping(merged.get("context")))
        assumptions = list(self._text_items(context.get("assumptions")))
        assumptions.append(
            "적용된 패턴: "
            + ", ".join(match.pattern.id for match in self._ranked_pattern_matches(pattern_matches))
        )

        requirements = list(self._mapping_items(merged.get("requirements")))
        constraints = list(self._mapping_items(merged.get("constraints")))
        output_spec = dict(self._mapping(merged.get("outputSpec")))
        output_sections = list(self._mapping_items(output_spec.get("sections")))
        validation_rules = list(self._mapping_items(merged.get("validationRules")))
        pattern_formats: list[tuple[str, str]] = []

        for match in self._ranked_pattern_matches(pattern_matches):
            defaults = match.pattern.to_prompt_defaults()
            requirements.extend(defaults.requirements)
            constraints.extend(defaults.constraints)
            output_sections.extend(self._mapping_items(defaults.output_spec.get("sections")))
            validation_rules.extend(defaults.validation_rules)
            pattern_formats.append((match.pattern.id, str(defaults.output_spec["format"])))

        output_format, format_conflicts = self._resolve_output_format(
            current_format=str(output_spec.get("format", "markdown")),
            pattern_formats=tuple(pattern_formats),
        )
        if format_conflicts:
            assumptions.append(
                "패턴 출력 형식 충돌은 "
                f"{pattern_formats[0][0]}의 {output_format} 추천값으로 결정합니다: "
                + ", ".join(f"{pattern_id}={format_name}" for pattern_id, format_name in format_conflicts)
            )

        context["assumptions"] = self._dedupe_texts(assumptions)
        output_spec["format"] = output_format
        output_spec["sections"] = self._dedupe_output_sections(output_sections)
        merged["context"] = context
        merged["requirements"] = self._dedupe_items_with_ids(requirements, "REQ", self._requirement_key)
        merged["constraints"] = self._dedupe_items_with_ids(constraints, "CON", self._constraint_key)
        merged["outputSpec"] = output_spec
        merged["validationRules"] = self._dedupe_items_with_ids(validation_rules, "VAL", self._validation_rule_key)
        return merged

    def _ranked_pattern_matches(self, pattern_matches: tuple[PatternMatch, ...]) -> tuple[PatternMatch, ...]:
        return tuple(sorted(pattern_matches, key=lambda match: (match.rank or 9999, -match.score, match.pattern.id)))

    def _resolve_output_format(
        self,
        current_format: str,
        pattern_formats: tuple[tuple[str, str], ...],
    ) -> tuple[str, tuple[tuple[str, str], ...]]:
        if not pattern_formats:
            return current_format, ()

        _, selected_format = pattern_formats[0]
        conflicts = tuple(
            (pattern_id, format_name)
            for pattern_id, format_name in pattern_formats[1:]
            if format_name != selected_format
        )
        return selected_format, conflicts

    def _dedupe_items_with_ids(
        self,
        items: Sequence[Mapping[str, object]],
        prefix: str,
        key_factory: Callable[[Mapping[str, object]], tuple[object, ...]],
    ) -> list[dict[str, object]]:
        deduped: list[dict[str, object]] = []
        seen: set[tuple[object, ...]] = set()
        for item in items:
            key = key_factory(item)
            if key in seen:
                continue
            seen.add(key)
            next_item = dict(item)
            next_item["id"] = f"{prefix}-{len(deduped) + 1}"
            deduped.append(next_item)
        return deduped

    def _dedupe_output_sections(self, sections: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
        deduped: list[dict[str, object]] = []
        seen: set[tuple[object, ...]] = set()
        for section in sections:
            key = self._output_section_key(section)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(dict(section))
        return deduped

    def _requirement_key(self, requirement: Mapping[str, object]) -> tuple[object, ...]:
        return (
            self._normalize_key(requirement.get("category")),
            self._normalize_key(requirement.get("description")),
            self._normalize_key(requirement.get("priority")),
            tuple(self._normalize_key(item) for item in self._text_items(requirement.get("acceptanceCriteria"))),
        )

    def _constraint_key(self, constraint: Mapping[str, object]) -> tuple[object, ...]:
        return (
            self._normalize_key(constraint.get("scope")),
            self._normalize_key(constraint.get("description")),
        )

    def _output_section_key(self, section: Mapping[str, object]) -> tuple[object, ...]:
        return (
            self._normalize_key(section.get("title")),
            self._normalize_key(section.get("description")),
            bool(section.get("required")),
        )

    def _validation_rule_key(self, rule: Mapping[str, object]) -> tuple[object, ...]:
        return (
            self._normalize_key(rule.get("severity")),
            self._normalize_key(rule.get("description")),
        )

    def _mapping(self, value: object) -> Mapping[str, object]:
        if isinstance(value, Mapping):
            return value
        return {}

    def _mapping_items(self, value: object) -> tuple[Mapping[str, object], ...]:
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            return ()
        return tuple(item for item in value if isinstance(item, Mapping))

    def _text_items(self, value: object) -> tuple[str, ...]:
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            return ()
        return tuple(str(item).strip() for item in value if str(item).strip())

    def _dedupe_texts(self, values: Sequence[str]) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()
        for value in values:
            key = self._normalize_key(value)
            if not key or key in seen:
                continue
            seen.add(key)
            result.append(value)
        return result

    def _normalize_key(self, value: object) -> str:
        return " ".join(str(value).casefold().split())

    def _render_recovery_prompt(self, source_text: str, analysis: AnalyzerResult) -> str:
        return "\n".join(
            [
                "# Prompt-Booster Recovery",
                "",
                f"Source: {source_text}",
                f"Fallback: {analysis.fallback.reason}",
                "",
                "지원하는 개발 작업 의도나 도메인을 더 구체적으로 입력해야 합니다.",
            ]
        )

    def _prompt_ir_action_for(self, intent: IntentType | None) -> str:
        mapping = {
            IntentType.CODE_GENERATION: "implement",
            IntentType.SYSTEM_DESIGN: "design",
            IntentType.REFACTORING: "optimize",
            IntentType.DEBUGGING: "debug",
            IntentType.TEST_GENERATION: "implement",
            IntentType.DEVOPS: "deploy",
            IntentType.ARCHITECTURE: "design",
        }
        return mapping[intent or IntentType.CODE_GENERATION]

    def _prompt_ir_domain_for(self, category: Category | None) -> str:
        return (category or Category.BACKEND).value

    def _related_domains_for(self, category: Category | None) -> list[str]:
        if category in (Category.BACKEND, Category.FRONTEND, Category.AI, Category.DEVOPS):
            return ["architecture"]
        return []

    def _tech_stack_for(self, category: Category | None) -> list[str]:
        stacks = {
            Category.BACKEND: ["API", "Service", "Persistence"],
            Category.FRONTEND: ["UI", "State", "Component"],
            Category.AI: ["LLM", "Embedding", "Evaluation"],
            Category.DEVOPS: ["CI", "Deployment", "Observability"],
            Category.ARCHITECTURE: ["Boundary", "Dependency Rule", "Tradeoff"],
        }
        return stacks[category or Category.BACKEND]

    def _resolve_pattern_library(
        self,
        pattern_library: PatternLibrary | Mapping[str, object] | str | PathLike[str] | None,
    ) -> PatternLibrary:
        if pattern_library is None:
            return PatternLibrary.load_default()
        if isinstance(pattern_library, PatternLibrary):
            return pattern_library
        if isinstance(pattern_library, Mapping):
            return PatternLibrary.from_dict(pattern_library)
        if isinstance(pattern_library, (str, PathLike)):
            return PatternLibrary.from_file(pattern_library)
        raise TypeError("pattern_library는 PatternLibrary, dict, path 중 하나여야 합니다.")

    def _stable_id(self, source_text: str, target: str) -> str:
        digest = hashlib.sha1(f"{target}\n{source_text}".encode("utf-8")).hexdigest()[:12]
        return f"prompt-request-{digest}"


def optimize_prompt(source_text: str, target: str | None = None) -> OptimizerResult:
    return PromptOptimizer().optimize(source_text, target)
