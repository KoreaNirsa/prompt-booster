# Token Optimization

이 문서는 이슈 #17 범위의 토큰 최적화 전략을 정의합니다.

## 목적

Prompt-Booster의 목표는 긴 프롬프트를 만드는 것이 아니라, 필요한 지시를 빠짐없이 유지하면서 반복 설명을 줄인 고품질 프롬프트를 만드는 것입니다. 토큰 최적화는 정보 삭제가 아니라 구조화된 중간 상태를 유지한 뒤 최종 렌더링 직전에 중복을 압축하는 방식으로 수행합니다.

## 긴 프롬프트와 고품질 프롬프트의 차이

| 구분 | 긴 프롬프트 | 고품질 프롬프트 |
| --- | --- | --- |
| 요구사항 | 같은 요구를 여러 문장으로 반복합니다. | 요구사항과 수용 기준을 구조화해 한 번씩만 제시합니다. |
| 제약조건 | 보안, 테스트, 유지보수 같은 boilerplate가 반복됩니다. | 같은 제약 설명은 한 줄로 유지하고 필요한 scope만 결합합니다. |
| 출력 형식 | 같은 섹션 제목이 여러 번 등장합니다. | 같은 제목의 섹션은 설명을 병합해 한 섹션으로 렌더링합니다. |
| 검증 | 같은 검증 항목이 여러 severity로 반복됩니다. | 같은 검증 설명은 가장 높은 severity로 한 번만 렌더링합니다. |

## 적용 단계

1. Optimizer는 Analyzer, RIF, Pattern Library, Constraint Injection 결과를 Prompt IR로 유지합니다.
2. Pattern content는 Prompt IR의 requirements, constraints, outputSpec, validationRules에 구조화된 상태로 병합됩니다.
3. Renderer는 최종 텍스트를 만들기 직전에 중복 항목을 압축합니다.
4. 렌더링 결과는 필요한 지시와 검증 기준을 보존하되 반복되는 boilerplate를 피합니다.

## 1차 압축 규칙

- Requirements: 같은 description은 한 번만 렌더링하고 acceptance criteria는 중복 없이 병합합니다. priority가 다르면 `must`, `should`, `could` 순서로 더 강한 값을 사용합니다.
- Constraints: 같은 description은 한 번만 렌더링하고 scope는 중복 없이 결합합니다.
- Output sections: 같은 title은 한 번만 렌더링하고 서로 다른 description은 `;`로 병합합니다.
- Validation rules: 같은 description은 한 번만 렌더링하고 severity는 `error`, `warning`, `info` 순서로 더 강한 값을 사용합니다.

## 검증

토큰 최적화는 `tests/test_prompt_renderer.py`의 구조화된 중복 압축 테스트와 `tests/snapshots`의 렌더링 결과로 검증합니다. Prompt IR 스키마는 변경하지 않으며, 최종 텍스트 확장 직전 Renderer에서만 압축을 수행합니다.
