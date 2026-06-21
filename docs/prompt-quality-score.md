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

## 점수 경계

| 범위 | 등급 | 예시 |
| --- | --- | --- |
| 0-39 | 낮은 품질 | `Build app`처럼 작업 의도만 있고 역할, 맥락, 제약조건, 출력 형식, 검증 조건이 대부분 없는 요청입니다. |
| 40-79 | 중간 품질 | `Implement JWT login API with tests and error handling`처럼 핵심 요구와 일부 검증 조건은 있지만 역할, 출력 형식, 프로젝트 맥락이 부족한 요청입니다. |
| 80-100 | 높은 품질 | 역할, 기술 스택, 요구사항, 제약조건, 출력 섹션, 검증 체크리스트가 함께 명시된 요청입니다. |

## 진단 정보

각 점수 결과는 총점, 항목별 breakdown, 진단 정보를 포함합니다.

- `missing`: 해당 항목의 점수가 0점입니다.
- `weak`: 해당 항목의 점수가 최대 점수보다 낮습니다.

Prompt IR 내부 `qualityScore`는 기존 스키마 계약을 유지하기 위해 총점과 항목별 breakdown만 포함합니다. 원본 입력과 최적화된 출력의 진단 정보는 Optimizer 결과의 `sourceQualityScore`, `optimizedQualityScore`에서 제공합니다.

품질 회귀를 확인하기 위한 benchmark set과 성공 지표는 [`quality-benchmarks.md`](quality-benchmarks.md)에 정리되어 있습니다.
