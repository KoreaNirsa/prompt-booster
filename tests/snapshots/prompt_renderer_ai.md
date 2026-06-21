# Optimized Prompt

## Role
AI 애플리케이션 개발자

## Instruction
code_generation 요청을 ai 도메인으로 최적화합니다.

## Requirements
- [must] 'RAG 챗봇 구현해줘' 요청을 AI 애플리케이션 도메인의 구현 작업으로 구체화합니다.
  - 요청의 원래 목적을 유지합니다.
  - 외부 모델 의존성과 fallback 경계를 명시합니다.
  - 구현 범위, 필요한 코드 단위, 테스트 범위를 제시합니다.
  - 검증 가능한 완료 기준을 포함합니다.
- [must] Role, Instruction, Format 기반 프롬프트 구조를 생성합니다.
  - 구현 목표 섹션은 구현해야 할 기능과 범위를 요약합니다.
  - 핵심 변경 사항 섹션은 수정하거나 생성해야 할 주요 코드 단위를 설명합니다.
  - 검증 계획 섹션은 테스트와 자체 검증 기준을 정의합니다.
- [should] Analyzer confidence 0.95 결과를 검증 정보로 유지합니다.
  - 분석 결과와 렌더링 결과를 테스트에서 함께 확인할 수 있습니다.
- [must] RAG의 retrieval strategy, query 변환, top-k, reranking 기준을 정의합니다.
  - 검색 대상, ranking 기준, 검색 실패 시 fallback behavior가 설명됩니다.
- [must] 문서 chunking, overlap, metadata, source handling 방식을 명시합니다.
  - chunk 크기, 출처 보존, citation 생성 기준이 구분됩니다.
- [must] answer quality, citation accuracy, retrieval recall에 대한 evaluation criteria를 정의합니다.
  - 정답성, 근거 일치, 출처 누락, fallback 응답을 검증할 수 있습니다.
- [must] Chatbot의 conversation state, message history, system instruction 경계를 정의합니다.
  - 대화 컨텍스트 유지, 초기화, 사용자별 상태 보관 기준이 설명됩니다.
- [must] 모르는 질문, 정책 위반, 모델 오류에 대한 fallback behavior를 명시합니다.
  - 답변 불가, 재질문, 상담 연결 또는 제한 응답 조건이 구분됩니다.
- [must] 응답 품질, 안전성, hallucination 방지에 대한 evaluation criteria를 정의합니다.
  - 정확성, 정책 준수, 사용자 만족, 실패 응답을 검증할 수 있습니다.

## Constraints
- [maintainability] 최종 프롬프트를 렌더링하기 전까지 구조화된 IR 필드를 유지합니다.
- [testing] 렌더링 결과에 자체 검증 항목을 포함합니다.
- [architecture] 모델 호출, 검색, fallback 경계를 분리합니다.
- [maintainability] retrieval query, selected source, fallback reason을 관측할 수 있게 기록합니다.
- [security] 근거 없는 답변은 생성하지 않고 source handling 실패 시 제한된 fallback을 반환합니다.
- [security] 민감 정보와 정책 위반 요청은 safety constraints에 따라 제한합니다.
- [maintainability] conversation turn, fallback reason, model error를 관측할 수 있게 기록합니다.

## Output Format
- 구현 목표: 구현해야 할 기능과 범위를 요약합니다.
- 핵심 변경 사항: 수정하거나 생성해야 할 주요 코드 단위를 설명합니다.
- 검증 계획: 테스트와 자체 검증 기준을 정의합니다.
- Retrieval Design: retrieval strategy, chunking, metadata, citation 또는 source handling 정책을 설명합니다.
- Generation Flow: 검색, 컨텍스트 구성, 답변 생성, fallback behavior 흐름을 정리합니다.
- Validation Criteria: evaluation criteria, citation accuracy, retrieval recall 검증 항목을 포함합니다.
- Observability: query, retrieved chunks, source, fallback reason 로그 기준을 설명합니다.
- Conversation Flow: conversation state, message history, system instruction 경계를 설명합니다.
- Fallback Behavior: 모르는 질문, 정책 위반, 모델 오류 처리 흐름을 정리합니다.
- Validation Criteria: evaluation criteria, hallucination 방지, 안전성 검증 기준을 포함합니다.
- Observability: 대화 로그, fallback reason, model error 기록 기준을 설명합니다.

## Validation
- [error] 감지된 intent와 category가 최종 프롬프트 목표에 반영되어 있는지 확인합니다.
- [error] 요구사항, 제약조건, 출력 형식, 검증 항목이 누락되지 않았는지 확인합니다.
- [error] evaluation criteria가 retrieval과 generation 품질을 모두 다루는지 확인합니다.
- [error] citation 또는 source handling이 누락되지 않았는지 확인합니다.
- [error] validation criteria가 응답 품질과 안전성을 모두 다루는지 확인합니다.
- [warning] fallback behavior가 사용자 경험과 안전 제약을 함께 고려하는지 확인합니다.
