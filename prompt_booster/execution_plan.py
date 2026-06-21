from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .adaptive_grill import ClarificationQuestion
from .optimizer import OptimizerResult, PromptOptimizer


EXECUTION_MODES = ("render_only", "auto_execute")


@dataclass(frozen=True)
class ExecutionBlockedReason:
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "message": self.message,
        }


@dataclass(frozen=True)
class AgentExecutionInput:
    target: str
    prompt: str
    source_text: str
    prompt_ir_summary: dict[str, object] | None
    matched_patterns: tuple[dict[str, object], ...]
    clarification_answers: tuple[dict[str, str], ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "target": self.target,
            "prompt": self.prompt,
            "sourceText": self.source_text,
            "promptIrSummary": self.prompt_ir_summary,
            "matchedPatterns": list(self.matched_patterns),
            "clarificationAnswers": list(self.clarification_answers),
            "executionPolicy": {
                "businessLogicGuessing": "forbidden",
                "requiresAllRequiredClarifications": True,
            },
        }


@dataclass(frozen=True)
class ExecutionPlan:
    mode: str
    target: str
    status: str
    rendered_prompt: str | None
    execution_input: AgentExecutionInput | None
    required_questions: tuple[ClarificationQuestion, ...]
    blocked_reasons: tuple[ExecutionBlockedReason, ...]

    @property
    def execution_ready(self) -> bool:
        return self.status == "ready"

    def to_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "target": self.target,
            "status": self.status,
            "executionReady": self.execution_ready,
            "renderedPrompt": self.rendered_prompt,
            "executionInput": self.execution_input.to_dict() if self.execution_input else None,
            "requiredQuestions": [question.to_dict() for question in self.required_questions],
            "blockedReasons": [reason.to_dict() for reason in self.blocked_reasons],
        }


