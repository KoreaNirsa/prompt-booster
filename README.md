# 🚀 Prompt-Booster

> 모호한 요청을 실무 수준의 프롬프트로 변환합니다.
>
> **Developer-Focused Prompt Optimization Platform**

Prompt-Booster는 개발자의 짧고 모호한 요청을 AI 코딩 에이전트가 이해하기 쉬운 고품질 프롬프트로 변환하는 오픈소스 프로젝트입니다.

단순히 프롬프트를 길게 만드는 것이 아니라, Prompt Engineering 기법을 적용하여 AI가 더 정확하고 일관된 결과를 생성할 수 있도록 돕습니다.

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

15 / 100
```

최적화 후

↓

```text
Prompt Quality Score

95 / 100
```

평가 기준

* Role
* Requirement
* Constraint
* Context
* Output Format
* Validation
* Technical Specificity

---

# 🧩 Token Optimization

Prompt-Booster는 프롬프트를 길게 늘리는 방식으로 품질을 높이지 않습니다.

중간 상태는 Prompt IR로 구조화해 유지하고, 최종 렌더링 직전에 중복 요구사항, 제약조건, 출력 섹션, 검증 항목을 압축합니다.

자세한 기준은 [`docs/token-optimization.md`](docs/token-optimization.md)에 정리되어 있습니다.

---

# 💡 예시

입력

```text
JWT 로그인 만들어줘
```

Prompt-Booster 출력

```text
당신은 시니어 Spring Boot 백엔드 개발자입니다.

목표:
Spring Security와 JWT를 사용한 인증 시스템을 구현하세요.

요구사항:
- Access Token
- Refresh Token
- Stateless 인증
- BCrypt PasswordEncoder

출력:
1. 프로젝트 구조
2. Entity
3. DTO
4. SecurityConfig
5. JWT Filter
6. Service
7. Controller
8. 테스트 코드

검증:
- 로그인 성공 여부
- 토큰 만료 처리
- 예외 처리
```

---

# 🎯 지원 예정 플랫폼

* Codex
* Claude Code
* Cursor
* Windsurf
* Gemini CLI
* OpenHands

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
