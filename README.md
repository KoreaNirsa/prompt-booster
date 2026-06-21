# 🚀 Prompt-Booster

> 모호한 요청을 실무 수준의 프롬프트로 변환합니다.
>
> **Developer-Focused Prompt Optimization Platform**

Prompt-Booster는 개발자의 짧고 모호한 요청을 AI 코딩 에이전트가 이해하기 쉬운 고품질 프롬프트로 변환하는 오픈소스 프로젝트입니다.

단순히 프롬프트를 길게 만드는 것이 아니라, Prompt Engineering 기법을 적용하여 AI가 더 정확하고 일관된 결과를 생성할 수 있도록 돕습니다.

---

# 🚦 빠른 시작

## 요구 환경

* Python 3.10 이상
* Git

현재 저장소는 별도 패키징 파일 없이 표준 라이브러리 기반 로컬 실행을 기준으로 합니다.

## 저장소 준비

```bash
git clone https://github.com/KoreaNirsa/prompt-booster.git
cd prompt-booster
python -m unittest discover -s tests
```

## 기본 사용법

Codex Plugin entrypoint를 직접 실행해 최적화 결과를 확인할 수 있습니다.

```bash
python plugins/prompt-booster/scripts/prompt_booster_command.py prompt.optimize --source-text "JWT 로그인 만들어줘" --target codex
```

지원 명령은 다음과 같습니다.

| 명령 | 목적 |
| --- | --- |
| `prompt.optimize` | 원문 요청을 분석하고 target별 최적화 프롬프트를 반환합니다. |
| `prompt.score` | 원문 요청의 Prompt Quality Score와 진단 정보를 반환합니다. |
| `prompt.explain` | analyzer, pattern, clarification 흐름을 설명합니다. |
| `prompt.patterns` | 사용 가능한 Pattern Library 항목을 조회합니다. |

라이브러리 코드에서는 `optimize_prompt`를 직접 호출할 수 있습니다.

```python
from prompt_booster import optimize_prompt

result = optimize_prompt("게시판 설계해줘", target="neutral")
print(result.rendered_prompt)
```

Codex Plugin 사용 가이드는 [`docs/codex-plugin-usage.md`](docs/codex-plugin-usage.md)에 정리되어 있습니다.

---

# 🤔 왜 Prompt-Booster가 필요한가?

많은 개발자들이 다음과 같이 요청합니다.

```text
JWT 로그인 만들어줘
```

```text
쇼핑몰 만들어줘
```

```text
RAG 챗봇 구현해줘
```

하지만 이러한 요청은 다음과 같은 문제를 가지고 있습니다.

* 역할(Role)이 없음
* 요구사항이 부족함
* 기술 스택이 불명확함
* 출력 형식이 정의되지 않음
* 검증 조건이 없음

결과적으로 AI가 생성하는 결과물의 품질 편차가 커지게 됩니다.

Prompt-Booster는 이러한 문제를 해결하기 위해 설계되었습니다.

---

# 🎯 프로젝트 목표

Prompt-Booster의 목표는 단순합니다.

```text
긴 프롬프트 생성 ❌

좋은 프롬프트 생성 ✅
```

사용자의 의도를 분석하고 부족한 정보를 보완하여 AI가 가장 잘 이해할 수 있는 형태로 프롬프트를 최적화합니다.

---

# ✨ 주요 기능

## Intent Analysis

사용자의 요청 의도를 분석합니다.

예시

```text
게시판 만들어줘
```

↓

```text
Code Generation
```

---

## Context Expansion

누락된 요구사항을 자동 보완합니다.

예시

```text
게시판 만들어줘
```

↓

자동 보강

```text
- CRUD
- 검색
- 페이징
- 댓글
- 예외 처리
```

---

## RIF Engine

Prompt Engineering의 기본 원칙인 RIF를 적용합니다.

### Role

AI의 역할 정의

### Instruction

수행해야 할 작업 정의

