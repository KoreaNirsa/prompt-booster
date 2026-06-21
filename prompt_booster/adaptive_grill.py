from __future__ import annotations

from dataclasses import dataclass

from .intent_analyzer import AnalyzerResult, Category


@dataclass(frozen=True)
class ClarificationQuestion:
    id: str
    topic: str
    question: str
    reason: str
    examples: tuple[str, ...]
    required: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "topic": self.topic,
            "question": self.question,
            "reason": self.reason,
            "examples": list(self.examples),
            "required": self.required,
        }


class AdaptiveGrillMe:
    def __init__(self, max_questions: int = 3) -> None:
        self._max_questions = max_questions

    def generate(self, source_text: str, analysis: AnalyzerResult) -> tuple[ClarificationQuestion, ...]:
        if analysis.fallback.used:
            return ()

        normalized = self._normalize(source_text)
        if self._is_broad_default_request(normalized) and not self._has_high_impact_signal(normalized):
            return ()

        candidates = [
            self._framework_question(normalized, analysis),
            self._persistence_question(normalized, analysis),
            self._auth_scope_question(normalized, analysis),
            self._payment_question(normalized, analysis),
            self._deployment_question(normalized, analysis),
            self._external_integration_question(normalized, analysis),
        ]
        return tuple(question for question in candidates if question is not None)[: self._max_questions]

    def _framework_question(self, normalized: str, analysis: AnalyzerResult) -> ClarificationQuestion | None:
        if analysis.category not in (Category.BACKEND, Category.FRONTEND):
            return None
        if self._has_any(normalized, ("spring", "react", "next.js", "nextjs", "django", "fastapi")):
            return None
        if not self._has_any(normalized, ("api", "서비스", "대시보드", "프레임워크", "framework", "기술 스택")):
            return None
        return ClarificationQuestion(
            id="Q-FRAMEWORK",
            topic="framework",
            question="사용할 주요 프레임워크를 지정해야 하나요?",
            reason=f"{analysis.category.value} {analysis.intent.value} 작업에서 프레임워크 선택은 파일 구조와 구현 방식에 직접 영향을 줍니다.",
            examples=("Spring Boot", "FastAPI", "React", "프로젝트 기본 스택을 따릅니다"),
        )

    def _persistence_question(self, normalized: str, analysis: AnalyzerResult) -> ClarificationQuestion | None:
        if analysis.category != Category.BACKEND:
            return None
        if self._has_any(normalized, ("mysql", "postgres", "postgresql", "mongodb", "redis", "jpa")):
            return None
        if not self._has_any(normalized, ("저장", "database", "db", "데이터", "영속", "repository")):
            return None
        return ClarificationQuestion(
            id="Q-PERSISTENCE",
            topic="persistence",
            question="데이터 저장 방식이나 저장소 제품을 지정해야 하나요?",
            reason="저장소 선택은 데이터 모델, repository 경계, 테스트 전략에 영향을 줍니다.",
            examples=("JPA와 관계형 데이터베이스", "MongoDB", "인메모리 저장소", "프로젝트 기본 저장소를 따릅니다"),
        )

    def _auth_scope_question(self, normalized: str, analysis: AnalyzerResult) -> ClarificationQuestion | None:
        if analysis.category != Category.BACKEND:
            return None
        if not self._has_any(normalized, ("인증", "로그인", "jwt", "oauth", "권한", "role", "auth")):
            return None
        if self._has_any(normalized, ("관리자", "사용자 권한", "role 기반", "rbac", "scope")):
            return None
        return ClarificationQuestion(
            id="Q-AUTH-SCOPE",
            topic="auth_scope",
            question="인증이 적용될 API 범위와 권한 수준을 어디까지 포함해야 하나요?",
            reason="인증 범위는 보호할 endpoint, 토큰 claim, 예외 처리 기준을 바꿉니다.",
            examples=("로그인과 토큰 발급만 포함", "사용자/관리자 권한 분리", "전체 API 보호", "기존 권한 정책을 따릅니다"),
        )

    def _payment_question(self, normalized: str, analysis: AnalyzerResult) -> ClarificationQuestion | None:
        if analysis.category != Category.BACKEND:
            return None
        if not self._has_any(normalized, ("결제", "payment", "checkout")):
            return None
        return ClarificationQuestion(
            id="Q-PAYMENT",
            topic="payment",
            question="결제 기능은 어떤 제공자와 결제 흐름을 기준으로 해야 하나요?",
            reason="결제 제공자와 승인/취소 흐름은 API 계약과 예외 처리를 크게 바꿉니다.",
            examples=("토스페이먼츠 카드 결제", "Stripe Checkout", "결제 예약만 구현", "결제 기능은 이번 범위에서 제외"),
        )

    def _deployment_question(self, normalized: str, analysis: AnalyzerResult) -> ClarificationQuestion | None:
        if analysis.category not in (Category.BACKEND, Category.DEVOPS):
            return None
        if not self._has_any(normalized, ("배포", "deploy", "docker", "kubernetes", "aws", "운영")):
            return None
        return ClarificationQuestion(
            id="Q-DEPLOYMENT",
            topic="deployment",
            question="배포 환경과 운영 검증 범위를 어디까지 포함해야 하나요?",
            reason="배포 대상은 설정, secret 처리, rollback, health check 요구사항에 영향을 줍니다.",
            examples=("Docker Compose 로컬 실행", "AWS 배포", "Kubernetes 배포", "배포는 이번 범위에서 제외"),
        )

    def _external_integration_question(
        self,
        normalized: str,
        analysis: AnalyzerResult,
    ) -> ClarificationQuestion | None:
        if analysis.category not in (Category.BACKEND, Category.AI):
            return None
        if not self._has_any(normalized, ("외부 연동", "api 연동", "webhook", "third-party", "3rd party", "연동")):
            return None
        return ClarificationQuestion(
            id="Q-EXTERNAL-INTEGRATION",
            topic="external_integration",
            question="연동해야 할 외부 시스템과 실패 처리 기준을 지정해야 하나요?",
            reason="외부 연동은 adapter 경계, 재시도, timeout, fallback 동작에 영향을 줍니다.",
            examples=("결제사 webhook", "외부 회원 API", "문서 검색 API", "외부 연동은 mock 경계만 정의"),
        )

    def _is_broad_default_request(self, normalized: str) -> bool:
        return self._has_any(normalized, ("쇼핑몰", "게시판"))

    def _has_high_impact_signal(self, normalized: str) -> bool:
        return self._has_any(
            normalized,
            (
                "프레임워크",
                "framework",
                "저장",
                "database",
                "db",
                "인증",
                "로그인",
                "jwt",
                "oauth",
                "권한",
                "결제",
                "payment",
                "checkout",
                "배포",
                "deploy",
                "docker",
                "kubernetes",
                "aws",
                "외부 연동",
                "api 연동",
                "webhook",
                "third-party",
                "연동",
            ),
        )

    def _normalize(self, source_text: str) -> str:
        return " ".join(source_text.casefold().split())

    def _has_any(self, normalized: str, keywords: tuple[str, ...]) -> bool:
        return any(keyword in normalized for keyword in keywords)