class PromptExecutionPlanner:
    def __init__(self, optimizer: PromptOptimizer | None = None, max_questions: int = 3) -> None:
        self._optimizer = optimizer or PromptOptimizer()
        self._max_questions = max_questions

    def plan(
        self,
        source_text: str,
        target: str = "codex",
        mode: str = "render_only",
        clarification_answers: Mapping[str, object] | None = None,
    ) -> ExecutionPlan:
        if mode not in EXECUTION_MODES:
            raise ValueError(f"지원하지 않는 execution mode입니다: {mode}")

        result = self._optimizer.optimize(source_text, target)
        if not result.ok:
            return ExecutionPlan(
                mode=mode,
                target=target,
                status="blocked",
                rendered_prompt=result.rendered_prompt if mode == "render_only" else None,
                execution_input=None,
                required_questions=(),
                blocked_reasons=tuple(
                    ExecutionBlockedReason(code=error.code, message=error.message) for error in result.errors
                ),
            )

        if mode == "render_only":
            return ExecutionPlan(
                mode=mode,
                target=target,
                status="render_only",
                rendered_prompt=result.rendered_prompt,
                execution_input=None,
                required_questions=(),
                blocked_reasons=(),
            )

        questions = self._execution_questions(result)
        normalized_answers = self._normalize_answers(clarification_answers)
        missing_questions = tuple(question for question in questions if not self._answer_for(question, normalized_answers))
        if missing_questions:
            return ExecutionPlan(
                mode=mode,
                target=target,
                status="blocked",
                rendered_prompt=None,
                execution_input=None,
                required_questions=missing_questions,
                blocked_reasons=(
                    ExecutionBlockedReason(
                        code="required_clarification_missing",
                        message="자동 실행 전에 필수 비즈니스 또는 고영향 요구사항 답변이 필요합니다.",
                    ),
                ),
            )

        answered_questions = self._answered_questions(questions, normalized_answers)
        return ExecutionPlan(
            mode=mode,
            target=target,
            status="ready",
            rendered_prompt=None,
            execution_input=AgentExecutionInput(
                target=target,
                prompt=self._prompt_with_clarification_answers(result.rendered_prompt or "", answered_questions),
                source_text=source_text,
                prompt_ir_summary=self._prompt_ir_summary(result.prompt_ir),
                matched_patterns=tuple(self._pattern_match_summary(match) for match in result.pattern_matches),
                clarification_answers=answered_questions,
            ),
            required_questions=(),
            blocked_reasons=(),
        )

    def _execution_questions(self, result: OptimizerResult) -> tuple[ClarificationQuestion, ...]:
        questions = list(result.clarification_questions)
        if not questions:
            broad_question = self._broad_business_scope_question(result.source_text)
            if broad_question:
                questions.append(broad_question)
        return tuple(questions[: self._max_questions])

    def _broad_business_scope_question(self, source_text: str) -> ClarificationQuestion | None:
        normalized = " ".join(source_text.casefold().split())
        if "쇼핑몰" in normalized:
            return ClarificationQuestion(
                id="Q-BUSINESS-SCOPE",
                topic="business_scope",
                question="자동 실행 전에 쇼핑몰의 핵심 비즈니스 범위를 어디까지로 제한해야 하나요?",
                reason="상품, 주문, 결제, 배송 범위는 구현할 API, 데이터 모델, 예외 처리를 크게 바꿉니다.",
                examples=(
                    "상품 조회와 장바구니까지만 포함",
                    "주문 생성까지 포함하고 결제는 제외",
                    "회원, 상품, 주문, 결제를 모두 포함",
                    "기존 기획서 범위를 따릅니다",
                ),
            )
        if "게시판" in normalized:
            return ClarificationQuestion(
                id="Q-BUSINESS-SCOPE",
                topic="business_scope",
                question="자동 실행 전에 게시판의 핵심 기능과 권한 범위를 어디까지로 제한해야 하나요?",
                reason="댓글, 파일 첨부, 공지, 권한 범위는 API contract와 저장 모델을 바꿉니다.",
                examples=(
                    "게시글 CRUD만 포함",
                    "댓글과 파일 첨부까지 포함",
                    "관리자 공지와 사용자 권한을 포함",
                    "기존 서비스 정책을 따릅니다",
                ),
            )
        return None

    def _normalize_answers(self, answers: Mapping[str, object] | None) -> dict[str, str]:
        if not answers:
            return {}
        return {
            str(key): str(value).strip()
            for key, value in answers.items()
            if str(key).strip() and str(value).strip()
        }

    def _answer_for(self, question: ClarificationQuestion, answers: Mapping[str, str]) -> str:
        return answers.get(question.id, "") or answers.get(question.topic, "")

    def _answered_questions(
        self,
        questions: Sequence[ClarificationQuestion],
        answers: Mapping[str, str],
    ) -> tuple[dict[str, str], ...]:
        answered = []
        for question in questions:
            answer = self._answer_for(question, answers)
            if answer:
                answered.append({"id": question.id, "topic": question.topic, "answer": answer})
        return tuple(answered)

    def _prompt_with_clarification_answers(
        self,
        rendered_prompt: str,
        answered_questions: Sequence[Mapping[str, str]],
    ) -> str:
        if not answered_questions:
            return rendered_prompt
        lines = [rendered_prompt.rstrip(), "", "## Clarification Answers"]
        for answer in answered_questions:
            lines.append(f"- {answer['topic']}: {answer['answer']}")
        return "\n".join(lines)

    def _prompt_ir_summary(self, prompt_ir: dict[str, object] | None) -> dict[str, object] | None:
        if prompt_ir is None:
            return None
        intent = prompt_ir.get("intent")
        context = prompt_ir.get("context")
        output_spec = prompt_ir.get("outputSpec")
        return {
            "id": prompt_ir.get("id"),
            "intent": intent if isinstance(intent, dict) else None,
            "context": {
                "audience": context.get("audience"),
                "techStack": context.get("techStack"),
            }
            if isinstance(context, dict)
            else None,
            "requirementCount": len(self._list_value(prompt_ir.get("requirements"))),
            "constraintCount": len(self._list_value(prompt_ir.get("constraints"))),
            "outputSectionCount": len(self._list_value(output_spec.get("sections")))
            if isinstance(output_spec, dict)
            else 0,
            "validationRuleCount": len(self._list_value(prompt_ir.get("validationRules"))),
        }

    def _pattern_match_summary(self, match: object) -> dict[str, object]:
        pattern = getattr(match, "pattern")
        return {
            "id": pattern.id,
            "category": pattern.category,
            "rank": getattr(match, "rank"),
            "confidence": getattr(match, "confidence"),
        }

    def _list_value(self, value: object) -> list[object]:
        return value if isinstance(value, list) else []


def plan_prompt_execution(
    source_text: str,
    target: str = "codex",
    mode: str = "render_only",
    clarification_answers: Mapping[str, object] | None = None,
) -> ExecutionPlan:
    return PromptExecutionPlanner().plan(source_text, target, mode, clarification_answers)
