import copy
import json
import re
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


def format_json_path(path):
    if not path:
        return "$"

    formatted = "$"
    for part in path:
        if isinstance(part, int):
            formatted += f"[{part}]"
        else:
            formatted += f".{part}"
    return formatted


def resolve_ref(root_schema, ref):
    require(ref.startswith("#/"), f"지원하지 않는 $ref 형식입니다: {ref}")

    current = root_schema
    for raw_part in ref[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        current = current[part]
    return current


def validate_type(expected_type, value, path):
    validators = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
    }
    validator = validators.get(expected_type)
    require(validator is not None, f"{format_json_path(path)}: 지원하지 않는 type입니다: {expected_type}")
    require(validator(value), f"{format_json_path(path)}: {expected_type} 타입이어야 합니다.")


def validate_against_schema(schema, value, root_schema=None, path=None):
    root_schema = root_schema or schema
    path = path or []

    if "$ref" in schema:
        validate_against_schema(resolve_ref(root_schema, schema["$ref"]), value, root_schema, path)
        return

    if "type" in schema:
        validate_type(schema["type"], value, path)

    if "const" in schema:
        require(value == schema["const"], f"{format_json_path(path)}: const 값과 다릅니다.")

    if "enum" in schema:
        require(value in schema["enum"], f"{format_json_path(path)}: enum에 없는 값입니다.")

    if isinstance(value, str):
        if "minLength" in schema:
            require(len(value) >= schema["minLength"], f"{format_json_path(path)}: 문자열이 너무 짧습니다.")
        if "pattern" in schema:
            require(re.match(schema["pattern"], value), f"{format_json_path(path)}: pattern과 일치하지 않습니다.")

    if isinstance(value, int) and not isinstance(value, bool):
        if "minimum" in schema:
            require(value >= schema["minimum"], f"{format_json_path(path)}: minimum보다 작습니다.")
        if "maximum" in schema:
            require(value <= schema["maximum"], f"{format_json_path(path)}: maximum보다 큽니다.")

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        missing = set(required) - set(value)
        require(not missing, f"{format_json_path(path)}: 필수 필드가 누락되었습니다: {sorted(missing)}")

        if schema.get("additionalProperties") is False:
            unexpected = set(value) - set(properties)
            require(not unexpected, f"{format_json_path(path)}: 허용되지 않은 필드입니다: {sorted(unexpected)}")

        for key, property_schema in properties.items():
            if key in value:
                validate_against_schema(property_schema, value[key], root_schema, [*path, key])

    if isinstance(value, list):
        if "minItems" in schema:
            require(len(value) >= schema["minItems"], f"{format_json_path(path)}: 항목 수가 부족합니다.")
        if schema.get("uniqueItems"):
            serialized_items = [json.dumps(item, sort_keys=True, ensure_ascii=False) for item in value]
            require(len(serialized_items) == len(set(serialized_items)), f"{format_json_path(path)}: 중복 항목이 있습니다.")
        if "items" in schema:
            for index, item in enumerate(value):
                validate_against_schema(schema["items"], item, root_schema, [*path, index])


def validate_json_schema_contract(path, payload, schema):
    try:
        validate_against_schema(schema, payload)
    except AssertionError as error:
        raise AssertionError(f"{path.name}: JSON Schema 검증 실패: {error}") from error


def require_schema_failure(schema, payload, case_name):
    try:
        validate_against_schema(schema, payload)
    except AssertionError:
        return
    raise AssertionError(f"{case_name}: JSON Schema 위반 payload가 통과했습니다.")


def validate_negative_cases(schema, payload):
    invalid_action = copy.deepcopy(payload)
    invalid_action["intent"]["action"] = "invalid-action"
    require_schema_failure(schema, invalid_action, "intent.action enum 밖 값")

    unexpected_field = copy.deepcopy(payload)
    unexpected_field["unexpected"] = True
    require_schema_failure(schema, unexpected_field, "top-level 추가 필드")


def validate_schema(schema):
    defs = set(schema.get("$defs", {}))
    required = set(schema.get("required", []))
    schema_defs = defs | {"PromptRequest"}

    require(EXPECTED_DEFS <= schema_defs, "필수 도메인 타입 정의가 누락되었습니다.")
    require(TOP_LEVEL_FIELDS <= required, "PromptRequest 필수 필드가 누락되었습니다.")

    domains = set(schema["$defs"]["Domain"]["enum"])
    require(EXPECTED_DOMAINS == domains, "지원 도메인 목록이 이슈 범위와 다릅니다.")


def validate_example(path, payload, schema):
    validate_json_schema_contract(path, payload, schema)

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
        payload = load_json(examples[name])
        represented_domains |= validate_example(examples[name], payload, schema)

    require(EXPECTED_DOMAINS <= represented_domains, "예시 payload가 모든 요구 도메인을 표현하지 못합니다.")
    validate_negative_cases(schema, load_json(examples["jwt-auth.json"]))
    print("Prompt IR 예시가 유효합니다.")


if __name__ == "__main__":
    main()
