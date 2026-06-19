# Prompt IR 도메인 모델

이 문서는 이슈 #2의 Prompt IR 계약을 정의합니다. 현재 저장소에는 애플리케이션 런타임이 없으므로 특정 언어 타입을 먼저 만들지 않고, JSON으로 직렬화 가능한 계약을 기준으로 도메인 모델을 고정합니다.

## 입력과 출력

- 입력: 사용자의 원문 요청과 Analyzer가 확인한 개발 맥락입니다.
- 출력: `PromptRequest` JSON 객체입니다.
- 검증: `schemas/prompt-ir.schema.json` 계약과 `tools/validate_prompt_ir_examples.py` 검증 스크립트를 사용합니다.

## 설계 원칙

- Analyzer 출력은 `PromptRequest` 하나로 고정합니다.
- 에이전트별 렌더러는 `PromptRequest`를 읽기만 하며 Analyzer 출력을 변경하지 않습니다.
- 에이전트 이름, 벤더, 프롬프트 문체 같은 렌더링 전용 정보는 IR에 넣지 않습니다.
- 백엔드, 프론트엔드, AI, DevOps, 아키텍처 요청은 `Intent.primaryDomain`과 `Intent.relatedDomains`로 표현합니다.

## 도메인 타입

| 타입 | 역할 |
| --- | --- |
| `PromptRequest` | 프롬프트 최적화 요청의 최상위 IR입니다. |
| `Intent` | 사용자가 원하는 작업 목적, 주요 도메인, 관련 도메인을 표현합니다. |
| `PromptContext` | 기술 스택, 대상 사용자, 기존 상태, Analyzer 추론 맥락을 표현합니다. |
| `Requirement` | 구현되어야 하는 기능, 보안, 테스트, 문서 요구사항을 표현합니다. |
| `Constraint` | 유지보수성, 보안, 성능, 배포, 아키텍처 제약을 표현합니다. |
| `OutputSpec` | 최종 프롬프트가 요구해야 하는 산출물 형식을 표현합니다. |
| `ValidationRule` | 생성 결과가 스스로 확인해야 하는 검증 규칙을 표현합니다. |
| `PromptQualityScore` | 원문 또는 보강된 프롬프트의 품질 점수를 표현합니다. |

## 예시 payload

- `examples/prompt-ir/jwt-auth.json`: JWT 인증 구현 요청입니다.
- `examples/prompt-ir/board-crud.json`: 게시판 CRUD 구현 요청입니다.
- `examples/prompt-ir/rag-chatbot.json`: RAG 챗봇 구현 요청입니다.

세 예시는 함께 백엔드, 프론트엔드, AI, DevOps, 아키텍처 도메인을 모두 표현합니다.
