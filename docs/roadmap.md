# Roadmap

이 문서는 Prompt-Booster 기획서의 단계별 목표를 v0.1부터 v1.0까지 정리합니다.

## v0.1

목표는 기본 Prompt Optimizer와 RIF Engine을 제공하는 것입니다.

- 사용자 입력의 intent와 category를 분석합니다.
- Role, Instruction, Format 기반 프롬프트 구조를 생성합니다.
- 요구사항, 제약조건, 출력 형식, 검증 항목을 구조화합니다.

## v0.2

목표는 Adaptive Grill-Me와 Prompt Quality Score를 제공하는 것입니다.

- 추론 가능한 정보는 먼저 보강합니다.
- 비즈니스 로직처럼 추측하면 안 되는 정보는 clarification question으로 남깁니다.
- 원문과 최적화 결과의 품질 점수를 비교할 수 있게 합니다.

## v0.3

목표는 Prompt Pattern Library를 제공하는 것입니다.

- backend, frontend, ai, devops, architecture category를 기준으로 반복 패턴을 관리합니다.
- 패턴별 기본 요구사항, 제약조건, 출력 섹션, 검증 항목을 재사용합니다.
- pattern matching 결과를 optimizer output에 노출합니다.

## v0.4

목표는 Codex Plugin을 제공하는 것입니다.

- `prompt.optimize`, `prompt.score`, `prompt.explain`, `prompt.patterns` 명령 계약을 고정합니다.
- Codex target 렌더링을 제공합니다.
- plugin manifest, skill, entrypoint 패키징을 검증합니다.

## v0.5

목표는 Claude Code 지원을 제공하는 것입니다.

- core analyzer와 pattern matcher는 유지합니다.
- agent adapter를 통해 최종 렌더링 단계만 target별로 분리합니다.
- `claude_code` target을 안정적인 command contract로 노출합니다.

## v1.0

목표는 멀티 AI Agent 지원입니다.

- Cursor, Windsurf, Gemini CLI, OpenHands 같은 target 확장 지점을 제공합니다.
- agent별 차이는 adapter와 renderer 경계 안에서만 처리합니다.
- core optimizer, Prompt IR, Pattern Library 계약은 target과 분리해 유지합니다.

## 유지보수 기준

- 새 roadmap 항목은 관련 이슈와 연결합니다.
- 기능 목표가 바뀌면 README, 관련 docs, test strategy를 함께 갱신합니다.
- 비즈니스 로직이 불명확한 기능은 구현 목표가 아니라 clarification 대상으로 기록합니다.
