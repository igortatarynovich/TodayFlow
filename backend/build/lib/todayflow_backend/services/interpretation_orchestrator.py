"""Deterministic interpretation orchestrator for cross-module consistency."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class InterpretationOrchestrator:
    """Applies stable rules to avoid contradictory daily recommendations."""

    version: str = "orchestrator-v1"

    def build_daily_guidance(
        self,
        core_profile: dict[str, Any] | None,
        numerology: dict[str, Any] | None,
        needs: str | None,
    ) -> dict[str, Any]:
        if not core_profile:
            return {
                "version": self.version,
                "focus": "Базовый ритм",
                "do_focus": "Один короткий осознанный шаг",
                "avoid_focus": "Распыление и резкие решения",
                "tone": "neutral",
                "rules_applied": ["fallback_without_profile"],
            }

        baseline = (core_profile.get("baseline") or {})
        numerology = numerology or {}
        life_path = self._as_int((core_profile.get("numerology") or {}).get("life_path"))
        day_number = self._as_int(numerology.get("dayNumber"))
        element_focus = baseline.get("element_focus") or "Стабильность и бережный темп"
        rhythm_style = baseline.get("rhythm_style") or "Малые повторяемые действия"

        do_focus = element_focus
        avoid_focus = "Перегруз задач и реактивные решения"
        tone = "grounded"
        rules_applied = ["baseline_element_focus", "baseline_rhythm_style"]

        if needs:
            do_focus = self._append_focus(do_focus, self._needs_focus_phrase(needs))
            rules_applied.append("needs_domain_priority")

        if day_number is not None:
            if day_number in {1, 8}:
                do_focus = self._append_focus(do_focus, "Сделай один ясный шаг, где нужна инициатива.")
                avoid_focus = "Импульсивные конфликты и давление"
                tone = "directive"
            elif day_number in {2, 6}:
                do_focus = self._append_focus(do_focus, "Держись мягкой коммуникации и не ускоряй чувствительные разговоры.")
                avoid_focus = "Эмоциональные качели и самокритику"
                tone = "supportive"
            elif day_number in {4, 7}:
                do_focus = self._append_focus(do_focus, "Лучше завершать начатое, чем распыляться на новое.")
                avoid_focus = "Хаос и частые переключения"
                tone = "structured"
            rules_applied.append("daily_number_alignment")

        if life_path in {11, 22, 33}:
            do_focus = self._append_focus(do_focus, "Зафиксируй смысл дня в одной короткой записи.")
            rules_applied.append("master_number_reflection")

        # Contradiction guard: "do" and "avoid" must not overlap semantically by text.
        if self._normalized(do_focus) in self._normalized(avoid_focus):
            avoid_focus = "Действия без внутренней опоры"
            rules_applied.append("anti_contradiction_guard")

        return {
            "version": self.version,
            "focus": rhythm_style,
            "do_focus": do_focus,
            "avoid_focus": avoid_focus,
            "tone": tone,
            "rules_applied": rules_applied,
        }

    @staticmethod
    def _normalized(value: str) -> str:
        return (value or "").strip().lower()

    @staticmethod
    def _as_int(value: Any) -> int | None:
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return None

    @staticmethod
    def _append_focus(base: str, addition: str | None) -> str:
        extra = (addition or "").strip()
        root = (base or "").strip()
        if not extra:
            return root
        if not root:
            return extra
        if root.endswith((".", "!", "?")):
            return f"{root} {extra}"
        return f"{root}. {extra}"

    @staticmethod
    def _needs_focus_phrase(needs: str) -> str:
        normalized = (needs or "").strip().lower()
        return {
            "love": "В отношениях важнее не угадывать, а держать контакт живым.",
            "relationship": "В отношениях важнее не угадывать, а держать контакт живым.",
            "money_career": "В работе и деньгах полезнее опираться на ясные договоренности.",
            "business": "В работе и деньгах полезнее опираться на ясные договоренности.",
            "state": "Сейчас особенно важно не перегружать себя и не терять внутреннюю опору.",
            "pattern": "Полезнее замечать повторяющийся сценарий до того, как он снова включится.",
            "decision": "Лучше сузить выбор до одного проверяемого следующего шага.",
            "general": "Лучше держаться одного понятного направления, а не распыляться.",
        }.get(normalized, "Лучше держаться одного понятного направления, а не распыляться.")


_ORCHESTRATOR = InterpretationOrchestrator()


def get_interpretation_orchestrator() -> InterpretationOrchestrator:
    return _ORCHESTRATOR
