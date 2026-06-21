from __future__ import annotations

from dataclasses import dataclass

from .intent_analyzer import AnalyzerResult, Category, IntentType


@dataclass(frozen=True)
class RifRole:
    title: str
    description: str
    responsibilities: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "description": self.description,
            "responsibilities": list(self.responsibilities),
        }


@dataclass(frozen=True)
class RifInstruction:
    objective: str
    expectations: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "objective": self.objective,
            "expectations": list(self.expectations),
        }


@dataclass(frozen=True)
class RifFormatSection:
    title: str
    description: str
    required: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "description": self.description,
            "required": self.required,
        }


@dataclass(frozen=True)
class RifOutput:
    role: RifRole
    instruction: RifInstruction
    format_sections: tuple[RifFormatSection, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "role": self.role.to_dict(),
            "instruction": self.instruction.to_dict(),
            "format": {
                "sections": [section.to_dict() for section in self.format_sections],
            },
        }


DOMAIN_LABELS = {
    Category.BACKEND: "백엔드",
    Category.FRONTEND: "프론트엔드",
    Category.AI: "AI 애플리케이션",
    Category.DEVOPS: "DevOps",
    Category.ARCHITECTURE: "소프트웨어 아키텍처",
}

INTENT_LABELS = {
    IntentType.CODE_GENERATION: "구현",
    IntentType.SYSTEM_DESIGN: "시스템 설계",
    IntentType.REFACTORING: "리팩토링",
    IntentType.DEBUGGING: "디버깅",
    IntentType.TEST_GENERATION: "테스트 작성",
    IntentType.DEVOPS: "배포",
    IntentType.ARCHITECTURE: "아키텍처 설계",
}


