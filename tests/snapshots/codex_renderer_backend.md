# Codex Task Prompt

## Task Objective
- [objective] code_generation 요청을 backend 도메인으로 최적화합니다.
- [source] JWT 로그인 구현해줘
- [role] 백엔드 개발자

## Implementation Scope
- [must] 'JWT 로그인 구현해줘' 요청을 백엔드 도메인의 구현 작업으로 구체화합니다.
  - 요청의 원래 목적을 유지합니다.
  - Controller, Service, Repository 같은 계층 책임을 구분합니다.
  - 구현 범위, 필요한 코드 단위, 테스트 범위를 제시합니다.
  - 검증 가능한 완료 기준을 포함합니다.
- [must] Role, Instruction, Format 기반 프롬프트 구조를 생성합니다.
  - 구현 목표 섹션은 구현해야 할 기능과 범위를 요약합니다.
  - 핵심 변경 사항 섹션은 수정하거나 생성해야 할 주요 코드 단위를 설명합니다.
  - 검증 계획 섹션은 테스트와 자체 검증 기준을 정의합니다.
- [should] Analyzer confidence 0.89 결과를 검증 정보로 유지합니다.
  - 분석 결과와 렌더링 결과를 테스트에서 함께 확인할 수 있습니다.
- [must] JWT 인증 흐름을 Access Token과 Refresh Token 기준으로 분리해 정의합니다.
  - 로그인 성공 시 Access Token과 Refresh Token 발급 조건이 설명됩니다.
  - 잘못된 인증 정보와 만료 토큰 처리 조건이 설명됩니다.
- [must] 토큰 만료, refresh strategy, secret handling, 인증 실패 오류 응답을 명시합니다.
  - Access Token과 Refresh Token의 만료 기준과 재발급 정책이 분리됩니다.
  - JWT secret은 코드에 하드코딩하지 않고 안전한 설정 경로로 주입됩니다.

## File Change Expectations
- 변경 전에 관련 파일, 테스트, 기존 구조를 먼저 확인합니다.
- Prompt IR 요구사항과 제약조건에 필요한 파일만 변경합니다.
- 비즈니스 로직이 불명확하면 구현을 추측하지 않고 질문합니다.

## Constraints
- [maintainability] 최종 프롬프트를 렌더링하기 전까지 구조화된 IR 필드를 유지합니다.
- [testing] 렌더링 결과에 자체 검증 항목을 포함합니다.
- [security] 인증, 입력 검증, 오류 처리 같은 백엔드 안전 조건을 고려합니다.
- [security] 비밀번호 원문 저장을 금지하고 해시 저장을 전제로 둡니다.
- [maintainability] Controller, Service, Repository 책임을 분리합니다.
- [security] secret 또는 credential 값을 코드, 로그, 예시에 노출하지 않습니다.

## Expected Output
- 구현 목표: 구현해야 할 기능과 범위를 요약합니다.
- 핵심 변경 사항: 수정하거나 생성해야 할 주요 코드 단위를 설명합니다.
- 검증 계획: 테스트와 자체 검증 기준을 정의합니다.
- 프로젝트 구조: 인증 관련 패키지와 주요 책임을 설명합니다.
- 핵심 코드: DTO, Service, Security 설정, Filter, Controller의 핵심 코드를 포함합니다.
- 테스트: 로그인 성공, 인증 실패, 토큰 만료, refresh 실패 검증 테스트를 포함합니다.

## Verification Steps
- [error] 감지된 intent와 category가 최종 프롬프트 목표에 반영되어 있는지 확인합니다.
- [error] 요구사항, 제약조건, 출력 형식, 검증 항목이 누락되지 않았는지 확인합니다.
- [error] JWT 만료, 서명 오류, 인증 실패 응답이 분리되어 있는지 확인합니다.
- [warning] Controller에 비즈니스 로직이 들어가지 않았는지 확인합니다.
- [test] 관련 테스트와 정적 검사를 실행하고 결과를 보고합니다.
- [risk] 실행할 수 없는 검증은 이유와 남은 위험을 명시합니다.

## Operational Risk Notes
- config와 secret 주입 경로를 코드와 분리합니다.
- observability, 오류 응답, failure mode를 검토합니다.
- 배포 또는 인증 흐름 변경이 포함되면 rollback 영향을 별도로 적습니다.
