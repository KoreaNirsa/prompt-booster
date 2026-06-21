# 테스트 전략

이 문서는 이슈 #23 범위의 Prompt-Booster 테스트 계층과 로컬 검증 명령을 정리합니다.

## 테스트 계층

| 계층 | 목적 | 대표 파일 |
| --- | --- | --- |
| 단위 테스트 | Intent Analyzer, RIF Engine, Pattern Matcher, Constraint Injector, Quality Scorer, Prompt Renderer의 단일 책임을 검증합니다. | `tests/test_intent_analyzer.py`, `tests/test_rif_engine.py`, `tests/test_pattern_library.py`, `tests/test_optimizer.py`, `tests/test_quality_score.py`, `tests/test_prompt_renderer.py` |
| snapshot 테스트 | 대표 입력의 최종 렌더링 프롬프트가 의도한 구조를 유지하는지 검증합니다. | `tests/test_prompt_renderer.py`, `tests/test_codex_renderer.py`, `tests/snapshots/` |
| 회귀 테스트 | 핵심 샘플의 intent/category, 최소 섹션, Prompt IR 구조, quality score threshold가 낮아지지 않는지 검증합니다. | `tests/test_core_fixtures.py`, `tests/test_regression_contracts.py`, `tests/test_quality_benchmarks.py` |
| contract 테스트 | Codex Plugin command output envelope와 command별 output shape가 깨지지 않는지 검증합니다. | `tests/test_plugin_command_contract.py`, `tests/test_plugin_entrypoint.py`, `tests/test_regression_contracts.py` |

## 로컬 검증 명령

릴리스 전에는 다음 명령을 실행합니다.

```bash
python -m unittest discover -s tests
python tools/validate_prompt_patterns.py
python tools/validate_prompt_ir_examples.py
python tools/evaluate_quality_benchmarks.py
python -m json.tool plugins/prompt-booster/.codex-plugin/plugin.json > /dev/null
```

Windows PowerShell에서는 마지막 명령의 출력 리다이렉션을 다음처럼 사용할 수 있습니다.

```powershell
python -m json.tool plugins\prompt-booster\.codex-plugin\plugin.json > $null
```

## Assertion 기준

테스트는 단순 문구 변경에 취약한 assertion보다 구조화된 assertion을 우선합니다.

- 최종 prompt 전체 문구가 중요한 renderer는 snapshot으로 고정합니다.
- 회귀 테스트는 `promptIr.intent`, `promptIr.outputSpec.sections`, `qualityScore.total`, command envelope key처럼 구조화된 필드를 확인합니다.
- 새 benchmark나 fixture를 추가할 때 기존 threshold를 낮추기 전에 scorer, analyzer, pattern 변경이 회귀인지 먼저 확인합니다.
