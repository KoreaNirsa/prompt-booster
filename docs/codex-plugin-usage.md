# Codex Plugin 사용 가이드

이 문서는 패키징된 Codex Plugin을 로컬에서 실행하고 검증하는 방법을 설명합니다. 명령별 입출력 계약은 [`codex-plugin-commands.md`](codex-plugin-commands.md)를 기준으로 합니다.

## 패키지 위치

```text
plugins/prompt-booster/
  .codex-plugin/plugin.json
  skills/prompt-booster/SKILL.md
  scripts/prompt_booster_command.py
```

`prompt_booster_command.py`는 저장소 루트에서 실행해야 합니다. entrypoint는 core optimizer, quality scorer, pattern library를 호출하며 별도 비즈니스 로직을 중복 구현하지 않습니다.

## 기본 실행

```bash
python plugins/prompt-booster/scripts/prompt_booster_command.py prompt.optimize --source-text "JWT 로그인 만들어줘" --target codex
```

지원 target은 `neutral`, `codex`, `claude_code`입니다. `target`을 생략하면 `neutral`을 사용합니다.

## JSON payload 실행

복잡한 옵션은 JSON payload로 전달할 수 있습니다.

```bash
python plugins/prompt-booster/scripts/prompt_booster_command.py prompt.optimize --input-json "{\"sourceText\":\"게시판 설계해줘\",\"target\":\"codex\",\"includePromptIr\":true}"
```

PowerShell에서는 따옴표 이스케이프가 환경에 따라 달라질 수 있으므로, 문제가 생기면 `--source-text`, `--target`, `--include-prompt-ir` 옵션을 우선 사용합니다.

## 명령 목록

| 명령 | 필수 입력 | 주요 출력 |
| --- | --- | --- |
| `prompt.optimize` | `sourceText` | `renderedPrompt`, `promptIrSummary`, `matchedPatterns`, `clarificationQuestions`, `qualityScore` |
| `prompt.score` | `sourceText` | `analysis`, `sourceQualityScore` |
| `prompt.explain` | `sourceText` | `analysis`, `matchedSignals`, `pipelineSteps`, `matchedPatterns`, `clarificationQuestions` |
| `prompt.patterns` | 없음 | `patterns` |

## Pattern 조회

```bash
python plugins/prompt-booster/scripts/prompt_booster_command.py prompt.patterns --category backend
```

패턴 기본 요구사항과 제약조건까지 확인하려면 `--include-defaults`를 함께 사용합니다.

```bash
python plugins/prompt-booster/scripts/prompt_booster_command.py prompt.patterns --category backend --include-defaults
```

## 오류 응답

모든 명령은 같은 envelope를 반환합니다.

```json
{
  "ok": false,
  "command": "prompt.optimize",
  "data": null,
  "error": {
    "code": "unsupported_target",
    "message": "지원하지 않는 target입니다.",
    "recoverable": true,
    "details": {
      "field": "target",
      "allowedValues": [
        "claude_code",
        "codex",
        "neutral"
      ]
    }
  }
}
```

오류 코드는 `empty_input`, `invalid_options`, `unsupported_target` 중 하나입니다. 입력을 수정하면 재시도할 수 있는 오류는 `recoverable: true`로 표시합니다.

## 로컬 검증

```bash
python -m unittest tests.test_plugin_entrypoint
python -m unittest tests.test_plugin_command_contract
python -m unittest discover -s tests
python -m json.tool plugins/prompt-booster/.codex-plugin/plugin.json > /dev/null
```

Windows PowerShell에서는 마지막 명령을 다음처럼 실행합니다.

```powershell
python -m json.tool plugins\prompt-booster\.codex-plugin\plugin.json > $null
```

## 관련 문서

- [`codex-plugin-commands.md`](codex-plugin-commands.md)
- [`agent-adapters.md`](agent-adapters.md)
- [`prompt-pattern-library.md`](prompt-pattern-library.md)
- [`prompt-quality-score.md`](prompt-quality-score.md)
