from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .intent_analyzer import AnalyzerResult


CRITERION_MAXIMA: tuple[tuple[str, int], ...] = (
    ("role", 10),
    ("requirement", 25),
    ("constraint", 20),
    ("context", 15),
    ("outputFormat", 10),
    ("validation", 10),
    ("technicalSpecificity", 10),
)


@dataclass(frozen=True)
class QualityCriterion:
    name: str
    score: int
    max: int
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "score": self.score,
            "max": self.max,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class QualityDiagnostic:
    field: str
    severity: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "field": self.field,
            "severity": self.severity,
            "message": self.message,
        }


@dataclass(frozen=True)
class PromptQualityReport:
    total: int
    max: int
    criteria: tuple[QualityCriterion, ...]
    diagnostics: tuple[QualityDiagnostic, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "total": self.total,
            "max": self.max,
            "criteria": [criterion.to_dict() for criterion in self.criteria],
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }

    def to_prompt_ir_score(self) -> dict[str, object]:
        return {
            "total": self.total,
            "max": self.max,
            "criteria": [criterion.to_dict() for criterion in self.criteria],
        }


class PromptQualityScorer:
    def score_source_text(self, source_text: str, analysis: AnalyzerResult | None = None) -> PromptQualityReport:
        normalized = self._normalize(source_text)
        criteria = (
            self._source_role_score(normalized),
            self._source_requirement_score(normalized, analysis),
            self._source_constraint_score(normalized),
            self._source_context_score(normalized, analysis),
            self._source_output_format_score(normalized),
            self._source_validation_score(normalized),
            self._source_technical_specificity_score(normalized, analysis),
        )
        return self._report(criteria)

    def score_prompt_ir(self, prompt_ir: Mapping[str, object]) -> PromptQualityReport:
        context = self._mapping(prompt_ir.get("context"))
        output_spec = self._mapping(prompt_ir.get("outputSpec"))
        criteria = (
            self._ir_role_score(context),
            self._ir_requirement_score(self._mapping_items(prompt_ir.get("requirements"))),
            self._ir_constraint_score(self._mapping_items(prompt_ir.get("constraints"))),
            self._ir_context_score(context),
            self._ir_output_format_score(output_spec),
            self._ir_validation_score(self._mapping_items(prompt_ir.get("validationRules"))),
            self._ir_technical_specificity_score(prompt_ir),
        )
        return self._report(criteria)

    def _source_role_score(self, normalized: str) -> QualityCriterion:
        if self._has_any(normalized, ("act as", "as a", "role", "developer", "engineer", "architect", "개발자", "아키텍트", "역할")):
            return QualityCriterion("role", 10, 10, "수행 역할이 원문에 명시되어 있습니다.")
        return QualityCriterion("role", 0, 10, "수행 역할이 원문에 없습니다.")

    def _source_requirement_score(self, normalized: str, analysis: AnalyzerResult | None) -> QualityCriterion:
        score = 0
        if analysis and analysis.intent is not None:
            score += 6
        score += min(12, self._count_keywords(normalized, REQUIREMENT_KEYWORDS) * 3)
        if len(normalized.split()) >= 8:
            score += 4
        if self._has_any(normalized, ("with", "include", "including", "and", "포함", "함께")):
            score += 3
        score = min(25, score)
        if score >= 20:
            reason = "핵심 요구사항이 여러 항목으로 구체화되어 있습니다."
        elif score > 0:
            reason = "요구사항 신호는 있으나 세부 항목이 부족합니다."
        else:
            reason = "구체적인 요구사항이 없습니다."
        return QualityCriterion("requirement", score, 25, reason)

    def _source_constraint_score(self, normalized: str) -> QualityCriterion:
        score = min(20, self._count_keywords(normalized, CONSTRAINT_KEYWORDS) * 5)
        reason = "제약조건 신호가 원문에 포함되어 있습니다." if score else "제약조건이 원문에 없습니다."
        return QualityCriterion("constraint", score, 20, reason)

    def _source_context_score(self, normalized: str, analysis: AnalyzerResult | None) -> QualityCriterion:
        score = 0
        if analysis and analysis.category is not None:
            score += 5
        score += min(8, self._count_keywords(normalized, CONTEXT_KEYWORDS) * 2)
        if self._has_any(normalized, ("project", "existing", "legacy", "신규", "기존", "프로젝트")):
            score += 2
        score = min(15, score)
        if score >= 12:
            reason = "도메인과 구현 맥락이 충분히 드러납니다."
        elif score > 0:
            reason = "일부 도메인 맥락은 있으나 프로젝트 상태가 부족합니다."
        else:
            reason = "도메인 또는 프로젝트 맥락이 없습니다."
        return QualityCriterion("context", score, 15, reason)

    def _source_output_format_score(self, normalized: str) -> QualityCriterion:
        score = 10 if self._has_any(normalized, OUTPUT_FORMAT_KEYWORDS) else 0
        reason = "출력 형식이 원문에 명시되어 있습니다." if score else "출력 형식이 원문에 없습니다."
        return QualityCriterion("outputFormat", score, 10, reason)

    def _source_validation_score(self, normalized: str) -> QualityCriterion:
        score = min(10, self._count_keywords(normalized, VALIDATION_KEYWORDS) * 5)
        reason = "검증 또는 테스트 조건이 원문에 포함되어 있습니다." if score else "검증 조건이 원문에 없습니다."
        return QualityCriterion("validation", score, 10, reason)

    def _source_technical_specificity_score(self, normalized: str, analysis: AnalyzerResult | None) -> QualityCriterion:
        score = min(10, self._count_keywords(normalized, TECHNICAL_KEYWORDS) * 2)
        if analysis and analysis.matched_signals:
            score = min(10, score + min(4, len(analysis.matched_signals)))
        if score >= 8:
            reason = "기술 스택과 구현 단서가 충분히 구체적입니다."
        elif score > 0:
            reason = "일부 기술 단서는 있으나 구현 단위가 부족합니다."
        else:
            reason = "기술 구체성이 부족합니다."
        return QualityCriterion("technicalSpecificity", score, 10, reason)

    def _ir_role_score(self, context: Mapping[str, object]) -> QualityCriterion:
        score = 10 if self._text(context.get("audience")) else 0
        reason = "역할 또는 대상 독자가 정의되어 있습니다." if score else "역할 또는 대상 독자가 없습니다."
        return QualityCriterion("role", score, 10, reason)

    def _ir_requirement_score(self, requirements: tuple[Mapping[str, object], ...]) -> QualityCriterion:
        criteria_count = sum(1 for requirement in requirements if self._text_items(requirement.get("acceptanceCriteria")))
        score = min(25, (len(requirements) * 6) + (criteria_count * 2))
        if len(requirements) >= 3 and criteria_count >= 2:
            score = 25
        reason = "요구사항과 수용 기준이 구조화되어 있습니다." if score else "요구사항이 없습니다."
        return QualityCriterion("requirement", score, 25, reason)

    def _ir_constraint_score(self, constraints: tuple[Mapping[str, object], ...]) -> QualityCriterion:
        scopes = {self._text(constraint.get("scope")) for constraint in constraints if self._text(constraint.get("scope"))}
        score = min(20, (len(constraints) * 5) + len(scopes))
        if len(constraints) >= 3:
            score = 20
        reason = "공통 및 도메인 제약조건이 포함되어 있습니다." if score else "제약조건이 없습니다."
        return QualityCriterion("constraint", score, 20, reason)

    def _ir_context_score(self, context: Mapping[str, object]) -> QualityCriterion:
        score = 0
        if self._text(context.get("audience")):
            score += 4
        if self._text(context.get("projectState")):
            score += 4
        score += min(5, len(self._text_items(context.get("techStack"))) * 2)
        score += min(2, len(self._text_items(context.get("assumptions"))))
        score = min(15, score)
        reason = "대상, 상태, 기술 스택 맥락이 구조화되어 있습니다." if score else "맥락 정보가 없습니다."
        return QualityCriterion("context", score, 15, reason)

    def _ir_output_format_score(self, output_spec: Mapping[str, object]) -> QualityCriterion:
        sections = self._mapping_items(output_spec.get("sections"))
        score = 0
        if self._text(output_spec.get("format")):
            score += 4
        if sections:
            score += min(6, len(sections) * 2)
        score = min(10, score)
        reason = "출력 형식과 섹션이 정의되어 있습니다." if score else "출력 형식이 없습니다."
        return QualityCriterion("outputFormat", score, 10, reason)

    def _ir_validation_score(self, validation_rules: tuple[Mapping[str, object], ...]) -> QualityCriterion:
        score = min(10, len(validation_rules) * 5)
        reason = "자체 검증 규칙이 포함되어 있습니다." if score else "검증 규칙이 없습니다."
        return QualityCriterion("validation", score, 10, reason)

    def _ir_technical_specificity_score(self, prompt_ir: Mapping[str, object]) -> QualityCriterion:
        context = self._mapping(prompt_ir.get("context"))
        source_text = self._text(prompt_ir.get("sourceText"))
        requirements = self._mapping_items(prompt_ir.get("requirements"))
        tech_stack = self._text_items(context.get("techStack"))
        score = min(10, (len(tech_stack) * 2) + self._count_keywords(self._normalize(source_text), TECHNICAL_KEYWORDS))
        if requirements:
            score = min(10, score + min(2, len(requirements)))
        reason = "기술 스택과 구현 단위가 충분히 구체적입니다." if score >= 8 else "기술 구체성이 일부 부족합니다."
        return QualityCriterion("technicalSpecificity", score, 10, reason)

    def _report(self, criteria: tuple[QualityCriterion, ...]) -> PromptQualityReport:
        total = max(0, min(100, sum(criterion.score for criterion in criteria)))
        return PromptQualityReport(total=total, max=100, criteria=criteria, diagnostics=self._diagnostics(criteria))

    def _diagnostics(self, criteria: tuple[QualityCriterion, ...]) -> tuple[QualityDiagnostic, ...]:
        diagnostics: list[QualityDiagnostic] = []
        for criterion in criteria:
            if criterion.score >= criterion.max:
                continue
            severity = "missing" if criterion.score == 0 else "weak"
            severity_label = "누락" if severity == "missing" else "약함"
            diagnostics.append(
                QualityDiagnostic(
                    field=criterion.name,
                    severity=severity,
                    message=f"{criterion.name} 항목이 {severity_label} 상태입니다. {criterion.reason}",
                )
            )
        return tuple(diagnostics)

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

    def _text(self, value: object) -> str:
        if value is None:
            return ""
        return str(value).strip()

    def _normalize(self, text: str) -> str:
        return " ".join(text.casefold().split())

    def _has_any(self, normalized: str, keywords: tuple[str, ...]) -> bool:
        return any(keyword in normalized for keyword in keywords)

    def _count_keywords(self, normalized: str, keywords: tuple[str, ...]) -> int:
        return sum(1 for keyword in keywords if keyword in normalized)


