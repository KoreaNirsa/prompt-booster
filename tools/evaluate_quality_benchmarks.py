from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from prompt_booster import optimize_prompt  # noqa: E402


BENCHMARK_PATH = ROOT / "benchmarks" / "prompt-quality-benchmarks.json"


def load_json(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def evaluate_benchmarks(payload: dict[str, object]) -> dict[str, object]:
    evaluation = payload.get("evaluation")
    target = evaluation.get("target", "neutral") if isinstance(evaluation, dict) else "neutral"
    cases = payload.get("cases", [])
    results = [evaluate_case(case, str(target)) for case in cases if isinstance(case, dict)]
    return {
        "benchmarkCount": len(results),
        "passed": all(result["passed"] for result in results),
        "results": results,
    }


def evaluate_case(case: dict[str, object], target: str) -> dict[str, object]:
    errors: list[str] = []
    result = optimize_prompt(str(case.get("sourceText", "")), target=target)
    if not result.ok:
        return {
            "id": case.get("id"),
            "passed": False,
            "errors": [error.message for error in result.errors],
        }

    expected_intent = str(case.get("expectedIntent"))
    expected_category = str(case.get("expectedCategory"))
    if result.analysis.intent.value != expected_intent:
        errors.append(f"intent expected={expected_intent} actual={result.analysis.intent.value}")
    if result.analysis.category.value != expected_category:
        errors.append(f"category expected={expected_category} actual={result.analysis.category.value}")

    sections = {
        str(section.get("title"))
        for section in result.prompt_ir["outputSpec"]["sections"]
        if isinstance(section, dict)
    }
    minimum_sections = {str(section) for section in case.get("minimumSections", [])}
    missing_sections = sorted(minimum_sections - sections)
    if missing_sections:
        errors.append(f"minimumSections missing={missing_sections}")

    expectations = case.get("qualityExpectations")
    if isinstance(expectations, dict):
        source_total = result.source_quality_score.total
        optimized_total = result.optimized_quality_score.total
        improvement = optimized_total - source_total
        source_max = int(expectations.get("sourceMax", 100))
        optimized_min = int(expectations.get("optimizedMin", 0))
        improvement_min = int(expectations.get("improvementMin", 0))
        if source_total > source_max:
            errors.append(f"sourceQualityScore expected<={source_max} actual={source_total}")
        if optimized_total < optimized_min:
            errors.append(f"optimizedQualityScore expected>={optimized_min} actual={optimized_total}")
        if improvement < improvement_min:
            errors.append(f"qualityScoreImprovement expected>={improvement_min} actual={improvement}")
    else:
        source_total = None
        optimized_total = None
        improvement = None
        errors.append("qualityExpectations가 없습니다.")

    return {
        "id": case.get("id"),
        "passed": not errors,
        "sourceQualityScore": source_total,
        "optimizedQualityScore": optimized_total,
        "improvement": improvement,
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    path = Path(argv[0]) if argv else BENCHMARK_PATH
    summary = evaluate_benchmarks(load_json(path))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
