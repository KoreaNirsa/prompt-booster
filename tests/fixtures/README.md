# 핵심 샘플 fixture

이 디렉터리는 #7 회귀 테스트에서 사용하는 핵심 샘플 요청을 보관합니다.

## 유지보수 규칙

- `core_samples.json`의 각 fixture는 `id`, `name`, `sourceText`, `expectedIntent`, `expectedCategory`, `minimumSections`, `expectedBehavior`를 포함해야 합니다.
- `minimumSections`는 렌더링된 최종 프롬프트에서 사라지면 안 되는 핵심 섹션입니다.
- fixture는 모호한 사용자 입력을 보호하기 위한 회귀 기준입니다. 새로운 최적화 로직이 추가되어도 intent, category, 핵심 섹션이 의도 없이 약해지면 안 됩니다.

## 현재 fixture

| id | sourceText | expectedIntent | expectedCategory | expectedBehavior |
| --- | --- | --- | --- | --- |
| `jwt-login` | `JWT 로그인 만들어줘` | `code_generation` | `backend` | 인증 구현 요청으로 분류되고 백엔드 안전 조건을 포함한 최종 프롬프트를 생성합니다. |
| `board-design` | `게시판 설계해줘` | `system_design` | `architecture` | 설계 요청으로 분류되고 아키텍처 관점의 구조화된 프롬프트를 생성합니다. |
| `rag-chatbot` | `RAG 챗봇 구현해줘` | `code_generation` | `ai` | AI 애플리케이션 구현 요청으로 분류되고 모델 호출과 fallback 경계를 포함한 프롬프트를 생성합니다. |
| `generic-refactoring` | `리팩토링 해줘` | `refactoring` | `architecture` | 도메인이 명시되지 않은 리팩토링 요청은 구조 개선 관점의 아키텍처 작업으로 분류합니다. |
| `shopping-mall` | `쇼핑몰 만들어줘` | `code_generation` | `backend` | 쇼핑몰 구현 요청은 전자상거래 백엔드 구현 작업으로 분류하고 핵심 프롬프트 섹션을 유지합니다. |
