# Codex Plugin Command Contract

이 문서는 이슈 #18 범위의 Codex Plugin 명령 인터페이스를 정의합니다. 실제 plugin manifest와 entrypoint 패키징은 별도 이슈에서 다루며, 이 문서는 Prompt-Booster가 외부 명령으로 노출할 안정적인 계약만 고정합니다.

## 공통 응답 형태

모든 명령은 같은 envelope를 사용합니다.

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `ok` | boolean | 명령 처리 성공 여부입니다. |
| `command` | string | 실행된 명령 이름입니다. |
| `data` | object 또는 null | 성공 시 명령별 출력 payload입니다. |
| `error` | object 또는 null | 실패 시 오류 payload입니다. |

오류 payload는 다음 필드를 포함합니다.

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `code` | string | `empty_input`, `invalid_options`, `unsupported_target` 중 하나입니다. |
| `message` | string | 사용자에게 보여줄 수 있는 오류 설명입니다. |
| `recoverable` | boolean | 입력을 고치면 재시도 가능한 오류인지 나타냅니다. |
| `details` | object | 잘못된 필드, 허용 값, 원인 같은 구조화된 세부 정보입니다. |

## 명령 목록

### `prompt.optimize`

사용자 원문을 분석하고 최적화된 프롬프트를 생성합니다.

입력 필드:

| 필드 | 필수 | 타입 | 설명 |
| --- | --- | --- | --- |
| `sourceText` | 예 | string | 최적화할 사용자 원문 요청입니다. |
| `target` | 아니오 | string | `neutral`, `codex`, `claude_code` 중 하나입니다. 생략 시 `neutral`을 사용합니다. |
| `includePromptIr` | 아니오 | boolean | 전체 Prompt IR을 응답에 포함할지 결정합니다. 기본값은 `false`입니다. |
| `includeQualityScore` | 아니오 | boolean | quality score 상세 정보를 포함할지 결정합니다. 기본값은 `true`입니다. |

출력 필드:

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `renderedPrompt` | string 또는 null | 최종 렌더링 프롬프트입니다. |
| `promptIrSummary` | object 또는 null | intent, context, requirement count, output section count를 요약한 값입니다. |
| `matchedPatterns` | array | 매칭된 pattern id, category, rank, confidence 목록입니다. |
| `clarificationQuestions` | array | 실행 전 사용자 답변이 필요한 질문 목록입니다. |
| `qualityScore` | object 또는 null | 사용할 수 있는 경우 source 및 optimized quality score입니다. |
| `promptIr` | object 또는 null | `includePromptIr=true`일 때만 포함되는 전체 Prompt IR입니다. |

### `prompt.score`

원문 요청의 품질 점수와 진단 정보를 반환합니다.

입력 필드:

| 필드 | 필수 | 타입 | 설명 |
| --- | --- | --- | --- |
| `sourceText` | 예 | string | 점수화할 사용자 원문 요청입니다. |

출력 필드:

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `analysis` | object | intent, category, matched signals, confidence입니다. |
| `sourceQualityScore` | object | 원문 요청의 점수, 항목별 breakdown, diagnostics입니다. |

### `prompt.executionPlan`

최적화된 프롬프트를 사용자에게 최종 응답으로 보여줄지, 대상 에이전트의 내부 실행 입력으로 전달할지 결정합니다. 이 명령은 외부 에이전트를 직접 실행하지 않고 자동 실행을 시작하기 위한 구조화된 입력만 생성합니다.

입력 필드:

| 필드 | 필수 | 타입 | 설명 |
| --- | --- | --- | --- |
| `sourceText` | 예 | string | 실행 계획을 만들 사용자 원문 요청입니다. |
| `target` | 아니오 | string | `neutral`, `codex`, `claude_code` 중 하나입니다. 생략 시 `codex`를 사용합니다. |
| `executionMode` | 아니오 | string | `render_only`, `auto_execute` 중 하나입니다. 생략 시 `render_only`를 사용합니다. |
| `clarificationAnswers` | 아니오 | object | 질문 `id` 또는 `topic`을 key로 하는 사용자 답변입니다. |

출력 필드:

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `executionPlan` | object | 실행 모드, 실행 가능 여부, 사용자 출력 프롬프트, 내부 실행 입력, 필수 질문, 차단 사유입니다. |

`executionPlan`은 다음 상태를 사용합니다.

| status | 의미 |
| --- | --- |
| `render_only` | 최적화된 프롬프트를 사용자에게 반환하는 모드입니다. `executionInput`은 없습니다. |
| `blocked` | 자동 실행 전에 필수 질문 답변이나 입력 수정이 필요합니다. |
| `ready` | 필수 답변이 충족되어 `executionInput`을 대상 에이전트로 전달할 수 있습니다. |

`auto_execute` 모드에서 비즈니스 로직 또는 고영향 요구사항 답변이 없으면 `executionReady=false`, `executionInput=null`, `requiredQuestions`와 `blockedReasons`를 반환합니다.

### `prompt.explain`

Analyzer와 Optimizer가 어떤 근거로 결과를 만들었는지 설명합니다.

입력 필드:

| 필드 | 필수 | 타입 | 설명 |
| --- | --- | --- | --- |
| `sourceText` | 예 | string | 설명할 사용자 원문 요청입니다. |
| `target` | 아니오 | string | `neutral`, `codex`, `claude_code` 중 하나입니다. 생략 시 `neutral`을 사용합니다. |

출력 필드:

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `analysis` | object | intent, category, confidence, fallback 정보입니다. |
| `matchedSignals` | array | Analyzer가 감지한 신호 목록입니다. |
| `pipelineSteps` | array | 실행된 optimizer pipeline step 목록입니다. |
| `matchedPatterns` | array | 매칭된 pattern id와 ranking 정보입니다. |
| `clarificationQuestions` | array | 추가 질문이 필요한 경우의 질문 목록입니다. |

### `prompt.patterns`

사용 가능한 Pattern Library 항목을 조회합니다.

입력 필드:

| 필드 | 필수 | 타입 | 설명 |
| --- | --- | --- | --- |
| `category` | 아니오 | string | `backend`, `frontend`, `ai`, `devops`, `architecture` 중 하나로 필터링합니다. |
| `includeDefaults` | 아니오 | boolean | pattern prompt defaults를 포함할지 결정합니다. 기본값은 `false`입니다. |
| `locale` | 아니오 | string | defaults를 해석할 locale입니다. 생략 시 pattern 기본 locale을 사용합니다. |

출력 필드:

| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `patterns` | array | pattern id, category, keywords, matching metadata, supported locales, agent profiles 목록입니다. |

## 오류 응답

| code | 발생 조건 | recoverable |
| --- | --- | --- |
| `empty_input` | `sourceText`가 없거나 공백뿐인 경우입니다. | true |
| `invalid_options` | 입력 payload가 object가 아니거나 필드 타입, category, include 옵션이 계약과 다른 경우입니다. | true |
| `unsupported_target` | `target`이 지원 값인 `neutral`, `codex`, `claude_code`가 아닌 경우입니다. | true |

`prompt.patterns`는 `sourceText`를 받지 않으므로 `empty_input`을 반환하지 않습니다. 잘못된 category 또는 include 옵션은 `invalid_options`로 반환합니다.
