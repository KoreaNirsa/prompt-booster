# Prompt Booster Plugin Package

이 디렉터리는 Prompt-Booster의 Codex Plugin 패키지입니다.

## 구조

```text
plugins/prompt-booster/
  .codex-plugin/plugin.json
  skills/prompt-booster/SKILL.md
  scripts/prompt_booster_command.py
```

## Command Entrypoint

명령 entrypoint는 repo root에서 다음 형식으로 실행합니다.

```bash
python plugins/prompt-booster/scripts/prompt_booster_command.py prompt.optimize --source-text "JWT 로그인 만들어줘" --target codex
```

JSON payload를 직접 전달할 수도 있습니다.

```bash
python plugins/prompt-booster/scripts/prompt_booster_command.py prompt.optimize --input-json "{\"sourceText\":\"JWT 로그인 만들어줘\",\"target\":\"codex\"}"
```

지원 target은 `neutral`, `codex`, `claude_code`입니다.

사용자용 실행 가이드는 [`docs/codex-plugin-usage.md`](../../docs/codex-plugin-usage.md)에 정리되어 있습니다.

## Local Validation

```bash
python <plugin-creator-skill>/scripts/validate_plugin.py plugins/prompt-booster
python -m unittest tests.test_plugin_entrypoint
python -m unittest discover -s tests
```

첫 번째 명령은 local Codex 환경의 plugin manifest validator를 사용합니다. `<plugin-creator-skill>`은 각 개발 환경의 plugin-creator skill 경로로 바꿔 실행합니다.

## Contract

입력과 출력 envelope는 repo의 `docs/codex-plugin-commands.md`와 `tests/fixtures/plugin_command_contract.json`을 기준으로 유지합니다. entrypoint는 core optimizer, quality scorer, pattern library를 호출하며 비즈니스 로직을 중복 구현하지 않습니다.