REQUIREMENT_KEYWORDS = (
    "implement",
    "build",
    "create",
    "design",
    "refactor",
    "debug",
    "api",
    "login",
    "crud",
    "rag",
    "chatbot",
    "dashboard",
    "구현",
    "설계",
    "리팩토링",
    "로그인",
    "게시판",
)

CONSTRAINT_KEYWORDS = (
    "security",
    "error",
    "exception",
    "performance",
    "accessibility",
    "rollback",
    "validation",
    "maintainability",
    "보안",
    "오류",
    "예외",
    "성능",
    "접근성",
    "검증",
)

CONTEXT_KEYWORDS = (
    "spring",
    "react",
    "next.js",
    "jwt",
    "rag",
    "docker",
    "kubernetes",
    "github actions",
    "backend",
    "frontend",
    "ai",
    "devops",
    "architecture",
    "api",
    "database",
)

OUTPUT_FORMAT_KEYWORDS = (
    "markdown",
    "json",
    "yaml",
    "section",
    "sections",
    "checklist",
    "format",
    "return",
    "출력",
    "형식",
    "섹션",
    "체크리스트",
)

VALIDATION_KEYWORDS = (
    "test",
    "tests",
    "unit test",
    "integration test",
    "validation",
    "validate",
    "verify",
    "checklist",
    "테스트",
    "검증",
    "확인",
)

TECHNICAL_KEYWORDS = (
    "spring",
    "securityfilterchain",
    "userdetailsservice",
    "controller",
    "service",
    "repository",
    "dto",
    "jwt",
    "token",
    "api",
    "react",
    "component",
    "state",
    "rag",
    "embedding",
    "vector",
    "docker",
    "kubernetes",
    "ci",
    "cd",
)
