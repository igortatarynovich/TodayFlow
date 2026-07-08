"""Guided check-in service: pulls prompts/mantras/rituals per axes."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

from todayflow_backend.core import models
from todayflow_backend.data import astrology as astrology_ref
from todayflow_backend.data import content_system
from todayflow_backend.i18n import localize_checkin, localize_mantra, localize_ritual
from todayflow_backend.services.tarot import TarotService


class CheckInService:
    def __init__(self, tarot_service: TarotService | None = None) -> None:
        self.prompts = astrology_ref.check_ins()
        self.tarot_service = tarot_service or TarotService()

    def daily_prompt(self, user_id: int, *, locale: str | None = None) -> models.CheckInResponse:
        if not self.prompts:
            raise ValueError("Check-in prompts are not configured.")
        index = self.tarot_service._stable_seed(user_id, date.today().isoformat(), "checkin") % len(self.prompts)
        prompt = self.prompts[index]

        mantra = self._find_mantra(prompt.get("mantra_id"))
        ritual = self._find_ritual(prompt.get("ritual_id"))

        prompt_dict = localize_checkin(prompt, locale=locale)
        prompt_model = models.CheckInPrompt(
            id=prompt["id"],
            prompt=prompt_dict.get("prompt", ""),
            reflection_steps=prompt_dict.get("reflection_steps", []),
            mantra=self._create_mantra_with_human_text(mantra, locale=locale) if mantra else None,
            ritual=self._create_ritual_with_human_text(ritual, locale=locale) if ritual else None,
            cta=prompt_dict.get("cta"),
        )
        return models.CheckInResponse(prompt=prompt_model)

    @property
    def tarot(self) -> TarotService:
        return self.tarot_service

    @property
    def mantras(self) -> List[Dict]:
        return self.tarot_service.mantras

    @property
    def rituals(self) -> List[Dict]:
        return self.tarot_service.rituals

    def _find_mantra(self, mantra_id: str | None) -> Dict | None:
        if not mantra_id:
            return None
        return next((m for m in self.mantras if m["id"] == mantra_id), None)

    def _find_ritual(self, ritual_id: str | None) -> Dict | None:
        if not ritual_id:
            return None
        return next((r for r in self.rituals if r["id"] == ritual_id), None)

    def _create_mantra_with_human_text(self, mantra_data: Dict | None, *, locale: str | None = None) -> models.Mantra | None:
        """Localize mantra and add human_text from Content System."""
        if not mantra_data:
            return None
        mantra_dict = localize_mantra(mantra_data, locale=locale)
        mantra_id = mantra_dict.get("id")
        if mantra_id:
            try:
                content_mantra = content_system.get_mantra_by_id(mantra_id)
                if content_mantra and content_mantra.get("human_text"):
                    mantra_dict["human_text"] = content_mantra["human_text"]
            except Exception:
                pass
        return models.Mantra(**mantra_dict)

    def _create_ritual_with_human_text(self, ritual_data: Dict | None, *, locale: str | None = None) -> models.Ritual | None:
        """Localize ritual and add human_text from Content System."""
        if not ritual_data:
            return None
        ritual_dict = localize_ritual(ritual_data, locale=locale)
        ritual_id = ritual_dict.get("id")
        if ritual_id:
            try:
                content_ritual = content_system.get_ritual_by_id(ritual_id)
                if content_ritual and content_ritual.get("human_text"):
                    ritual_dict["human_text"] = content_ritual["human_text"]
            except Exception:
                pass
        return models.Ritual(**ritual_dict)


async def get_checkin_service() -> CheckInService:
    return CheckInService()
