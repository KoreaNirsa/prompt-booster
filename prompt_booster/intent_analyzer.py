from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


class IntentType(str, Enum):
    CODE_GENERATION = "code_generation"
    SYSTEM_DESIGN = "system_design"
    REFACTORING = "refactoring"
    DEBUGGING = "debugging"
    TEST_GENERATION = "test_generation"
    DEVOPS = "devops"
    ARCHITECTURE = "architecture"


class Category(str, Enum):
    BACKEND = "backend"
    FRONTEND = "frontend"
    AI = "ai"
    DEVOPS = "devops"
    ARCHITECTURE = "architecture"


@dataclass(frozen=True)
class MatchedSignal:
    kind: str
    value: str
    keyword: str
    weight: int

    def to_dict(self) -> dict[str, str | int]:
        return {
            "kind": self.kind,
            "value": self.value,
            "keyword": self.keyword,
            "weight": self.weight,
        }


@dataclass(frozen=True)
class FallbackInfo:
    used: bool
    reason: str | None

    def to_dict(self) -> dict[str, bool | str | None]:
        return {
            "used": self.used,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class AnalyzerResult:
    intent: IntentType | None
    category: Category | None
    matched_signals: tuple[MatchedSignal, ...]
    confidence: float
    fallback: FallbackInfo

    def to_dict(self) -> dict[str, object]:
        return {
            "intent": self.intent.value if self.intent else None,
            "category": self.category.value if self.category else None,
            "matchedSignals": [signal.to_dict() for signal in self.matched_signals],
            "confidence": self.confidence,
            "fallback": self.fallback.to_dict(),
        }


@dataclass(frozen=True)
class SignalRule:
    kind: str
    value: IntentType | Category
    keywords: tuple[str, ...]
    weight: int


INTENT_RULES: tuple[SignalRule, ...] = (
    SignalRule(
        "intent",
        IntentType.ARCHITECTURE,
        (
            "clean architecture",
            "hexagonal",
            "ddd",
            "msa",
            "architecture",
            "아키텍처",
            "도메인 주도",
        ),
        4,
    ),
    SignalRule(
        "intent",
        IntentType.DEVOPS,
        (
            "github actions",
            "kubernetes",
            "docker",
            "ci",
            "cd",
            "aws",
            "deploy",
            "배포",
            "인프라",
        ),
        4,
    ),
    SignalRule(
        "intent",
        IntentType.TEST_GENERATION,
        (
            "test",
            "tests",
            "unit test",
            "테스트",
            "회귀",
            "검증",
        ),
        3,
    ),
    SignalRule(
        "intent",
        IntentType.DEBUGGING,
        (
            "debug",
            "bug",
            "error",
            "fix",
            "디버그",
            "버그",
            "오류",
            "에러",
            "고쳐",
        ),
        3,
    ),
    SignalRule(
        "intent",
        IntentType.REFACTORING,
        (
            "refactor",
            "refactoring",
            "cleanup",
            "리팩토링",
            "개선",
            "정리",
        ),
        3,
    ),
    SignalRule(
        "intent",
        IntentType.SYSTEM_DESIGN,
        (
            "system design",
            "design",
            "erd",
            "설계",
            "구조",
        ),
        3,
    ),
    SignalRule(
        "intent",
        IntentType.CODE_GENERATION,
        (
            "implement",
            "create",
            "build",
            "make",
            "develop",
            "code",
            "구현",
            "만들어",
            "작성",
            "개발",
            "생성",
        ),
        2,
    ),
)


CATEGORY_RULES: tuple[SignalRule, ...] = (
    SignalRule(
        "category",
        Category.AI,
        (
            "rag",
            "llm",
            "embedding",
            "vector database",
            "agent",
            "chatbot",
            "ai",
            "챗봇",
            "임베딩",
            "벡터",
        ),
        4,
    ),
    SignalRule(
        "category",
        Category.DEVOPS,
        (
            "github actions",
            "kubernetes",
            "docker",
            "aws",
            "ci",
            "cd",
            "deploy",
            "배포",
            "인프라",
        ),
        4,
    ),
    SignalRule(
        "category",
        Category.ARCHITECTURE,
        (
            "clean architecture",
            "hexagonal",
            "ddd",
            "msa",
            "architecture",
            "system design",
            "아키텍처",
            "설계",
            "경계",
        ),
        3,
    ),
    SignalRule(
        "category",
        Category.ARCHITECTURE,
        (
            "refactor",
            "refactoring",
            "cleanup",
            "리팩토링",
            "개선",
            "정리",
        ),
        1,
    ),
    SignalRule(
        "category",
        Category.FRONTEND,
        (
            "react",
            "next.js",
            "nextjs",
            "dashboard",
            "component",
            "ui",
            "page",
            "frontend",
            "프론트엔드",
            "화면",
            "컴포넌트",
        ),
        3,
    ),
    SignalRule(
        "category",
        Category.BACKEND,
        (
            "spring",
            "jwt",
            "oauth",
            "api",
            "rest",
            "jpa",
            "database",
            "entity",
            "controller",
            "service",
            "backend",
            "로그인",
            "인증",
            "서비스",
            "서버",
            "백엔드",
            "게시판",
            "crud",
            "쇼핑몰",
            "커머스",
            "ecommerce",
            "e-commerce",
            "commerce",
            "상품",
            "주문",
            "결제",
        ),
        3,
    ),
)


class IntentAnalyzer:
    def analyze(self, text: str) -> AnalyzerResult:
        normalized = self._normalize(text)
        if not normalized:
            return AnalyzerResult(
                intent=None,
                category=None,
                matched_signals=(),
                confidence=0.0,
                fallback=FallbackInfo(used=True, reason="empty_input"),
            )

        intent, intent_score, intent_signals = self._match_best(normalized, INTENT_RULES)
        category, category_score, category_signals = self._match_best(normalized, CATEGORY_RULES)
        matched_signals = (*intent_signals, *category_signals)

        fallback_reason = self._fallback_reason(intent, category)
        confidence = self._confidence(intent_score, category_score, fallback_reason)

        return AnalyzerResult(
            intent=intent if isinstance(intent, IntentType) else None,
            category=category if isinstance(category, Category) else None,
            matched_signals=matched_signals,
            confidence=confidence,
            fallback=FallbackInfo(used=fallback_reason is not None, reason=fallback_reason),
        )

    def _match_best(
        self,
        normalized: str,
        rules: tuple[SignalRule, ...],
    ) -> tuple[IntentType | Category | None, int, tuple[MatchedSignal, ...]]:
        scores: dict[IntentType | Category, int] = {}
        signals: list[MatchedSignal] = []

        for rule in rules:
            for keyword in rule.keywords:
                if self._keyword_matches(normalized, keyword):
                    scores[rule.value] = scores.get(rule.value, 0) + rule.weight
                    signals.append(
                        MatchedSignal(
                            kind=rule.kind,
                            value=rule.value.value,
                            keyword=keyword,
                            weight=rule.weight,
                        )
                    )

        if not scores:
            return None, 0, ()

        order = {rule.value: index for index, rule in enumerate(rules)}
        selected = max(scores, key=lambda value: (scores[value], -order[value]))
        selected_signals = tuple(signal for signal in signals if signal.value == selected.value)
        return selected, scores[selected], selected_signals

    def _fallback_reason(
        self,
        intent: IntentType | Category | None,
        category: IntentType | Category | None,
    ) -> str | None:
        if intent is None and category is None:
            return "no_supported_signal"
        if intent is None:
            return "intent_unclassified"
        if category is None:
            return "category_unclassified"
        return None

    def _confidence(self, intent_score: int, category_score: int, fallback_reason: str | None) -> float:
        if intent_score == 0 and category_score == 0:
            return 0.0

        confidence = min(0.95, 0.25 + ((intent_score + category_score) * 0.08))
        if fallback_reason:
            confidence = min(confidence, 0.55)
        return round(confidence, 2)

    def _normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.casefold()).strip()

    def _keyword_matches(self, normalized: str, keyword: str) -> bool:
        if self._is_ascii_keyword(keyword):
            return re.search(rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])", normalized) is not None
        return keyword in normalized

    def _is_ascii_keyword(self, keyword: str) -> bool:
        return keyword.isascii()


def analyze_intent(text: str) -> AnalyzerResult:
    return IntentAnalyzer().analyze(text)
