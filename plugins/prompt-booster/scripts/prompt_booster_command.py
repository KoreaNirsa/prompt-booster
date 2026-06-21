from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from prompt_booster import (  # noqa: E402
    Category,
    PatternLibrary,
    PromptOptimizer,
    PromptQualityScorer,
    analyze_intent,
)
from prompt_booster.optimizer import SUPPORTED_TARGETS  # noqa: E402


COMMANDS = {"prompt.optimize", "prompt.score", "prompt.explain", "prompt.patterns"}
PATTERN_CATEGORIES = {category.value for category in Category}


def run_command(command: str, payload: object | None = None) -> dict[str, object]:
    if command not in COMMANDS:
        return _failure(command, "invalid_options", "지원하지 않는 명령입니다.", {"command": command})
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        return _failure(command, "invalid_options", "입력 payload는 object여야 합니다.", {"payloadType": type(payload).__name__})

    if command == "prompt.optimize":
        return _run_optimize(command, payload)
    if command == "prompt.score":
        return _run_score(command, payload)
    if command == "prompt.explain":
        return _run_explain(command, payload)
    return _run_patterns(command, payload)


def _run_optimize(command: str, payload: dict[str, object]) -> dict[str, object]:
    source_text_error = _source_text_error(command, payload)
    if source_text_error:
        return source_text_error

    target = payload.get("target", "neutral")
    target_error = _target_error(command, target)
    if target_error:
        return target_error

    include_prompt_ir = payload.get("includePromptIr", False)
    include_quality_score = payload.get("includeQualityScore", True)
    for field, value in (("includePromptIr", include_prompt_ir), ("includeQualityScore", include_quality_score)):
        if not isinstance(value, bool):
            return _failure(command, "invalid_options", f"{field}는 boolean이어야 합니다.", {"field": field})

    result = PromptOptimizer().optimize(str(payload["sourceText"]), str(target))
    if not result.ok:
        return _failure(
            command,
            result.errors[0].code,
            result.errors[0].message,
            {"pipelineSteps": list(result.pipeline_steps)},
        )

    data: dict[str, object] = {
        "renderedPrompt": result.rendered_prompt,
        "promptIrSummary": _prompt_ir_summary(result.prompt_ir),
        "matchedPatterns": [_pattern_match_summary(match) for match in result.pattern_matches],
        "clarificationQuestions": [question.to_dict() for question in result.clarification_questions],
        "qualityScore": None,
        "promptIr": None,
    }
    if include_quality_score:
        data["qualityScore"] = {
            "source": result.source_quality_score.to_dict() if result.source_quality_score else None,
            "optimized": result.optimized_quality_score.to_dict() if result.optimized_quality_score else None,
        }
    if include_prompt_ir:
        data["promptIr"] = result.prompt_ir
    return _success(command, data)


def _run_score(command: str, payload: dict[str, object]) -> dict[str, object]:
    source_text_error = _source_text_error(command, payload)
    if source_text_error:
        return source_text_error

    source_text = str(payload["sourceText"])
    analysis = analyze_intent(source_text)
    score = PromptQualityScorer().score_source_text(source_text, analysis)
    return _success(
        command,
        {
            "analysis": analysis.to_dict(),
            "sourceQualityScore": score.to_dict(),
        },
    )


def _run_explain(command: str, payload: dict[str, object]) -> dict[str, object]:
    source_text_error = _source_text_error(command, payload)
    if source_text_error:
        return source_text_error

    target = payload.get("target", "neutral")
    target_error = _target_error(command, target)
    if target_error:
        return target_error

    result = PromptOptimizer().optimize(str(payload["sourceText"]), str(target))
    analysis = result.analysis
    return _success(
        command,
        {
            "analysis": analysis.to_dict() if analysis else None,
            "matchedSignals": [signal.to_dict() for signal in analysis.matched_signals] if analysis else [],
            "pipelineSteps": list(result.pipeline_steps),
            "matchedPatterns": [_pattern_match_summary(match) for match in result.pattern_matches],
            "clarificationQuestions": [question.to_dict() for question in result.clarification_questions],
        },
    )


def _run_patterns(command: str, payload: dict[str, object]) -> dict[str, object]:
    category = payload.get("category")
    if category is not None and category not in PATTERN_CATEGORIES:
        return _failure(
            command,
            "invalid_options",
            "category는 지원하는 pattern category여야 합니다.",
            {"field": "category", "allowedValues": sorted(PATTERN_CATEGORIES)},
        )

    include_defaults = payload.get("includeDefaults", False)
    if not isinstance(include_defaults, bool):
        return _failure(command, "invalid_options", "includeDefaults는 boolean이어야 합니다.", {"field": "includeDefaults"})

    locale = payload.get("locale")
    if locale is not None and not isinstance(locale, str):
        return _failure(command, "invalid_options", "locale은 string이어야 합니다.", {"field": "locale"})

    patterns = []
    for pattern in PatternLibrary.load_default().patterns:
        if category is not None and pattern.category != category:
            continue
        item = pattern.to_dict()
        if include_defaults:
            item["promptDefaults"] = pattern.to_prompt_defaults(locale).to_dict()
        patterns.append(item)
    return _success(command, {"patterns": patterns})


