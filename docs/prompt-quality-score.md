# Prompt Quality Score

이 문서는 이슈 #9 범위의 Prompt Quality Score 산정 기준을 정의합니다.

## 점수 항목

점수는 항상 0부터 100 사이의 정수입니다. 총점은 아래 항목별 점수의 합입니다.

| 항목 | 최대 점수 | 평가 기준 |
| --- | ---: | --- |
| Role | 10 | 역할 또는 대상 독자가 명시되어 있는지 평가합니다. |
| Requirement | 25 | 구현, 설계, 테스트 같은 요구사항이 구체적인 항목으로 표현되어 있는지 평가합니다. |
| Constraint | 20 | 보안, 오류 처리, 성능, 접근성, 유지보수성 같은 제약조건이 있는지 평가합니다. |
| Context | 15 | 도메인, 프로젝트 상태, 기술 스택, 기존 맥락이 있는지 평가합니다. |
| Output Format | 10 | Markdown, JSON, 섹션, 체크리스트 같은 출력 형식이 정의되어 있는지 평가합니다. |
| Validation | 10 | 테스트, 검증, 확인 조건이 있는지 평가합니다. |
| Technical Specificity | 10 | 프레임워크, 계층, 컴포넌트, 저장소, 토큰, 배포 같은 기술 단서가 구체적인지 평가합니다. |

## Dimension 설명

- Role은 AI가 어떤 역할이나 대상 독자 관점에서 답해야 하는지 평가합니다.
- Requirement는 구현, 설계, 테스트 같은 작업 요구가 구체적인 항목과 수용 기준으로 표현되는지 평가합니다.
- Constraint는 보안, 오류 처리, 유지보수성, 접근성, 배포 같은 제한 조건이 있는지 평가합니다.
- Context는 도메인, 프로젝트 상태, 기술 스택, 기존 맥락이 포함되는지 평가합니다.
- Output Format은 Markdown, JSON, 섹션, 체크리스트처럼 결과 형식이 정의되는지 평가합니다.
- Validation은 테스트와 자체 검증 조건이 포함되는지 평가합니다.
- Technical Specificity는 프레임워크, 계층, 컴포넌트, 저장소, 토큰, 배포 같은 기술 단서가 충분한지 평가합니다.

## 점수 경계

| 범위 | 등급 | 예시 |
| --- | --- | --- |
| 0-39 | 낮은 품질 | `Build app`처럼 작업 의도만 있고 역할, 맥락, 제약조건, 출력 형식, 검증 조건이 대부분 없는 요청입니다. |
| 40-79 | 중간 품질 | `Implement JWT login API with tests and error handling`처럼 핵심 요구와 일부 검증 조건은 있지만 역할, 출력 형식, 프로젝트 맥락이 부족한 요청입니다. |
| 80-100 | 높은 품질 | 역할, 기술 스택, 요구사항, 제약조건, 출력 섹션, 검증 체크리스트가 함께 명시된 요청입니다. |

## Scoring Example

예시는 현재 `prompt.optimize --source-text "쇼핑몰 만들어줘" --target neutral` 결과를 기준으로 합니다.

| 항목 | 원문 점수 | 최적화 후 점수 | 변화 이유 |
| --- | ---: | ---: | --- |
| Role | 0/10 | 10/10 | 최적화 후 `백엔드 개발자` 역할이 정의됩니다. |
| Requirement | 6/25 | 25/25 | 구현 범위, 코드 단위, 테스트 범위, 완료 기준이 구조화됩니다. |
| Constraint | 0/20 | 20/20 | IR 유지, 자체 검증, 보안 조건이 추가됩니다. |
| Context | 5/15 | 15/15 | backend domain과 API, Service, Persistence 맥락이 정리됩니다. |
| Output Format | 0/10 | 10/10 | 구현 목표, 핵심 변경 사항, 검증 계획 섹션이 정의됩니다. |
| Validation | 0/10 | 10/10 | intent/category 반영과 필수 항목 누락 검증이 추가됩니다. |
| Technical Specificity | 2/10 | 8/10 | backend 구현 단서가 보강되지만 세부 비즈니스 정책은 추측하지 않습니다. |
| 총점 | 13/100 | 98/100 | 모호한 요청이 구조화된 개발 프롬프트로 변환됩니다. |

이 예시에서 상품, 결제, 배송 같은 비즈니스 정책은 자동 구현 요구사항으로 확정하지 않습니다. 필요한 경우 Adaptive Grill-Me가 사용자에게 질문해야 합니다.

## 진단 정보

각 점수 결과는 총점, 항목별 breakdown, 진단 정보를 포함합니다.

- `missing`: 해당 항목의 점수가 0점입니다.
- `weak`: 해당 항목의 점수가 최대 점수보다 낮습니다.

Prompt IR 내부 `qualityScore`는 기존 스키마 계약을 유지하기 위해 총점과 항목별 breakdown만 포함합니다. 원본 입력과 최적화된 출력의 진단 정보는 Optimizer 결과의 `sourceQualityScore`, `optimizedQualityScore`에서 제공합니다.

품질 회귀를 확인하기 위한 benchmark set과 성공 지표는 [`quality-benchmarks.md`](quality-benchmarks.md)에 정리되어 있습니다.
