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

## 자동 실행 준비 계약

자동 실행 흐름은 adapter가 외부 에이전트를 직접 호출하는 방식이 아니라, `prompt.executionPlan`이 만든 `executionInput`을 대상 에이전트 실행 계층에 전달하는 방식으로 정의합니다.

| 필드 | 설명 |
| --- | --- |
| `target` | 실행 입력을 받을 agent target입니다. |
| `prompt` | target별 renderer가 만든 내부 실행 프롬프트입니다. 필수 질문 답변이 있으면 `Clarification Answers` 섹션을 함께 포함합니다. |
| `sourceText` | 사용자의 원문 요청입니다. |
| `promptIrSummary` | intent, context, requirement count, output section count 요약입니다. |
| `matchedPatterns` | 실행 입력 생성에 반영된 pattern match 요약입니다. |
| `clarificationAnswers` | 자동 실행 전에 사용자가 답한 필수 질문입니다. |
| `executionPolicy` | 비즈니스 로직 추측 금지와 필수 질문 충족 조건입니다. |

`executionPolicy.businessLogicGuessing`은 항상 `forbidden`입니다. 필수 질문이 남아 있으면 `executionInput`을 만들지 않고 `blocked` 상태를 반환해야 합니다.
