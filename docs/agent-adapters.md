# Agent Adapter

Prompt-Booster는 analyzer, pattern matcher, Prompt IR 생성을 agent와 분리합니다. Agent별 차이는 `AgentAdapterRegistry` 뒤에 있는 adapter가 최종 렌더링 단계에서만 처리합니다.

## 지원 target

| target | adapter | 출력 방식 |
| --- | --- | --- |
| `neutral` | `RendererAgentAdapter` | agent 중립 `PromptRenderer` 출력입니다. |
| `codex` | `RendererAgentAdapter` | 코딩 에이전트가 실행하기 쉬운 Codex 작업 프롬프트입니다. |
| `claude_code` | `RendererAgentAdapter` | Codex와 같은 코딩 에이전트 섹션 구조를 사용하되 제목만 Claude Code 대상으로 표시합니다. |

`claude_code`는 현재 별도 비즈니스 규칙이나 실행 계약이 정의되어 있지 않으므로 Codex와 동일한 task objective, implementation scope, constraints, expected output, verification steps, operational risk notes 구조를 사용합니다. 향후 Claude Code 전용 요구가 명시되면 adapter 또는 renderer만 교체하고 core analyzer와 pattern matcher는 변경하지 않습니다.

## 확장 예정 target

다음 target은 확장 지점으로 예약합니다.

- `cursor`
- `windsurf`
- `gemini_cli`
- `openhands`

새 agent를 추가할 때는 `PromptAgentAdapter`를 구현하고 `AgentAdapterRegistry`에 등록합니다. adapter는 공유 Prompt IR을 입력으로 받아 target별 prompt만 반환해야 하며, intent 분석, pattern matching, constraint 주입 규칙을 변경하지 않습니다.

## 오류 처리

지원하지 않는 target은 `unsupported_target` 오류로 반환합니다. 오류 메시지는 요청 target과 현재 지원 target 목록을 포함해야 합니다.