def _source_text_error(command: str, payload: dict[str, object]) -> dict[str, object] | None:
    source_text = payload.get("sourceText")
    if source_text is None:
        return _failure(command, "empty_input", "sourceText가 비어 있습니다.", {"field": "sourceText"})
    if not isinstance(source_text, str):
        return _failure(command, "invalid_options", "sourceText는 string이어야 합니다.", {"field": "sourceText"})
    if not source_text.strip():
        return _failure(command, "empty_input", "sourceText가 비어 있습니다.", {"field": "sourceText"})
    return None


def _target_error(command: str, target: object) -> dict[str, object] | None:
    if not isinstance(target, str):
        return _failure(command, "invalid_options", "target은 string이어야 합니다.", {"field": "target"})
    if target not in SUPPORTED_TARGETS:
        return _failure(
            command,
            "unsupported_target",
            "지원하지 않는 target입니다.",
            {"field": "target", "allowedValues": sorted(SUPPORTED_TARGETS)},
        )
    return None


def _prompt_ir_summary(prompt_ir: dict[str, object] | None) -> dict[str, object] | None:
    if prompt_ir is None:
        return None
    intent = prompt_ir.get("intent")
    context = prompt_ir.get("context")
    output_spec = prompt_ir.get("outputSpec")
    return {
        "id": prompt_ir.get("id"),
        "intent": intent if isinstance(intent, dict) else None,
        "context": {
            "audience": context.get("audience"),
            "techStack": context.get("techStack"),
        }
        if isinstance(context, dict)
        else None,
        "requirementCount": len(_list_value(prompt_ir.get("requirements"))),
        "constraintCount": len(_list_value(prompt_ir.get("constraints"))),
        "outputSectionCount": len(_list_value(output_spec.get("sections"))) if isinstance(output_spec, dict) else 0,
        "validationRuleCount": len(_list_value(prompt_ir.get("validationRules"))),
    }


def _pattern_match_summary(match: Any) -> dict[str, object]:
    return {
        "id": match.pattern.id,
        "category": match.pattern.category,
        "rank": match.rank,
        "confidence": match.confidence,
    }


def _list_value(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def _success(command: str, data: dict[str, object]) -> dict[str, object]:
    return {
        "ok": True,
        "command": command,
        "data": data,
        "error": None,
    }


def _failure(command: str, code: str, message: str, details: dict[str, object]) -> dict[str, object]:
    return {
        "ok": False,
        "command": command,
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "recoverable": True,
            "details": details,
        },
    }


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Run Prompt-Booster plugin commands.")
    parser.add_argument("command", choices=sorted(COMMANDS))
    parser.add_argument("--input-json", default=None, help="JSON object payload for the command.")
    parser.add_argument("--source-text", default=None, help="sourceText payload convenience option.")
    parser.add_argument("--target", default=None, help="target payload convenience option.")
    parser.add_argument("--include-prompt-ir", action="store_true", help="Include full Prompt IR for prompt.optimize.")
    parser.add_argument("--no-quality-score", action="store_true", help="Exclude quality score for prompt.optimize.")
    parser.add_argument("--category", default=None, help="Pattern category for prompt.patterns.")
    parser.add_argument("--include-defaults", action="store_true", help="Include prompt defaults for prompt.patterns.")
    parser.add_argument("--locale", default=None, help="Pattern locale for prompt.patterns.")
    args = parser.parse_args(argv)

    try:
        payload = _payload_from_args(args)
    except json.JSONDecodeError as exc:
        response = _failure(
            args.command,
            "invalid_options",
            "input-json은 JSON object여야 합니다.",
            {"field": "input-json", "reason": str(exc)},
        )
    else:
        response = run_command(args.command, payload)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    return 0 if response["ok"] else 1


def _payload_from_args(args: argparse.Namespace) -> object:
    if args.input_json is not None:
        return json.loads(args.input_json)

    payload: dict[str, object] = {}
    if args.source_text is not None:
        payload["sourceText"] = args.source_text
    if args.target is not None:
        payload["target"] = args.target
    if args.include_prompt_ir:
        payload["includePromptIr"] = True
    if args.no_quality_score:
        payload["includeQualityScore"] = False
    if args.category is not None:
        payload["category"] = args.category
    if args.include_defaults:
        payload["includeDefaults"] = True
    if args.locale is not None:
        payload["locale"] = args.locale
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