### Format

원하는 출력 형식 정의

---

## Constraint Injection

실무에서 필요한 제약 조건을 자동 추가합니다.

예시

```text
- SOLID 원칙 준수
- 유지보수성 고려
- 테스트 코드 작성
- 보안 고려
- 예외 처리 포함
```

---

## Output Specification

AI가 생성해야 하는 결과 형식을 명확하게 정의합니다.

예시

```text
1. 프로젝트 구조
2. ERD
3. API 명세
4. 코드
5. 테스트 코드
```

---

## Self Validation

AI가 스스로 결과를 검토하도록 유도합니다.

검증 항목

```text
- 요구사항 누락 여부
- 컴파일 가능 여부
- 보안 취약점 여부
- 설계 문제 여부
```

---

## Adaptive Grill-Me

Prompt-Booster는 무조건 질문하지 않습니다.

먼저 가능한 범위 내에서 추론을 수행하고,

정말 필요한 정보만 사용자에게 질문합니다.

예시

```text
쇼핑몰 만들어줘
```

↓

추론

```text
- 웹 서비스
- 회원 기능 포함
- 상품 관리 포함
```

↓

질문

```text
1. Spring Boot를 사용할까요?
2. React를 사용할까요?
3. 결제 기능이 필요한가요?
```

---

# 🧠 Prompt Pattern Library

Prompt-Booster의 핵심 차별화 기능입니다.

반복적으로 사용되는 개발 패턴을 내장하여 더 높은 품질의 프롬프트를 생성합니다.

## Backend

* Spring REST API
* Spring Security
* JWT Authentication
* OAuth2 Login
* Batch Processing
* Scheduler

## Frontend

* React SPA
* Next.js
* Dashboard
* Admin Page

## AI

* RAG
* Chatbot
* Agent
* Embedding
* Vector Database

## DevOps

* Docker
* Kubernetes
* GitHub Actions
* AWS Deployment

## Architecture

* Clean Architecture
* Hexagonal Architecture
* DDD
* Microservice Architecture

---

# 🔄 Prompt Rewrite Chain

Prompt-Booster는 다음 과정을 통해 프롬프트를 최적화합니다.

```text
사용자 입력
        │
        ▼
Intent Analysis
        │
        ▼
RIF 적용
        │
        ▼
Pattern Library 적용
        │
        ▼
Constraint Injection
        │
        ▼
Self Validation 추가
        │
        ▼
최종 Prompt 생성
```

---

# 📊 Prompt Quality Score

Prompt-Booster는 프롬프트 품질을 점수화합니다.

예시

입력

```text
쇼핑몰 만들어줘
```

↓

```text
Prompt Quality Score

13 / 100
```

최적화 후

↓

```text
Prompt Quality Score

98 / 100
```

평가 기준

* Role
* Requirement
* Constraint
* Context
* Output Format
* Validation
* Technical Specificity

품질 벤치마크와 성공 지표는 [`docs/quality-benchmarks.md`](docs/quality-benchmarks.md)에 정리되어 있습니다.

---

# 🧩 Token Optimization

Prompt-Booster는 프롬프트를 길게 늘리는 방식으로 품질을 높이지 않습니다.

중간 상태는 Prompt IR로 구조화해 유지하고, 최종 렌더링 직전에 중복 요구사항, 제약조건, 출력 섹션, 검증 항목을 압축합니다.

자세한 기준은 [`docs/token-optimization.md`](docs/token-optimization.md)에 정리되어 있습니다.

테스트 계층과 로컬 검증 명령은 [`docs/test-strategy.md`](docs/test-strategy.md)에 정리되어 있습니다.

---

# 💡 변환 예시

아래 예시는 현재 `prompt.optimize --target neutral` 결과의 주요 부분을 축약한 것입니다.

## JWT 로그인 만들어줘

변환 전

```text
JWT 로그인 만들어줘
```

변환 후

