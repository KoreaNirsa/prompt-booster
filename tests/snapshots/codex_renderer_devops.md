# Codex Task Prompt

## Task Objective
- [objective] devops 요청을 devops 도메인으로 최적화합니다.
- [source] GitHub Actions CI 배포 만들어줘
- [role] DevOps 엔지니어

## Implementation Scope
- [must] 'GitHub Actions CI 배포 만들어줘' 요청을 DevOps 도메인의 배포 작업으로 구체화합니다.
  - 요청의 원래 목적을 유지합니다.
  - secret, rollback, 상태 확인 조건을 포함합니다.
  - 배포 단계와 실패 시 복구 기준을 제시합니다.
  - 검증 가능한 완료 기준을 포함합니다.
- [must] Role, Instruction, Format 기반 프롬프트 구조를 생성합니다.
  - 작업 목표 섹션은 수행할 작업의 목표와 범위를 정의합니다.
  - 실행 계획 섹션은 필요한 단계와 산출물을 설명합니다.
  - 검증 기준 섹션은 결과를 확인할 기준을 정의합니다.
- [should] Analyzer confidence 0.95 결과를 검증 정보로 유지합니다.
  - 분석 결과와 렌더링 결과를 테스트에서 함께 확인할 수 있습니다.
- [must] GitHub Actions workflow trigger, job, step, reusable command를 정의합니다.
  - trigger, runner, dependency cache, artifact, permissions가 구분됩니다.
- [must] secret handling은 GitHub Secrets와 environment variable을 사용하고 로그에 secret을 노출하지 않습니다.
  - 토큰, cloud credential, registry credential이 workflow 파일에 직접 기록되지 않습니다.
- [must] 재현 가능한 명령과 실패 진단 기준을 각 job 또는 step에 포함합니다.
  - 로컬 재현 명령, 실패 로그 위치, 다음 확인 단계가 설명됩니다.
- [must] AWS deployment 대상 서비스, region, IAM 권한, environment assumption을 정의합니다.
  - 배포 대상, 네트워크, IAM role, 환경별 configuration이 구분됩니다.
- [must] secret handling은 AWS Secrets Manager, Parameter Store, environment variable 참조를 사용합니다.
  - access key, secret key, token은 코드, 로그, 예시 명령에 직접 노출되지 않습니다.
- [must] rollback, health check, observability, failure-mode expectations를 포함합니다.
  - 배포 실패, 헬스 체크 실패, 알람 발생 시 rollback 또는 중단 절차가 설명됩니다.
- [must] Kubernetes workload, service, ingress, configuration, environment variable, environment assumption을 정의합니다.
  - namespace, deployment, service, ingress, config map, environment variable 또는 secret 사용 기준이 구분됩니다.
- [must] secret handling은 manifest와 로그에 secret 값을 직접 노출하지 않도록 설계합니다.
  - secret은 Kubernetes Secret 또는 외부 secret manager로 참조됩니다.
- [must] rollback, health check, readiness/liveness probe, observability, failure-mode expectations를 포함합니다.
  - 배포 실패, probe 실패, rollout 중단, rollback 절차가 설명됩니다.

## File Change Expectations
- 변경 전에 관련 파일, 테스트, 기존 구조를 먼저 확인합니다.
- Prompt IR 요구사항과 제약조건에 필요한 파일만 변경합니다.
- 비즈니스 로직이 불명확하면 구현을 추측하지 않고 질문합니다.

## Constraints
- [maintainability] 최종 프롬프트를 렌더링하기 전까지 구조화된 IR 필드를 유지합니다.
- [testing] 렌더링 결과에 자체 검증 항목을 포함합니다.
- [deployment] secret 노출 없이 rollback과 상태 확인을 고려합니다.
- [security] workflow permissions는 최소 권한으로 선언하고 위험한 배포는 명시적 opt-in으로 제한합니다.
- [deployment] 배포 job은 rollback, health check, observability 조건을 통과한 뒤 진행합니다.
- [deployment] production 기본값은 비용과 권한을 보수적으로 제한하고 위험한 동작은 opt-in으로 둡니다.
- [maintainability] 변경 이력, 배포자, 환경, 실패 원인을 추적할 수 있어야 합니다.
- [deployment] production 변경은 위험한 동작을 명시적 opt-in으로 제한합니다.
- [performance] resource request/limit과 autoscaling 가정은 환경별로 명시합니다.
- [security] secret 또는 credential 값을 코드, 로그, 예시에 노출하지 않습니다.

## Expected Output
- 작업 목표: 수행할 작업의 목표와 범위를 정의합니다.
- 실행 계획: 필요한 단계와 산출물을 설명합니다.
- 검증 기준: 결과를 확인할 기준을 정의합니다.
- Workflow Contract: trigger, job, step, permission, environment variable 경계를 설명합니다.
- Reproducible Commands: 로컬 재현 명령, CI 실행 명령, 실패 진단 기준을 정리합니다.
- Secret Handling: GitHub Secrets, environment variable, 로그 마스킹 기준을 설명합니다.; Secrets Manager, Parameter Store, environment variable 참조 기준을 정리합니다.
- Validation Criteria: workflow syntax, 실패 진단, 권한, secret 노출 방지 검증 기준을 포함합니다.; 배포 전 검증, 배포 후 검증, secret 노출 방지, rollback 검증 기준을 포함합니다.; dry-run, rollout status, probe, secret 노출 방지 검증 기준을 포함합니다.
- Deployment Target: AWS service, region, IAM, network, configuration 가정을 설명합니다.
- Operational Checks: rollback, health check, observability, failure-mode expectations를 포함합니다.
- Manifest Design: workload, service, ingress, configuration, secret 참조를 설명합니다.
- Deployment Operations: rollback, health check, observability, failure-mode expectations를 정리합니다.
- Environment Assumptions: namespace, resource, region, cluster 권한 가정을 설명합니다.

## Verification Steps
- [error] 감지된 intent와 category가 최종 프롬프트 목표에 반영되어 있는지 확인합니다.
- [error] 요구사항, 제약조건, 출력 형식, 검증 항목이 누락되지 않았는지 확인합니다.
- [error] 재현 가능한 명령과 실패 진단 기준이 각 job에 포함되는지 확인합니다.
- [error] secret과 credential이 workflow 파일 또는 로그에 노출되지 않는지 확인합니다.
- [error] AWS credential과 secret이 코드, 로그, 명령 예시에 노출되지 않는지 확인합니다.
- [error] rollback, health check, observability, failure-mode expectations가 정의되는지 확인합니다.
- [error] secret 값이 manifest와 로그에 노출되지 않는지 확인합니다.
- [error] rollback, health check, observability가 배포 절차에 포함되는지 확인합니다.
- [test] 관련 테스트와 정적 검사를 실행하고 결과를 보고합니다.
- [risk] 실행할 수 없는 검증은 이유와 남은 위험을 명시합니다.

## Operational Risk Notes
- config와 secret 주입 경로를 코드와 분리합니다.
- observability, 오류 응답, failure mode를 검토합니다.
- 배포 변경에는 rollback 절차와 상태 확인 방법을 포함합니다.
