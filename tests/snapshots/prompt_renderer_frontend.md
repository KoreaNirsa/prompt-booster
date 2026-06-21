# Optimized Prompt

## Role
프론트엔드 개발자

## Instruction
code_generation 요청을 frontend 도메인으로 최적화합니다.

## Requirements
- [must] 'React 대시보드 만들어줘' 요청을 프론트엔드 도메인의 구현 작업으로 구체화합니다.
  - 요청의 원래 목적을 유지합니다.
  - 사용자 상태, 오류 상태, 접근성 고려사항을 포함합니다.
  - 구현 범위, 필요한 코드 단위, 테스트 범위를 제시합니다.
  - 검증 가능한 완료 기준을 포함합니다.
- [must] Role, Instruction, Format 기반 프롬프트 구조를 생성합니다.
  - 구현 목표 섹션은 구현해야 할 기능과 범위를 요약합니다.
  - 핵심 변경 사항 섹션은 수정하거나 생성해야 할 주요 코드 단위를 설명합니다.
  - 검증 계획 섹션은 테스트와 자체 검증 기준을 정의합니다.
- [should] Analyzer confidence 0.65 결과를 검증 정보로 유지합니다.
  - 분석 결과와 렌더링 결과를 테스트에서 함께 확인할 수 있습니다.
- [must] React SPA의 client-side routing, route boundary, navigation fallback을 정의합니다.
  - route별 page component와 공개/보호 화면, fallback 화면이 구분됩니다.
- [must] feature state, server state, form state를 포함한 state handling 방식을 명시합니다.
  - loading/error/empty states가 데이터 흐름과 사용자 액션별로 연결됩니다.
- [must] page, layout, feature, shared component organization을 정의합니다.
  - component ownership, props/state boundary, 재사용 컴포넌트 기준이 설명됩니다.
- [must] Dashboard routing, 핵심 지표, chart, table, filter 우선순위와 정보 계층을 정의합니다.
  - 주요 KPI, 보조 지표, 상세 table, filter 영역이 구분됩니다.
- [must] 데이터 조회와 filter state, state handling, loading/error/empty states 처리 방식을 명시합니다.
  - 초기 로딩, 부분 로딩, 오류, 데이터 없음 상태가 사용자 행동과 연결됩니다.
- [should] widget, chart, table, filter, layout component organization을 정의합니다.
  - 각 widget의 데이터 입력, fallback, 테스트 책임이 설명됩니다.

## Constraints
- [maintainability] 최종 프롬프트를 렌더링하기 전까지 구조화된 IR 필드를 유지합니다.
- [testing] 렌더링 결과에 자체 검증 항목을 포함합니다.
- [style] 로딩, 오류, 빈 상태와 접근성을 함께 고려합니다.
- [style] accessibility를 위해 interactive element는 keyboard navigation과 접근 가능한 이름을 제공합니다.
- [compatibility] responsive layout은 모바일과 데스크톱 주요 breakpoint에서 정보가 겹치지 않게 설계합니다.
- [style] accessibility를 위해 chart와 table은 텍스트 대체 정보와 keyboard 접근 경로를 제공합니다.
- [compatibility] responsive layout은 카드, 표, 필터가 작은 화면에서 겹치지 않게 재배치합니다.

## Output Format
- 구현 목표: 구현해야 할 기능과 범위를 요약합니다.
- 핵심 변경 사항: 수정하거나 생성해야 할 주요 코드 단위를 설명합니다.
- 검증 계획: 테스트와 자체 검증 기준을 정의합니다.
- File Structure: route, page, layout, feature, shared component 배치를 설명합니다.; dashboard route, widget, chart, table, filter, data 파일 배치를 설명합니다.
- Components: 주요 component 역할, props, state ownership을 정리합니다.; KPI card, chart, table, filter component 역할을 정리합니다.
- Tests: routing, state handling, loading/error/empty states 검증 테스트를 포함합니다.; filter state, loading/error/empty states, chart fallback 테스트를 포함합니다.
- Styling Approach: 전역 스타일, component style, responsive layout 전략을 설명합니다.; density, responsive grid, visual state styling approach를 설명합니다.

## Validation
- [error] 감지된 intent와 category가 최종 프롬프트 목표에 반영되어 있는지 확인합니다.
- [error] 요구사항, 제약조건, 출력 형식, 검증 항목이 누락되지 않았는지 확인합니다.
- [error] routing과 fallback 화면이 요구사항에 포함되어 있는지 확인합니다.
- [error] loading/error/empty states가 누락되지 않았는지 확인합니다.
- [error] Dashboard 데이터 상태가 loading/error/empty로 분리되는지 확인합니다.
- [warning] chart와 table 정보를 보조 기술이 이해할 수 있는지 확인합니다.
