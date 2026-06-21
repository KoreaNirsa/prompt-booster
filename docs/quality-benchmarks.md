# 품질 벤치마크와 성공 지표

이 문서는 이슈 #22 범위의 Prompt-Booster 품질 벤치마크를 정의합니다. 목표는 프롬프트 길이를 늘리는 것이 아니라 AI 코딩 에이전트가 더 적은 재질문과 수정 요청으로 실행 가능한 결과를 만들도록 돕는 것입니다.

## 벤치마크 세트

벤치마크 정의는 [`benchmarks/prompt-quality-benchmarks.json`](../benchmarks/prompt-quality-benchmarks.json)에 있습니다. 현재 세트는 다음 도메인을 모두 포함합니다.

| 도메인 | 대표 case |
| --- | --- |
| backend | JWT 로그인 구현 |
| frontend | React 대시보드 구현 |
| ai | RAG 챗봇 구현 |
| devops | GitHub Actions CI 배포 |
| architecture | Clean Architecture 모듈 경계 설계 |

각 case는 모호한 원문 프롬프트, 기대 intent/category, 최소 출력 섹션, quality score 기대값을 포함합니다.

## 성공 지표

| 지표 | 확인 방법 |
| --- | --- |
| 요구사항 누락 감소 | 최적화된 Prompt IR의 requirements와 output sections가 case별 minimumSections를 모두 포함하는지 확인합니다. |
| 출력 품질 향상 | optimized quality score가 case별 optimizedMin 이상인지 확인합니다. |
| 추가 수정 요청 감소 | constraints와 validationRules가 테스트, 오류 처리, 보안, 운영 조건을 포함하는지 확인합니다. |
| 생산성 향상 | optimized score와 source score의 차이가 case별 improvementMin 이상인지 확인합니다. |

## 로컬 평가

자동화가 완성되기 전에는 다음 명령으로 벤치마크를 로컬에서 확인합니다.

```bash
python tools/evaluate_quality_benchmarks.py
```

명령은 각 case의 분류 결과, 최소 섹션, source/optimized quality score, 개선폭을 검사하고 JSON 요약을 출력합니다. 실패한 case는 `errors`에 누락 섹션이나 점수 조건을 표시합니다.

## 수동 평가

로컬 명령을 실행할 수 없는 경우에는 다음 순서로 문서 기반 검토를 진행합니다.

1. benchmark case의 `sourceText`를 `prompt.optimize`에 입력합니다.
2. 반환된 `promptIr.intent`와 `promptIr.intent.primaryDomain`이 기대값과 일치하는지 확인합니다.
3. `promptIr.outputSpec.sections`에 `minimumSections`가 모두 포함되는지 확인합니다.
4. `sourceQualityScore.total`, `optimizedQualityScore.total`, 두 점수의 차이가 `qualityExpectations`를 만족하는지 확인합니다.
5. 실패한 조건은 새 case의 기대값을 낮추기 전에 scorer 또는 pattern 변경의 회귀인지 먼저 확인합니다.

## 새 case 추가 기준

새 benchmark case는 기존 품질 기준을 약화하지 않아야 합니다.

- 기존 case의 `optimizedMin` 또는 `improvementMin`을 낮추지 않습니다.
- 새 case는 하나의 모호한 원문 요청과 명확한 기대 intent/category를 가져야 합니다.
- 최소 섹션은 실제 산출물이 실행 가능한 결과를 만드는 데 필요한 항목만 포함합니다.
- source prompt가 충분히 모호한지 확인하기 위해 `sourceMax`는 40 이하로 둡니다.
- 새 도메인을 추가하면 문서의 도메인 표와 테스트 기대 도메인도 함께 갱신합니다.
