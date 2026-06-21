import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from prompt_booster import PatternLibrary

SCHEMA_PATH = ROOT / "schemas" / "prompt-pattern.schema.json"
PATTERN_PATH = ROOT / "patterns" / "core.json"
SCHEMA_VALIDATOR_PATH = ROOT / "tools" / "validate_prompt_ir_examples.py"

EXPECTED_PATTERN_CATEGORIES = {
    "backend",
    "frontend",
    "ai",
    "devops",
    "architecture",
}
EXPECTED_BACKEND_PATTERNS = {
    "backend.spring-rest-api",
    "backend.spring-security",
    "backend.jwt-auth",
    "backend.oauth2-login",
    "backend.batch-processing",
    "backend.scheduler",
}
EXPECTED_FRONTEND_PATTERNS = {
    "frontend.react-spa",
    "frontend.nextjs",
    "frontend.dashboard",
    "frontend.admin-page",
}
EXPECTED_AI_PATTERNS = {
    "ai.rag",
    "ai.agent",
    "ai.chatbot",
    "ai.embedding",
    "ai.vector-database",
}
EXPECTED_DEVOPS_PATTERNS = {
    "devops.docker",
    "devops.kubernetes",
    "devops.github-actions",
    "devops.aws-deployment",
}


def load_schema_validator():
    spec = importlib.util.spec_from_file_location("validate_prompt_ir_examples", SCHEMA_VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    validator = load_schema_validator()
    schema = validator.load_json(SCHEMA_PATH)
    payload = validator.load_json(PATTERN_PATH)

    category_enum = set(schema["$defs"]["PatternCategory"]["enum"])
    require(category_enum == EXPECTED_PATTERN_CATEGORIES, "패턴 스키마 category enum이 범위와 다릅니다.")

    validator.validate_against_schema(schema, payload)
    library = PatternLibrary.from_dict(payload)
    require(library.patterns, "패턴 정의가 비어 있습니다.")
    pattern_ids = {pattern.id for pattern in library.patterns}
    require(EXPECTED_BACKEND_PATTERNS <= pattern_ids, "필수 백엔드 패턴이 누락되었습니다.")
    require(EXPECTED_FRONTEND_PATTERNS <= pattern_ids, "필수 프론트엔드 패턴이 누락되었습니다.")
    require(EXPECTED_AI_PATTERNS <= pattern_ids, "필수 AI 패턴이 누락되었습니다.")
    require(EXPECTED_DEVOPS_PATTERNS <= pattern_ids, "필수 DevOps 패턴이 누락되었습니다.")
    print("Prompt Pattern Library 정의가 유효합니다.")


if __name__ == "__main__":
    main()
