# Agent Execution Flow

이 문서는 최적화된 프롬프트를 사용자에게 보여주는 흐름과 대상 에이전트의 내부 실행 입력으로 전달하는 흐름을 구분합니다.

## 실행 모드

| mode | 목적 | 출력 |
| --- | --- | --- |
| `render_only` | 최적화된 프롬프트를 사용자에게 최종 응답으로 노출합니다. | `renderedPrompt` |
| `auto_execute` | 최적화된 프롬프트를 대상 에이전트 실행 계층에 전달할 내부 입력으로 준비합니다. | `executionInput` 또는 `requiredQuestions` |

`auto_execute` 모드는 외부 에이전트를 직접 호출하지 않습니다. 이 모드는 자동 실행 가능 여부를 검증하고, 실행 가능한 경우 다음 계층이 사용할 입력 계약을 반환합니다.

## 자동 실행 전 검증

자동 실행 전에는 다음 조건을 확인합니다.

- 원문 입력과 target이 plugin command contract를 통과해야 합니다.
- optimizer가 Prompt IR과 target별 prompt를 생성할 수 있어야 합니다.
- 비즈니스 로직이나 고영향 요구사항을 추측해야 하는 경우 자동 실행을 차단해야 합니다.
- 질문은 실행 결과를 크게 바꾸는 항목으로 제한하며 최대 3개만 반환합니다.
- 각 질문은 사용자가 빠르게 답할 수 있도록 예시 답변을 포함해야 합니다.

## 차단 조건

필수 질문 답변이 없으면 `status=blocked`를 반환합니다.

```json
{
  "status": "blocked",
  "executionReady": false,
  "executionInput": null,
  "requiredQuestions": [
    {
      "id": "Q-BUSINESS-SCOPE",
      "topic": "business_scope",
      "question": "자동 실행 전에 쇼핑몰의 핵심 비즈니스 범위를 어디까지로 제한해야 하나요?",
      "examples": [
        "상품 조회와 장바구니까지만 포함",
        "주문 생성까지 포함하고 결제는 제외"
      ],
      "required": true
    }
  ]
}
```

이 상태에서는 대상 에이전트로 prompt를 전달하지 않습니다.

## 준비 완료 조건

필수 질문이 모두 답변되면 `status=ready`를 반환합니다.

```json
{
  "status": "ready",
  "executionReady": true,
  "renderedPrompt": null,
  "executionInput": {
    "target": "codex",
    "prompt": "# Codex Task Prompt\n...",
    "sourceText": "쇼핑몰 만들어줘",
    "clarificationAnswers": [
      {
        "id": "Q-BUSINESS-SCOPE",
        "topic": "business_scope",
        "answer": "주문 생성까지 포함하고 결제는 제외"
      }
    ],
    "executionPolicy": {
      "businessLogicGuessing": "forbidden",
      "requiresAllRequiredClarifications": true
    }
  }
}
```

`executionInput.prompt`는 사용자에게 최종 응답으로 노출하기 위한 값이 아니라 대상 에이전트 실행 계층으로 전달할 내부 입력입니다.
필수 질문 답변이 있으면 prompt 하단에 `Clarification Answers` 섹션을 포함해 에이전트가 비즈니스 범위를 추측하지 않도록 합니다.

## 관련 명령

```bash
python plugins/prompt-booster/scripts/prompt_booster_command.py prompt.executionPlan --source-text "쇼핑몰 만들어줘" --target codex --execution-mode auto_execute
```

필수 답변을 제공할 때는 질문 `id` 또는 `topic`을 key로 전달합니다.

```bash
python plugins/prompt-booster/scripts/prompt_booster_command.py prompt.executionPlan --source-text "쇼핑몰 만들어줘" --target codex --execution-mode auto_execute --clarification-answer "business_scope=주문 생성까지 포함하고 결제는 제외"
```
