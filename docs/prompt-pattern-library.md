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

## Category

Pattern category는 analyzer가 감지한 domain과 optimizer의 기본 보강 방향을 맞추기 위한 값입니다.

| category | 사용 기준 |
| --- | --- |
| `backend` | API, 인증, 배치, 스케줄러처럼 서버 구현 단위가 중심인 요청입니다. |
| `frontend` | React, Next.js, dashboard, admin page처럼 화면과 상호작용 구현이 중심인 요청입니다. |
| `ai` | RAG, agent, chatbot, embedding, vector database처럼 AI 기능 구현이 중심인 요청입니다. |
| `devops` | Docker, Kubernetes, GitHub Actions, AWS 배포처럼 운영과 배포 흐름이 중심인 요청입니다. |
| `architecture` | Clean Architecture, Hexagonal Architecture, DDD, MSA처럼 설계 경계와 tradeoff가 중심인 요청입니다. |

새 category는 schema, analyzer category, renderer 기대값이 함께 바뀌므로 별도 이슈에서 다룹니다.

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
- `architecture.clean`
- `architecture.hexagonal`
- `architecture.ddd`
- `architecture.msa`

각 패턴은 keywords와 matching metadata를 함께 제공하며, requirements, constraints, output format, validation items를 locale 텍스트 조각으로 해석합니다.

## 패턴 추가 방법

패턴은 `patterns/core.json`의 `patterns` 배열에 추가합니다. 새 패턴은 schema와 loader 검증을 통과해야 하며, Prompt IR 계약을 직접 바꾸지 않습니다.

1. `id`는 `category.name` 형식의 안정적인 값으로 정합니다.
2. `category`는 기존 enum인 `backend`, `frontend`, `ai`, `devops`, `architecture` 중 하나를 사용합니다.
3. `keywords`에는 사용자 원문과 analyzer 신호에서 실제로 매칭할 단어를 넣습니다.
4. `locales`에는 `defaultRequirements`, `defaultConstraints`, `recommendedOutputFormat`, `validationItems`가 참조할 텍스트 조각을 모두 정의합니다.
5. `defaultRequirements`에는 요구사항 설명과 acceptance criteria 참조를 넣습니다.
6. `defaultConstraints`에는 보안, 유지보수성, 테스트, 배포 같은 제약 범위를 넣습니다.
7. `recommendedOutputFormat.sections`에는 최종 프롬프트에 필요한 출력 섹션을 정의합니다.
8. `matchingMetadata`에는 intent hint, domain signal, confidence weight를 정의합니다.
9. `renderingHints.agentProfiles`에는 해당 패턴을 사용할 수 있는 agent profile을 명시합니다.

패턴을 추가한 뒤에는 다음 명령으로 검증합니다.

```bash
python tools/validate_prompt_patterns.py
python -m unittest tests.test_pattern_library tests.test_optimizer
```

패턴 추가가 benchmark 품질에 영향을 주는 경우 다음 명령도 함께 실행합니다.

```bash
python tools/evaluate_quality_benchmarks.py
```

## Optimizer 연동

Optimizer는 기본 패턴 파일을 로드하고 `patternMatches`에 매칭 결과를 노출합니다. 매칭은 원본 입력과 Analyzer 신호에서 확인한 keywords, intent hint, category, domain signal, confidence weight를 함께 사용해 점수화합니다. 결과는 `rank`, `confidence`, `score`를 포함해 같은 요청에서 여러 패턴이 예측 가능한 순서로 적용될 수 있게 합니다.

매칭된 패턴의 `PatternPromptDefaults`는 Prompt IR의 requirements, constraints, outputSpec, validationRules에 병합됩니다. 병합 시 같은 description, scope, acceptance criteria, output section 조합은 한 번만 유지하며, 출력 형식 추천이 서로 다르면 가장 높은 rank의 패턴 추천값을 사용하고 충돌 내역을 context assumptions에 남깁니다.

## 유지보수 기준

- 패턴은 비즈니스 로직을 추측하지 않고 일반 개발 패턴 수준의 요구사항만 제공합니다.
- 사용자 답변이 필요한 도메인 정책은 `validationItems`나 clarification question으로 남깁니다.
- 기존 pattern id는 snapshot, fixture, 외부 contract에서 참조될 수 있으므로 이름 변경 대신 새 패턴 추가를 우선합니다.
