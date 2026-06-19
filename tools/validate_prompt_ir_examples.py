import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "prompt-ir.schema.json"
EXAMPLE_DIR = ROOT / "examples" / "prompt-ir"

EXPECTED_DEFS = {
    "PromptRequest",
    "Intent",
    "PromptContext",
    "Requirement",
    "Constraint",
    "OutputSpec",
    "ValidationRule",
    "PromptQualityScore",
}

EXPECTED_EXAMPLES = {
    "jwt-auth.json",
    "board-crud.json",
    "rag-chatbot.json",
}

EXPECTED_DOMAINS = {
    "backend",
    "frontend",
    "ai",
    "devops",
    "architecture",
}

EXPECTED_SCORE_CRITERIA = {
    "role",
    "requirement",
    "constraint",
    "context",
    "outputFormat",
    "validation",
    "technicalSpecificity",
}

TOP_LEVEL_FIELDS = {
    "schemaVersion",
    "id",
    "sourceText",
    "intent",
    "context",
    "requirements",
    "constraints",
    "outputSpec",
    "validationRules",
    "qualityScore",
}


def load_json(path):
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def validate_schema(schema):
    defs = set(schema.get("$defs", {}))
    required = set(schema.get("required", []))
    schema_defs = defs | {"PromptRequest"}

    require(EXPECTED_DEFS <= schema_defs, "필수 도메인 타입 정의가 누락되었습니다.")
    require(TOP_LEVEL_FIELDS <= required, "PromptRequest 필수 필드가 누락되었습니다.")

    domains = set(schema["$defs"]["Domain"]["enum"])
    require(EXPECTED_DOMAINS == domains, "지원 도메인 목록이 이슈 범위와 다릅니다.")


def validate_example(path, payload):
    missing = TOP_LEVEL_FIELDS - set(payload)
    require(not missing, f"{path.name}: 최상위 필드가 누락되었습니다: {sorted(missing)}")
    require(payload["schemaVersion"] == "1.0.0", f"{path.name}: schemaVersion이 다릅니다.")
    require(payload["id"], f"{path.name}: id가 비어 있습니다.")
    require(payload["sourceText"], f"{path.name}: sourceText가 비어 있습니다.")

    intent = payload["intent"]
    require(intent["primaryDomain"] in EXPECTED_DOMAINS, f"{path.name}: primaryDomain이 유효하지 않습니다.")
    require(set(intent["relatedDomains"]) <= EXPECTED_DOMAINS, f"{path.name}: relatedDomains가 유효하지 않습니다.")

    require(payload["requirements"], f"{path.name}: requirements가 비어 있습니다.")
    require(payload["outputSpec"]["sections"], f"{path.name}: outputSpec.sections가 비어 있습니다.")
    require(payload["validationRules"], f"{path.name}: validationRules가 비어 있습니다.")

    score = payload["qualityScore"]
    require(0 <= score["total"] <= score["max"] == 100, f"{path.name}: qualityScore 범위가 유효하지 않습니다.")
    criteria_names = {criterion["name"] for criterion in score["criteria"]}
    require(EXPECTED_SCORE_CRITERIA == criteria_names, f"{path.name}: 품질 점수 기준이 누락되었습니다.")

    return {intent["primaryDomain"], *intent["relatedDomains"]}


def main():
    schema = load_json(SCHEMA_PATH)
    validate_schema(schema)

    examples = {path.name: path for path in EXAMPLE_DIR.glob("*.json")}
    require(EXPECTED_EXAMPLES <= set(examples), "필수 예시 payload가 누락되었습니다.")

    represented_domains = set()
    for name in sorted(EXPECTED_EXAMPLES):
        represented_domains |= validate_example(examples[name], load_json(examples[name]))

    require(EXPECTED_DOMAINS <= represented_domains, "예시 payload가 모든 요구 도메인을 표현하지 못합니다.")
    print("Prompt IR 예시가 유효합니다.")


if __name__ == "__main__":
    main()
