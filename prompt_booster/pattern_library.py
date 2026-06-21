from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
from os import PathLike
from pathlib import Path

from .intent_analyzer import AnalyzerResult, Category, IntentType


DEFAULT_PATTERN_PATH = Path(__file__).resolve().parents[1] / "patterns" / "core.json"
SUPPORTED_PATTERN_SCHEMA_VERSION = "1.0.0"
SUPPORTED_CATEGORIES = tuple(category.value for category in Category)
SUPPORTED_INTENT_HINTS = tuple(intent.value for intent in IntentType)
REQUIREMENT_CATEGORIES = (
    "functional",
    "nonFunctional",
    "security",
    "data",
    "integration",
    "testing",
    "documentation",
)
CONSTRAINT_SCOPES = (
    "security",
    "performance",
    "maintainability",
    "compatibility",
    "architecture",
    "testing",
    "deployment",
    "style",
)
OUTPUT_FORMATS = ("markdown", "json", "yaml", "code", "mixed")
VALIDATION_SEVERITIES = ("error", "warning", "info")


class PatternLibraryValidationError(ValueError):
    pass


@dataclass(frozen=True)
class PatternRequirementTemplate:
    category: str
    priority: str
    description_ref: str
    acceptance_criteria_refs: tuple[str, ...]


@dataclass(frozen=True)
class PatternConstraintTemplate:
    scope: str
    description_ref: str


@dataclass(frozen=True)
class PatternOutputSectionTemplate:
    title_ref: str
    description_ref: str
    required: bool


@dataclass(frozen=True)
class PatternOutputFormatTemplate:
    format: str
    sections: tuple[PatternOutputSectionTemplate, ...]


@dataclass(frozen=True)
class PatternValidationTemplate:
    severity: str
    description_ref: str


@dataclass(frozen=True)
class PatternMatchingMetadata:
    intent_hints: tuple[str, ...]
    domain_signals: tuple[str, ...]
    confidence_weight: int

    def to_dict(self) -> dict[str, object]:
        return {
            "intentHints": list(self.intent_hints),
            "domainSignals": list(self.domain_signals),
            "confidenceWeight": self.confidence_weight,
        }


@dataclass(frozen=True)
class PatternPromptDefaults:
    requirements: tuple[dict[str, object], ...]
    constraints: tuple[dict[str, str], ...]
    output_spec: dict[str, object]
    validation_rules: tuple[dict[str, str], ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "requirements": [dict(requirement) for requirement in self.requirements],
            "constraints": [dict(constraint) for constraint in self.constraints],
            "outputSpec": self.output_spec,
            "validationRules": [dict(rule) for rule in self.validation_rules],
        }


@dataclass(frozen=True)
class PromptPattern:
    id: str
    category: str
    keywords: tuple[str, ...]
    default_locale: str
    locales: Mapping[str, Mapping[str, str]]
    default_requirements: tuple[PatternRequirementTemplate, ...]
    default_constraints: tuple[PatternConstraintTemplate, ...]
    recommended_output_format: PatternOutputFormatTemplate
    validation_items: tuple[PatternValidationTemplate, ...]
    matching_metadata: PatternMatchingMetadata
    supported_locales: tuple[str, ...]
    agent_profiles: tuple[str, ...]

    def resolve_text(self, ref: str, locale: str | None = None) -> str:
        selected_locale = locale or self.default_locale
        locale_fragments = self.locales.get(selected_locale) or self.locales[self.default_locale]
        return locale_fragments[ref]

    def to_prompt_defaults(self, locale: str | None = None) -> PatternPromptDefaults:
        requirements = tuple(
            {
                "category": requirement.category,
                "priority": requirement.priority,
                "description": self.resolve_text(requirement.description_ref, locale),
                "acceptanceCriteria": [
                    self.resolve_text(ref, locale)
                    for ref in requirement.acceptance_criteria_refs
                ],
            }
            for requirement in self.default_requirements
        )
        constraints = tuple(
            {
                "scope": constraint.scope,
                "description": self.resolve_text(constraint.description_ref, locale),
            }
            for constraint in self.default_constraints
        )
        output_spec = {
            "format": self.recommended_output_format.format,
            "sections": [
                {
                    "title": self.resolve_text(section.title_ref, locale),
                    "description": self.resolve_text(section.description_ref, locale),
                    "required": section.required,
                }
                for section in self.recommended_output_format.sections
            ],
        }
        validation_rules = tuple(
            {
                "description": self.resolve_text(item.description_ref, locale),
                "severity": item.severity,
            }
            for item in self.validation_items
        )
        return PatternPromptDefaults(
            requirements=requirements,
            constraints=constraints,
            output_spec=output_spec,
            validation_rules=validation_rules,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "category": self.category,
            "keywords": list(self.keywords),
            "matchingMetadata": self.matching_metadata.to_dict(),
            "defaultLocale": self.default_locale,
            "supportedLocales": list(self.supported_locales),
            "agentProfiles": list(self.agent_profiles),
        }


