# Codex Task Prompt

## Task Objective
- [objective] refactoring 요청을 backend 도메인으로 최적화합니다.
- [source] 서비스 코드 리팩토링 해줘
- [role] 백엔드 개발자

## Implementation Scope
- [must] '서비스 코드 리팩토링 해줘' 요청을 백엔드 도메인의 리팩토링 작업으로 구체화합니다.
  - 요청의 원래 목적을 유지합니다.
  - Controller, Service, Repository 같은 계층 책임을 구분합니다.
  - 변경 전후의 동작 보존 조건을 제시합니다.
  - 검증 가능한 완료 기준을 포함합니다.
- [must] Role, Instruction, Format 기반 프롬프트 구조를 생성합니다.
  - 리팩토링 목표 섹션은 개선하려는 구조와 보존해야 할 동작을 정의합니다.
  - 변경 범위 섹션은 수정 대상과 제외 대상을 구분합니다.
  - 단계별 변경 섹션은 작은 단위로 적용할 변경 순서를 설명합니다.
  - 회귀 검증 섹션은 기존 동작 보존을 확인할 테스트를 정의합니다.
- [should] Analyzer confidence 0.73 결과를 검증 정보로 유지합니다.
  - 분석 결과와 렌더링 결과를 테스트에서 함께 확인할 수 있습니다.

## File Change Expectations
- 변경 전에 관련 파일, 테스트, 기존 구조를 먼저 확인합니다.
- Prompt IR 요구사항과 제약조건에 필요한 파일만 변경합니다.
- 비즈니스 로직이 불명확하면 구현을 추측하지 않고 질문합니다.

## Constraints
- [maintainability] 최종 프롬프트를 렌더링하기 전까지 구조화된 IR 필드를 유지합니다.
- [testing] 렌더링 결과에 자체 검증 항목을 포함합니다.
- [security] 인증, 입력 검증, 오류 처리 같은 백엔드 안전 조건을 고려합니다.
- [security] secret 또는 credential 값을 코드, 로그, 예시에 노출하지 않습니다.

## Expected Output
- 리팩토링 목표: 개선하려는 구조와 보존해야 할 동작을 정의합니다.
- 변경 범위: 수정 대상과 제외 대상을 구분합니다.
- 단계별 변경: 작은 단위로 적용할 변경 순서를 설명합니다.
- 회귀 검증: 기존 동작 보존을 확인할 테스트를 정의합니다.

## Verification Steps
- [error] 감지된 intent와 category가 최종 프롬프트 목표에 반영되어 있는지 확인합니다.
- [error] 요구사항, 제약조건, 출력 형식, 검증 항목이 누락되지 않았는지 확인합니다.
- [test] 관련 테스트와 정적 검사를 실행하고 결과를 보고합니다.
- [risk] 실행할 수 없는 검증은 이유와 남은 위험을 명시합니다.

## Operational Risk Notes
- config와 secret 주입 경로를 코드와 분리합니다.
- observability, 오류 응답, failure mode를 검토합니다.
- 배포 또는 인증 흐름 변경이 포함되면 rollback 영향을 별도로 적습니다.
