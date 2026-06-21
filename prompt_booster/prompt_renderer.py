from __future__ import annotations

from collections.abc import Mapping, Sequence


class PromptRenderer:
    def render(self, prompt_ir: Mapping[str, object]) -> str:
        intent = self._mapping(prompt_ir.get("intent"))
        context = self._mapping(prompt_ir.get("context"))
        output_spec = self._mapping(prompt_ir.get("outputSpec"))

        requirements = self._compact_requirements(self._mapping_items(prompt_ir.get("requirements")))
        constraints = self._compact_constraints(self._mapping_items(prompt_ir.get("constraints")))
        output_sections = self._compact_output_sections(self._mapping_items(output_spec.get("sections")))
        validation_rules = self._compact_validation_rules(self._mapping_items(prompt_ir.get("validationRules")))

        sections = [
            ("Role", self._role_lines(context)),
            ("Instruction", self._instruction_lines(intent)),
            ("Requirements", self._requirement_lines(requirements)),
            ("Constraints", self._constraint_lines(constraints)),
            ("Output Format", self._output_format_lines(output_sections)),
            ("Validation", self._validation_lines(validation_rules)),
        ]

        lines = ["# Optimized Prompt"]
        for title, section_lines in sections:
            if not section_lines:
                continue
            lines.extend(("", f"## {title}", *section_lines))
        return "\n".join(lines)

    def _role_lines(self, context: Mapping[str, object]) -> tuple[str, ...]:
        return self._unique_non_empty([context.get("audience")])

    def _instruction_lines(self, intent: Mapping[str, object]) -> tuple[str, ...]:
        return self._unique_non_empty([intent.get("summary")])

    def _requirement_lines(self, requirements: tuple[Mapping[str, object], ...]) -> tuple[str, ...]:
        lines: list[str] = []
        for requirement in requirements:
            description = self._text(requirement.get("description"))
            if description:
                priority = self._text(requirement.get("priority"))
                lines.append(self._prefix_with_tag(description, priority))
            for criterion in self._text_items(requirement.get("acceptanceCriteria")):
                lines.append(f"  - {criterion}")
        return self._unique_non_empty(lines)

    def _constraint_lines(self, constraints: tuple[Mapping[str, object], ...]) -> tuple[str, ...]:
        return self._unique_non_empty(
            self._prefix_with_tag(constraint.get("description"), constraint.get("scope"))
            for constraint in constraints
        )

    def _output_format_lines(self, sections: tuple[Mapping[str, object], ...]) -> tuple[str, ...]:
        lines = []
        for section in sections:
            title = self._text(section.get("title"))
            description = self._text(section.get("description"))
            if title and description:
                lines.append(f"- {title}: {description}")
            elif title:
                lines.append(f"- {title}")
            elif description:
                lines.append(f"- {description}")
        return self._unique_non_empty(lines)

    def _validation_lines(self, rules: tuple[Mapping[str, object], ...]) -> tuple[str, ...]:
        return self._unique_non_empty(
            self._prefix_with_tag(rule.get("description"), rule.get("severity"))
            for rule in rules
        )

    def _compact_requirements(
        self,
        requirements: tuple[Mapping[str, object], ...],
    ) -> tuple[Mapping[str, object], ...]:
        compacted: list[dict[str, object]] = []
        by_description: dict[str, dict[str, object]] = {}
        for requirement in requirements:
            description = self._text(requirement.get("description"))
            if not description:
                continue

            key = self._normalize_key(description)
            priority = self._text(requirement.get("priority"))
            acceptance_criteria = list(self._text_items(requirement.get("acceptanceCriteria")))
            existing = by_description.get(key)
            if existing is None:
                next_requirement = dict(requirement)
                next_requirement["description"] = description
                next_requirement["priority"] = priority
                next_requirement["acceptanceCriteria"] = acceptance_criteria
                by_description[key] = next_requirement
                compacted.append(next_requirement)
                continue

            if self._priority_rank(priority) > self._priority_rank(existing.get("priority")):
                existing["priority"] = priority
            existing["acceptanceCriteria"] = self._unique_texts(
                [*self._text_items(existing.get("acceptanceCriteria")), *acceptance_criteria]
            )
        return tuple(compacted)

    def _compact_constraints(
        self,
        constraints: tuple[Mapping[str, object], ...],
    ) -> tuple[Mapping[str, object], ...]:
        return self._compact_tagged_descriptions(constraints, "scope")

    def _compact_validation_rules(
        self,
        rules: tuple[Mapping[str, object], ...],
    ) -> tuple[Mapping[str, object], ...]:
        compacted: list[dict[str, object]] = []
        by_description: dict[str, dict[str, object]] = {}
        for rule in rules:
            description = self._text(rule.get("description"))
            if not description:
                continue

            key = self._normalize_key(description)
            severity = self._text(rule.get("severity"))
            existing = by_description.get(key)
            if existing is None:
                next_rule = dict(rule)
                next_rule["description"] = description
                next_rule["severity"] = severity
                by_description[key] = next_rule
                compacted.append(next_rule)
                continue

            if self._severity_rank(severity) > self._severity_rank(existing.get("severity")):
                existing["severity"] = severity
        return tuple(compacted)

    def _compact_output_sections(
        self,
        sections: tuple[Mapping[str, object], ...],
    ) -> tuple[Mapping[str, object], ...]:
        compacted: list[dict[str, object]] = []
        by_title: dict[str, dict[str, object]] = {}
        for section in sections:
            title = self._text(section.get("title"))
            description = self._text(section.get("description"))
            if not title and not description:
                continue

            key = self._normalize_key(title or description)
            existing = by_title.get(key)
            if existing is None:
                next_section = dict(section)
                next_section["title"] = title
                next_section["description"] = description
                next_section["required"] = bool(section.get("required"))
                by_title[key] = next_section
                compacted.append(next_section)
                continue

            descriptions = self._unique_texts(
                [*self._split_compacted_description(existing.get("description")), description]
            )
            existing["description"] = "; ".join(descriptions)
            existing["required"] = bool(existing.get("required")) or bool(section.get("required"))
        return tuple(compacted)

    def _compact_tagged_descriptions(
        self,
        items: tuple[Mapping[str, object], ...],
        tag_field: str,
    ) -> tuple[Mapping[str, object], ...]:
        compacted: list[dict[str, object]] = []
        by_description: dict[str, dict[str, object]] = {}
        for item in items:
            description = self._text(item.get("description"))
            if not description:
                continue

            key = self._normalize_key(description)
            tag = self._text(item.get(tag_field))
            existing = by_description.get(key)
            if existing is None:
                next_item = dict(item)
                next_item["description"] = description
                next_item[tag_field] = tag
                by_description[key] = next_item
                compacted.append(next_item)
                continue

            tags = self._unique_texts([*self._split_tags(existing.get(tag_field)), tag])
            existing[tag_field] = ", ".join(tags)
        return tuple(compacted)

    def _prefix_with_tag(self, description_value: object, tag_value: object) -> str:
        description = self._text(description_value)
        tag = self._text(tag_value)
        if not description:
            return ""
        if not tag:
            return f"- {description}"
        return f"- [{tag}] {description}"

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
        return self._unique_non_empty(value)

    def _unique_non_empty(self, values: object) -> tuple[str, ...]:
        result: list[str] = []
        seen: set[str] = set()
        for value in values:
            raw_text = "" if value is None else str(value)
            normalized = raw_text.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            if raw_text[:1].isspace():
                result.append(raw_text.rstrip())
            else:
                result.append(normalized)
        return tuple(result)

    def _text(self, value: object) -> str:
        if value is None:
            return ""
        return str(value).strip()

    def _unique_texts(self, values: Sequence[object]) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()
        for value in values:
            text = self._text(value)
            key = self._normalize_key(text)
            if not key or key in seen:
                continue
            seen.add(key)
            result.append(text)
        return result

    def _split_tags(self, value: object) -> tuple[str, ...]:
        return tuple(part.strip() for part in self._text(value).split(",") if part.strip())

    def _split_compacted_description(self, value: object) -> tuple[str, ...]:
        return tuple(part.strip() for part in self._text(value).split(";") if part.strip())

    def _priority_rank(self, value: object) -> int:
        return {"must": 3, "should": 2, "could": 1}.get(self._text(value), 0)

    def _severity_rank(self, value: object) -> int:
        return {"error": 3, "warning": 2, "info": 1}.get(self._text(value), 0)

    def _normalize_key(self, value: object) -> str:
        return " ".join(self._text(value).casefold().split())