@dataclass(frozen=True)
class PatternMatch:
    pattern: PromptPattern
    matched_keywords: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.pattern.id,
            "category": self.pattern.category,
            "matchedKeywords": list(self.matched_keywords),
        }


class PatternLibrary:
    def __init__(self, patterns: Sequence[PromptPattern]) -> None:
        self.patterns = tuple(patterns)
        self._patterns_by_id = {pattern.id: pattern for pattern in self.patterns}

    @classmethod
    def load_default(cls) -> PatternLibrary:
        return cls.from_file(DEFAULT_PATTERN_PATH)

    @classmethod
    def from_file(cls, path: str | PathLike[str]) -> PatternLibrary:
        with Path(path).open(encoding="utf-8") as file:
            return cls.from_dict(json.load(file))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> PatternLibrary:
        return PatternLibrary(_parse_payload(payload))

    def get(self, pattern_id: str) -> PromptPattern:
        return self._patterns_by_id[pattern_id]

    def match(self, source_text: str, analysis: AnalyzerResult) -> tuple[PatternMatch, ...]:
        if analysis.category is None:
            return ()

        normalized_source = _normalize(source_text)
        signal_keywords = {_normalize(signal.keyword) for signal in analysis.matched_signals}
        category = analysis.category.value
        matches: list[PatternMatch] = []

        for pattern in self.patterns:
            if pattern.category != category:
                continue
            matched_keywords = tuple(
                keyword
                for keyword in pattern.keywords
                if _normalize(keyword) in normalized_source or _normalize(keyword) in signal_keywords
            )
            if matched_keywords:
                matches.append(PatternMatch(pattern=pattern, matched_keywords=matched_keywords))

        return tuple(matches)

    def to_dict(self) -> dict[str, object]:
        return {
            "patterns": [pattern.to_dict() for pattern in self.patterns],
        }


def _parse_payload(payload: Mapping[str, object]) -> tuple[PromptPattern, ...]:
    _require_mapping(payload, "$")
    _require(payload.get("schemaVersion") == SUPPORTED_PATTERN_SCHEMA_VERSION, "$.schemaVersion: 지원하지 않는 버전입니다.")
    raw_patterns = _require_mapping_list(payload.get("patterns"), "$.patterns")
    patterns = tuple(_parse_pattern(raw_pattern, f"$.patterns[{index}]") for index, raw_pattern in enumerate(raw_patterns))
    ids = [pattern.id for pattern in patterns]
    _require(len(ids) == len(set(ids)), "$.patterns: pattern id가 중복되었습니다.")
    return patterns


def _parse_pattern(raw_pattern: Mapping[str, object], path: str) -> PromptPattern:
    required_fields = {
        "id",
        "category",
        "keywords",
        "defaultLocale",
        "locales",
        "defaultRequirements",
        "defaultConstraints",
        "recommendedOutputFormat",
        "validationItems",
        "matchingMetadata",
        "renderingHints",
    }
    _require_required_fields(raw_pattern, required_fields, path)

    pattern_id = _require_text(raw_pattern.get("id"), f"{path}.id")
    category = _require_allowed(raw_pattern.get("category"), SUPPORTED_CATEGORIES, f"{path}.category")
    keywords = _require_text_list(raw_pattern.get("keywords"), f"{path}.keywords")
    _require(len(keywords) == len(set(keywords)), f"{path}.keywords: 중복 키워드가 있습니다.")
    default_locale = _require_text(raw_pattern.get("defaultLocale"), f"{path}.defaultLocale")
    locales = _parse_locales(raw_pattern.get("locales"), f"{path}.locales")
    rendering_hints = _parse_rendering_hints(raw_pattern.get("renderingHints"), f"{path}.renderingHints")
    supported_locales = rendering_hints["supportedLocales"]
    agent_profiles = rendering_hints["agentProfiles"]
    _require(default_locale in supported_locales, f"{path}.defaultLocale: supportedLocales에 포함되어야 합니다.")
    _require(default_locale in locales, f"{path}.locales: defaultLocale 조각이 없습니다.")

    requirements = _parse_requirements(raw_pattern.get("defaultRequirements"), f"{path}.defaultRequirements")
    constraints = _parse_constraints(raw_pattern.get("defaultConstraints"), f"{path}.defaultConstraints")
    output_format = _parse_output_format(raw_pattern.get("recommendedOutputFormat"), f"{path}.recommendedOutputFormat")
    validation_items = _parse_validation_items(raw_pattern.get("validationItems"), f"{path}.validationItems")
    matching_metadata = _parse_matching_metadata(raw_pattern.get("matchingMetadata"), f"{path}.matchingMetadata")

    refs = _collect_refs(requirements, constraints, output_format, validation_items)
    for locale in supported_locales:
        _require(locale in locales, f"{path}.locales: supportedLocales의 {locale} 조각이 없습니다.")
        missing_refs = sorted(refs - set(locales[locale]))
        _require(not missing_refs, f"{path}.locales.{locale}: 참조 조각이 없습니다: {missing_refs}")

    return PromptPattern(
        id=pattern_id,
        category=category,
        keywords=keywords,
        default_locale=default_locale,
        locales=locales,
        default_requirements=requirements,
        default_constraints=constraints,
        recommended_output_format=output_format,
        validation_items=validation_items,
        matching_metadata=matching_metadata,
        supported_locales=supported_locales,
        agent_profiles=agent_profiles,
    )


