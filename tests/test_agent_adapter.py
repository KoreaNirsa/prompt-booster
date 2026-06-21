from collections.abc import Mapping
from dataclasses import dataclass
import unittest

from prompt_booster import (
    AgentAdapterRegistry,
    FUTURE_AGENT_TARGETS,
    PromptOptimizer,
    RendererAgentAdapter,
    default_agent_adapter_registry,
    optimize_prompt,
)
from prompt_booster.prompt_renderer import PromptRenderer


@dataclass(frozen=True)
class StaticAgentAdapter:
    target: str

    def render(self, prompt_ir: Mapping[str, object]) -> str:
        intent = prompt_ir.get("intent")
        action = intent.get("action") if isinstance(intent, dict) else ""
        return f"# Custom Agent Prompt\n- action={action}"


class AgentAdapterTest(unittest.TestCase):
    def test_default_registry_exposes_supported_and_future_targets(self):
        registry = default_agent_adapter_registry()

        self.assertEqual(("neutral", "codex", "claude_code"), registry.targets)
        self.assertEqual(("cursor", "windsurf", "gemini_cli", "openhands"), FUTURE_AGENT_TARGETS)
        self.assertEqual(FUTURE_AGENT_TARGETS, registry.future_targets)

    def test_same_ir_can_render_codex_and_claude_code_prompts(self):
        prompt_ir = optimize_prompt("JWT 로그인 구현해줘", target="codex").prompt_ir
        registry = default_agent_adapter_registry()

        codex_prompt = registry.render("codex", prompt_ir)
        claude_code_prompt = registry.render("claude_code", prompt_ir)

        self.assertTrue(codex_prompt.startswith("# Codex Task Prompt"))
        self.assertTrue(claude_code_prompt.startswith("# Claude Code Task Prompt"))
        self.assertEqual(codex_prompt.splitlines()[1:], claude_code_prompt.splitlines()[1:])
        self.assertIn("Access Token", claude_code_prompt)

    def test_optimizer_supports_claude_code_target(self):
        result = optimize_prompt("JWT 로그인 구현해줘", target="claude_code")

        self.assertTrue(result.ok)
        self.assertEqual("claude_code", result.target)
        self.assertIn("target=claude_code", result.prompt_ir["context"]["assumptions"])
        self.assertTrue(result.rendered_prompt.startswith("# Claude Code Task Prompt"))

    def test_custom_agent_can_be_added_without_core_pipeline_changes(self):
        registry = AgentAdapterRegistry(
            (
                RendererAgentAdapter("neutral", PromptRenderer()),
                StaticAgentAdapter("cursor"),
            )
        )
        optimizer = PromptOptimizer(agent_adapters=registry)

        result = optimizer.optimize("JWT 로그인 구현해줘", target="cursor")

        self.assertTrue(result.ok)
        self.assertEqual("cursor", result.target)
        self.assertEqual("# Custom Agent Prompt\n- action=implement", result.rendered_prompt)
        self.assertEqual("backend.jwt-auth", result.pattern_matches[0].pattern.id)

    def test_duplicate_adapter_target_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "중복된 agent adapter target"):
            AgentAdapterRegistry(
                (
                    RendererAgentAdapter("neutral", PromptRenderer()),
                    RendererAgentAdapter("neutral", PromptRenderer()),
                )
            )

    def test_unsupported_target_returns_clear_error(self):
        result = optimize_prompt("JWT 로그인 구현해줘", target="unknown")

        self.assertFalse(result.ok)
        self.assertEqual("unsupported_target", result.errors[0].code)
        self.assertIn("unknown", result.errors[0].message)
        self.assertIn("claude_code", result.errors[0].message)


if __name__ == "__main__":
    unittest.main()