```text
## Role
백엔드 개발자

## Instruction
code_generation 요청을 backend 도메인으로 최적화합니다.

## Requirements
- JWT 인증 흐름을 Access Token과 Refresh Token 기준으로 분리해 정의합니다.
- 토큰 만료, refresh strategy, secret handling, 인증 실패 오류 응답을 명시합니다.

## Output Format
- 프로젝트 구조
- 핵심 코드
- 테스트

## Validation
- JWT 만료, 서명 오류, 인증 실패 응답이 분리되어 있는지 확인합니다.
- Controller에 비즈니스 로직이 들어가지 않았는지 확인합니다.
```

품질 점수는 원문 21/100에서 최적화 후 99/100으로 상승합니다.

## 게시판 설계해줘

변환 전

```text
게시판 설계해줘
```

변환 후

```text
## Role
소프트웨어 아키텍트

## Instruction
system_design 요청을 architecture 도메인으로 최적화합니다.

## Requirements
- 모듈 책임과 의존성 방향을 포함합니다.
- 주요 구성 요소와 데이터 흐름을 제시합니다.
- 검증 가능한 완료 기준을 포함합니다.

## Output Format
- 설계 목표
- 구성 요소
- 데이터 흐름
- 검증 기준

## Validation
- 감지된 intent와 category가 최종 프롬프트 목표에 반영되어 있는지 확인합니다.
- 요구사항, 제약조건, 출력 형식, 검증 항목이 누락되지 않았는지 확인합니다.
```

품질 점수는 원문 19/100에서 최적화 후 98/100으로 상승합니다.

---

# 📚 문서 안내

| 문서 | 목적 |
| --- | --- |
| [`docs/prompt-ir.md`](docs/prompt-ir.md) | Prompt IR 구조와 예시를 설명합니다. |
| [`docs/prompt-pattern-library.md`](docs/prompt-pattern-library.md) | Pattern Library schema, category, pattern 추가 절차를 설명합니다. |
| [`docs/prompt-quality-score.md`](docs/prompt-quality-score.md) | Prompt Quality Score dimension과 scoring example을 설명합니다. |
| [`docs/codex-plugin-usage.md`](docs/codex-plugin-usage.md) | Codex Plugin 실행 방법과 명령 사용법을 설명합니다. |
| [`docs/agent-execution-flow.md`](docs/agent-execution-flow.md) | 최적화 프롬프트를 내부 실행 입력으로 전달하는 자동 실행 준비 흐름을 설명합니다. |
| [`docs/roadmap.md`](docs/roadmap.md) | v0.1부터 v1.0까지의 목표를 설명합니다. |
| [`docs/test-strategy.md`](docs/test-strategy.md) | 테스트 계층과 로컬 검증 명령을 설명합니다. |

---

# 🎯 지원 예정 플랫폼

* Codex
* Claude Code
* Cursor
* Windsurf
* Gemini CLI
* OpenHands

Agent별 target 확장 기준은 [`docs/agent-adapters.md`](docs/agent-adapters.md)에 정리되어 있습니다.

---

# 🗺️ 로드맵

Prompt-Booster의 단계별 목표는 [`docs/roadmap.md`](docs/roadmap.md)에 정리되어 있습니다.

---

# 🤝 기여하기

Prompt-Booster는 오픈소스 프로젝트입니다.

이슈, PR, 기능 제안은 언제든 환영합니다.

---

# 📜 라이선스

Apache License 2.0

Prompt-Booster는 Apache License 2.0 라이선스를 따릅니다.

상업적 사용, 수정, 배포가 가능하며 특허 관련 보호 조항을 포함합니다.

---

# 🌟 Vision

Prompt-Booster는 단순한 프롬프트 생성기가 아닙니다.

우리는 개발자의 의도를 AI에게 가장 정확하게 전달할 수 있는 Prompt Optimization Platform을 만드는 것을 목표로 합니다.

**Turn vague requests into production-ready prompts.**
