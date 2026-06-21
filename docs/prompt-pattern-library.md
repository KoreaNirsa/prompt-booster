# Prompt Pattern Library

이 문서는 이슈 #10 범위의 Pattern Library 스키마와 로딩 규칙을 정의합니다.

## 목적

Pattern Library는 반복되는 개발 패턴의 기본 요구사항, 제약조건, 출력 형식, 검증 규칙을 재사용하기 위한 별도 계약입니다. Prompt IR은 기존 계약을 유지하고, 패턴은 Optimizer가 매칭 결과로만 노출합니다.

## 스키마

스키마 파일은 `schemas/prompt-pattern.schema.json`입니다. 패턴 정의는 다음 필드를 포함합니다.

| 필드 | 역할 |
| --- | --- |
| `id` | 패턴을 식별하는 안정적인 값입니다. |
| `category` | `backend`, `frontend`, `ai`, `devops`, `architecture` 중 하나입니다. |
| `keywords` | 원본 입력과 Analyzer 신호에서 패턴을 매칭할 키워드입니다. |
| `defaultRequirements` | 패턴이 제공하는 기본 요구사항 템플릿입니다. |
| `defaultConstraints` | 패턴이 제공하는 기본 제약조건 템플릿입니다. |
| `recommendedOutputFormat` | 패턴에 적합한 출력 형식과 섹션 템플릿입니다. |
| `validationItems` | 패턴 적용 후 확인해야 하는 검증 항목입니다. |
| `matchingMetadata` | 매칭과 랭킹에 사용할 intent hint, domain signal, confidence weight입니다. |
| `locales` | 텍스트 조각을 locale별로 모아 중복 프롬프트 문장을 줄입니다. |
| `renderingHints` | 다국어 처리와 에이전트별 렌더링 확장을 위한 힌트입니다. |

## 텍스트 조각

패턴 템플릿은 문장을 직접 반복하지 않고 `descriptionRef`, `titleRef`, `acceptanceCriteriaRefs`로 `locales`의 텍스트 조각을 참조합니다. 로더는 모든 참조가 `defaultLocale`과 `supportedLocales`에 존재하는지 검증합니다.

## 기본 패턴

현재 기본 파일은 `patterns/core.json`이며, 다음 기본 패턴을 포함합니다.

- `backend.spring-rest-api`
- `backend.spring-security`
- `backend.jwt-auth`
- `backend.oauth2-login`
- `backend.batch-processing`
- `backend.scheduler`
- `frontend.react-spa`
- `frontend.nextjs`
- `frontend.dashboard`
- `frontend.admin-page`
- `ai.rag`
- `ai.agent`
- `ai.chatbot`
- `ai.embedding`
- `ai.vector-database`
- `devops.docker`
- `devops.kubernetes`
- `devops.github-actions`
- `devops.aws-deployment`

각 패턴은 keywords와 matching metadata를 함께 제공하며, requirements, constraints, output format, validation items를 locale 텍스트 조각으로 해석합니다.

## Optimizer 연동

Optimizer는 기본 패턴 파일을 로드하고 `patternMatches`에 매칭 결과를 노출합니다. 이번 범위에서는 Prompt IR에 패턴 기본값을 주입하지 않습니다. 후속 작업에서 `PatternPromptDefaults`를 사용해 요구사항, 제약조건, 출력 형식, 검증 규칙을 안전하게 병합할 수 있습니다.