class RifEngine:
    def generate(self, source_text: str, analysis: AnalyzerResult) -> RifOutput:
        category = analysis.category or Category.BACKEND
        intent = analysis.intent or IntentType.CODE_GENERATION

        return RifOutput(
            role=self._role_for(intent, category),
            instruction=self._instruction_for(source_text, intent, category),
            format_sections=self._format_sections_for(intent),
        )

    def _role_for(self, intent: IntentType, category: Category) -> RifRole:
        title_by_category = {
            Category.BACKEND: "백엔드 개발자",
            Category.FRONTEND: "프론트엔드 개발자",
            Category.AI: "AI 애플리케이션 개발자",
            Category.DEVOPS: "DevOps 엔지니어",
            Category.ARCHITECTURE: "소프트웨어 아키텍트",
        }
        return RifRole(
            title=title_by_category[category],
            description=f"{DOMAIN_LABELS[category]} 관점에서 {INTENT_LABELS[intent]} 요청을 구체화합니다.",
            responsibilities=(
                self._category_responsibility_for(category),
                self._intent_responsibility_for(intent),
            ),
        )

    def _instruction_for(self, source_text: str, intent: IntentType, category: Category) -> RifInstruction:
        return RifInstruction(
            objective=f"'{source_text}' 요청을 {DOMAIN_LABELS[category]} 도메인의 {INTENT_LABELS[intent]} 작업으로 구체화합니다.",
            expectations=(
                "요청의 원래 목적을 유지합니다.",
                self._category_expectation_for(category),
                self._intent_expectation_for(intent),
                "검증 가능한 완료 기준을 포함합니다.",
            ),
        )

    def _format_sections_for(self, intent: IntentType) -> tuple[RifFormatSection, ...]:
        sections_by_intent = {
            IntentType.CODE_GENERATION: (
                RifFormatSection("구현 목표", "구현해야 할 기능과 범위를 요약합니다."),
                RifFormatSection("핵심 변경 사항", "수정하거나 생성해야 할 주요 코드 단위를 설명합니다."),
                RifFormatSection("검증 계획", "테스트와 자체 검증 기준을 정의합니다."),
            ),
            IntentType.SYSTEM_DESIGN: (
                RifFormatSection("설계 목표", "해결해야 할 시스템 설계 문제를 정의합니다."),
                RifFormatSection("구성 요소", "주요 컴포넌트와 책임을 설명합니다."),
                RifFormatSection("데이터 흐름", "요청, 처리, 저장, 응답 흐름을 설명합니다."),
                RifFormatSection("검증 기준", "설계가 만족해야 할 확인 조건을 정의합니다."),
            ),
            IntentType.REFACTORING: (
                RifFormatSection("리팩토링 목표", "개선하려는 구조와 보존해야 할 동작을 정의합니다."),
                RifFormatSection("변경 범위", "수정 대상과 제외 대상을 구분합니다."),
                RifFormatSection("단계별 변경", "작은 단위로 적용할 변경 순서를 설명합니다."),
                RifFormatSection("회귀 검증", "기존 동작 보존을 확인할 테스트를 정의합니다."),
            ),
        }
        return sections_by_intent.get(
            intent,
            (
                RifFormatSection("작업 목표", "수행할 작업의 목표와 범위를 정의합니다."),
                RifFormatSection("실행 계획", "필요한 단계와 산출물을 설명합니다."),
                RifFormatSection("검증 기준", "결과를 확인할 기준을 정의합니다."),
            ),
        )

    def _category_responsibility_for(self, category: Category) -> str:
        responsibilities = {
            Category.BACKEND: "API, 서비스, 데이터 처리 책임을 분리합니다.",
            Category.FRONTEND: "화면 상태, 사용자 흐름, 컴포넌트 책임을 분리합니다.",
            Category.AI: "모델 호출, 검색, 평가 경계를 분리합니다.",
            Category.DEVOPS: "배포, 설정, 운영 검증 흐름을 분리합니다.",
            Category.ARCHITECTURE: "모듈 경계, 의존성 방향, tradeoff를 명확히 합니다.",
        }
        return responsibilities[category]

    def _intent_responsibility_for(self, intent: IntentType) -> str:
        responsibilities = {
            IntentType.CODE_GENERATION: "구현 단위와 테스트 가능한 산출물을 정의합니다.",
            IntentType.SYSTEM_DESIGN: "구성 요소, 흐름, 제약 조건을 구조화합니다.",
            IntentType.REFACTORING: "기존 동작을 보존하면서 변경 범위를 제한합니다.",
            IntentType.DEBUGGING: "재현 조건, 원인 후보, 검증 방법을 분리합니다.",
            IntentType.TEST_GENERATION: "테스트 대상, 케이스, 기대 결과를 명확히 합니다.",
            IntentType.DEVOPS: "배포 절차, 실패 대응, 상태 확인을 명시합니다.",
            IntentType.ARCHITECTURE: "아키텍처 원칙과 결정 근거를 정리합니다.",
        }
        return responsibilities[intent]

    def _category_expectation_for(self, category: Category) -> str:
        expectations = {
            Category.BACKEND: "Controller, Service, Repository 같은 계층 책임을 구분합니다.",
            Category.FRONTEND: "사용자 상태, 오류 상태, 접근성 고려사항을 포함합니다.",
            Category.AI: "외부 모델 의존성과 fallback 경계를 명시합니다.",
            Category.DEVOPS: "secret, rollback, 상태 확인 조건을 포함합니다.",
            Category.ARCHITECTURE: "모듈 책임과 의존성 방향을 포함합니다.",
        }
        return expectations[category]

    def _intent_expectation_for(self, intent: IntentType) -> str:
        expectations = {
            IntentType.CODE_GENERATION: "구현 범위, 필요한 코드 단위, 테스트 범위를 제시합니다.",
            IntentType.SYSTEM_DESIGN: "주요 구성 요소와 데이터 흐름을 제시합니다.",
            IntentType.REFACTORING: "변경 전후의 동작 보존 조건을 제시합니다.",
            IntentType.DEBUGGING: "오류 재현과 수정 검증 방법을 제시합니다.",
            IntentType.TEST_GENERATION: "정상, 실패, 경계 케이스를 구분합니다.",
            IntentType.DEVOPS: "배포 단계와 실패 시 복구 기준을 제시합니다.",
            IntentType.ARCHITECTURE: "결정 근거와 대안의 tradeoff를 제시합니다.",
        }
        return expectations[intent]