def _parse_locales(value: object, path: str) -> dict[str, Mapping[str, str]]:
    raw_locales = _require_mapping(value, path)
    locales: dict[str, Mapping[str, str]] = {}
    for raw_locale, raw_fragments in raw_locales.items():
        locale = _require_text(raw_locale, f"{path} locale")
        fragments = _require_mapping(raw_fragments, f"{path}.{locale}")
        parsed_fragments = {
            _require_text(key, f"{path}.{locale} key"): _require_text(fragment, f"{path}.{locale}.{key}")
            for key, fragment in fragments.items()
        }
        _require(parsed_fragments, f"{path}.{locale}: 텍스트 조각이 비어 있습니다.")
        locales[locale] = parsed_fragments
    _require(locales, f"{path}: locale 정의가 필요합니다.")
    return locales


def _parse_rendering_hints(value: object, path: str) -> dict[str, tuple[str, ...]]:
    raw_hints = _require_mapping(value, path)
    _require_required_fields(raw_hints, {"supportedLocales", "agentProfiles"}, path)
    return {
        "supportedLocales": _require_text_list(raw_hints.get("supportedLocales"), f"{path}.supportedLocales"),
        "agentProfiles": _require_text_list(raw_hints.get("agentProfiles"), f"{path}.agentProfiles"),
    }


def _parse_requirements(value: object, path: str) -> tuple[PatternRequirementTemplate, ...]:
    raw_requirements = _require_mapping_list(value, path)
    result = []
    for index, raw_requirement in enumerate(raw_requirements):
        item_path = f"{path}[{index}]"
        _require_required_fields(
            raw_requirement,
            {"category", "priority", "descriptionRef", "acceptanceCriteriaRefs"},
            item_path,
        )
        result.append(
            PatternRequirementTemplate(
                category=_require_allowed(
                    raw_requirement.get("category"),
                    REQUIREMENT_CATEGORIES,
                    f"{item_path}.category",
                ),
                priority=_require_allowed(
                    raw_requirement.get("priority"),
                    ("must", "should", "could"),
                    f"{item_path}.priority",
                ),
                description_ref=_require_text(raw_requirement.get("descriptionRef"), f"{item_path}.descriptionRef"),
                acceptance_criteria_refs=_require_text_list(
                    raw_requirement.get("acceptanceCriteriaRefs"),
                    f"{item_path}.acceptanceCriteriaRefs",
                ),
            )
        )
    return tuple(result)


def _parse_constraints(value: object, path: str) -> tuple[PatternConstraintTemplate, ...]:
    raw_constraints = _require_mapping_list(value, path)
    result = []
    for index, raw_constraint in enumerate(raw_constraints):
        item_path = f"{path}[{index}]"
        _require_required_fields(raw_constraint, {"scope", "descriptionRef"}, item_path)
        result.append(
            PatternConstraintTemplate(
                scope=_require_allowed(raw_constraint.get("scope"), CONSTRAINT_SCOPES, f"{item_path}.scope"),
                description_ref=_require_text(raw_constraint.get("descriptionRef"), f"{item_path}.descriptionRef"),
            )
        )
    return tuple(result)


def _parse_output_format(value: object, path: str) -> PatternOutputFormatTemplate:
    raw_output_format = _require_mapping(value, path)
    _require_required_fields(raw_output_format, {"format", "sections"}, path)
    sections = []
    for index, raw_section in enumerate(_require_mapping_list(raw_output_format.get("sections"), f"{path}.sections")):
        item_path = f"{path}.sections[{index}]"
        _require_required_fields(raw_section, {"titleRef", "descriptionRef", "required"}, item_path)
        required = raw_section.get("required")
        _require(isinstance(required, bool), f"{item_path}.required: boolean 타입이어야 합니다.")
        sections.append(
            PatternOutputSectionTemplate(
                title_ref=_require_text(raw_section.get("titleRef"), f"{item_path}.titleRef"),
                description_ref=_require_text(raw_section.get("descriptionRef"), f"{item_path}.descriptionRef"),
                required=required,
            )
        )
    return PatternOutputFormatTemplate(
        format=_require_allowed(raw_output_format.get("format"), OUTPUT_FORMATS, f"{path}.format"),
        sections=tuple(sections),
    )


