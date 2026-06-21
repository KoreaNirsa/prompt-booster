---
name: prompt-booster
description: Use Prompt-Booster to optimize vague developer requests, score prompt quality, explain analyzer decisions, and list reusable prompt patterns through the local command entrypoint.
---

# Prompt Booster

Prompt-Booster는 짧고 모호한 개발 요청을 구조화된 프롬프트로 변환합니다. 이 plugin은 repo의 core library를 감싼 command entrypoint를 제공합니다.

## Commands

- `prompt.optimize`: 사용자 원문을 최적화하고 렌더링 프롬프트, IR 요약, 매칭 패턴, 질문, quality score를 반환합니다.
- `prompt.score`: 사용자 원문의 quality score와 analyzer 결과를 반환합니다.
- `prompt.explain`: analyzer 신호, pipeline steps, 매칭 패턴, 질문을 설명합니다.
- `prompt.patterns`: 사용 가능한 Pattern Library 항목을 조회합니다.

## Local Entrypoint

명령은 `scripts/prompt_booster_command.py`를 통해 실행합니다. 입력과 출력 계약은 repo의 `docs/codex-plugin-commands.md`와 `tests/fixtures/plugin_command_contract.json`을 따릅니다.
