from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Protocol

from .claude_code_renderer import ClaudeCodePromptRenderer
from .codex_renderer import CodexPromptRenderer
from .prompt_renderer import PromptRenderer


FUTURE_AGENT_TARGETS = ("cursor", "windsurf", "gemini_cli", "openhands")


class PromptAgentAdapter(Protocol):
    target: str

    def render(self, prompt_ir: Mapping[str, object]) -> str:
        """Render shared Prompt IR into a target-specific prompt."""
        ...


@dataclass(frozen=True)
class RendererAgentAdapter:
    target: str
    renderer: PromptRenderer

    def render(self, prompt_ir: Mapping[str, object]) -> str:
        return self.renderer.render(prompt_ir)


class AgentAdapterRegistry:
    def __init__(self, adapters: Iterable[PromptAgentAdapter]) -> None:
        self._adapters: dict[str, PromptAgentAdapter] = {}
        for adapter in adapters:
            if adapter.target in self._adapters:
                raise ValueError(f"중복된 agent adapter target입니다: {adapter.target}")
            self._adapters[adapter.target] = adapter

    @property
    def targets(self) -> tuple[str, ...]:
        return tuple(self._adapters)

    @property
    def future_targets(self) -> tuple[str, ...]:
        return FUTURE_AGENT_TARGETS

    def get(self, target: str) -> PromptAgentAdapter | None:
        return self._adapters.get(target)

    def render(self, target: str, prompt_ir: Mapping[str, object]) -> str:
        adapter = self.get(target)
        if adapter is None:
            raise KeyError(f"지원하지 않는 agent adapter target입니다: {target}")
        return adapter.render(prompt_ir)


def default_agent_adapter_registry(neutral_renderer: PromptRenderer | None = None) -> AgentAdapterRegistry:
    return AgentAdapterRegistry(
        (
            RendererAgentAdapter("neutral", neutral_renderer or PromptRenderer()),
            RendererAgentAdapter("codex", CodexPromptRenderer()),
            RendererAgentAdapter("claude_code", ClaudeCodePromptRenderer()),
        )
    )