def _parse_validation_items(value: object, path: str) -> tuple[PatternValidationTemplate, ...]:
    raw_items = _require_mapping_list(value, path)
    result = []
    for index, raw_item in enumerate(raw_items):
        item_path = f"{path}[{index}]"
        _require_required_fields(raw_item, {"severity", "descriptionRef"}, item_path)
        result.append(
            PatternValidationTemplate(
                severity=_require_allowed(raw_item.get("severity"), VALIDATION_SEVERITIES, f"{item_path}.severity"),
                description_ref=_require_text(raw_item.get("descriptionRef"), f"{item_path}.descriptionRef"),
            )
        )
    return tuple(result)


def _parse_matching_metadata(value: object, path: str) -> PatternMatchingMetadata:
    raw_metadata = _require_mapping(value, path)
    _require_required_fields(raw_metadata, {"intentHints", "domainSignals", "confidenceWeight"}, path)
    confidence_weight = _require_int(raw_metadata.get("confidenceWeight"), f"{path}.confidenceWeight")
    _require(1 <= confidence_weight <= 5, f"{path}.confidenceWeight: 1부터 5 사이여야 합니다.")
    return PatternMatchingMetadata(
        intent_hints=tuple(
            _require_allowed(intent, SUPPORTED_INTENT_HINTS, f"{path}.intentHints[{index}]")
            for index, intent in enumerate(_require_text_list(raw_metadata.get("intentHints"), f"{path}.intentHints"))
        ),
        domain_signals=_require_text_list(raw_metadata.get("domainSignals"), f"{path}.domainSignals"),
        confidence_weight=confidence_weight,
    )


def _collect_refs(
    requirements: tuple[PatternRequirementTemplate, ...],
    constraints: tuple[PatternConstraintTemplate, ...],
    output_format: PatternOutputFormatTemplate,
    validation_items: tuple[PatternValidationTemplate, ...],
) -> set[str]:
    refs = set()
    for requirement in requirements:
        refs.add(requirement.description_ref)
        refs.update(requirement.acceptance_criteria_refs)
    refs.update(constraint.description_ref for constraint in constraints)
    for section in output_format.sections:
        refs.add(section.title_ref)
        refs.add(section.description_ref)
    refs.update(item.description_ref for item in validation_items)
    return refs


def _require_required_fields(value: Mapping[str, object], required_fields: set[str], path: str) -> None:
    missing = sorted(required_fields - set(value))
    _require(not missing, f"{path}: 필수 필드가 누락되었습니다: {missing}")


def _require_mapping(value: object, path: str) -> Mapping[str, object]:
    _require(isinstance(value, Mapping), f"{path}: object 타입이어야 합니다.")
    return value


def _require_mapping_list(value: object, path: str) -> tuple[Mapping[str, object], ...]:
    _require(isinstance(value, Sequence) and not isinstance(value, (str, bytes)), f"{path}: array 타입이어야 합니다.")
    _require(len(value) > 0, f"{path}: 최소 1개 항목이 필요합니다.")
    for index, item in enumerate(value):
        _require(isinstance(item, Mapping), f"{path}[{index}]: object 타입이어야 합니다.")
    return tuple(value)


def _require_text(value: object, path: str) -> str:
    _require(isinstance(value, str) and value.strip(), f"{path}: 비어 있지 않은 문자열이어야 합니다.")
    return value.strip()


def _require_text_list(value: object, path: str) -> tuple[str, ...]:
    _require(isinstance(value, Sequence) and not isinstance(value, (str, bytes)), f"{path}: array 타입이어야 합니다.")
    _require(len(value) > 0, f"{path}: 최소 1개 항목이 필요합니다.")
    return tuple(_require_text(item, f"{path}[{index}]") for index, item in enumerate(value))


def _require_int(value: object, path: str) -> int:
    _require(isinstance(value, int) and not isinstance(value, bool), f"{path}: integer 타입이어야 합니다.")
    return value


def _require_allowed(value: object, allowed_values: tuple[str, ...], path: str) -> str:
    text = _require_text(value, path)
    _require(text in allowed_values, f"{path}: 허용되지 않은 값입니다: {text}")
    return text


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PatternLibraryValidationError(f"패턴 정의 검증 실패: {message}")


def _normalize(text: str) -> str:
    return " ".join(text.casefold().split())
