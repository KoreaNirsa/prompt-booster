from __future__ import annotations

from collections.abc import Mapping, Sequence


class PromptRenderer:
    def render(self, prompt_ir: Mapping[str, object]) -> str:
        intent = self._mapping(prompt_ir.get("intent"))
        context = self._mapping(prompt_ir.get("context"))
        output_spec = self._mapping(prompt_ir.get("outputSpec"))

        requirements = self._mapping_items(prompt_ir.get("requirements"))
        constraints = self._mapping_items(prompt_ir.get("constraints"))
        output_sections = self._mapping_items(output_spec.get("sections"))
        validation_rules = self._mapping_items(prompt_ir.get("validationRules"))

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
