"""Aspect Engine service tying internal model to aspect reference."""

from __future__ import annotations

from math import fabs
from typing import Dict, List, Tuple

from todayflow_backend.core import models
from todayflow_backend.data import astrology as astrology_ref
from todayflow_backend.i18n import translate

BODY_PAIRS = [
    ("sun", "moon"),
    ("sun", "saturn"),
    ("sun", "mars"),
    ("moon", "saturn"),
    ("moon", "venus"),
    ("mercury", "saturn"),
    ("venus", "mars"),
]


class AspectEngine:
    def __init__(self) -> None:
        aspects = astrology_ref.aspects()
        self.aspect_map = {a["id"]: a for a in aspects}
        self.relations = self._load_relations()

    @staticmethod
    def _pair_key(left: str, right: str) -> str:
        return f"{left}_{right}"

    def _load_relations(self) -> Dict[str, Dict]:
        relations: Dict[str, Dict] = {}
        for relation in astrology_ref.aspect_relations():
            key = self._pair_key(relation["left"], relation["right"])
            relations[key] = relation
        return relations

    def _relation_for_pair(self, left: str, right: str) -> Dict | None:
        return self.relations.get(self._pair_key(left, right)) or self.relations.get(self._pair_key(right, left))

    def callouts(self, positions: List[Dict[str, float]], locale: str | None = None) -> models.AspectResponse:
        indexed = {pos["body"]: pos for pos in positions if "body" in pos and "longitude" in pos}
        callouts: List[models.AspectCallout] = []
        for left, right in BODY_PAIRS:
            if left not in indexed or right not in indexed:
                continue
            aspect_id, degrees, orb_delta = self._resolve_aspect(indexed[left]["longitude"], indexed[right]["longitude"])
            if not aspect_id:
                continue
            record = self.aspect_map.get(aspect_id)
            if not record:
                continue
            relation = self._relation_for_pair(left, right)
            strength = self._strength_label(orb_delta)
            label = f"{left.title()} {aspect_id.replace('_', ' ').title()} {right.title()}"
            description = record.get("description", "")
            integration = None
            axes: List[str] = []
            modulators: List[str] = []
            section = None
            if relation:
                if summary_key := relation.get("summary_key"):
                    description = translate(summary_key, locale=locale, default=description)
                if integration_key := relation.get("integration_key"):
                    integration_value = translate(integration_key, locale=locale, default="")
                    integration = integration_value or None
                axes = relation.get("axes", [])
                modulators = relation.get("modulators", [])
                section = relation.get("section")
            callouts.append(
                models.AspectCallout(
                    aspect_id=aspect_id,
                    label=label,
                    bodies=f"{left.title()} · {right.title()}",
                    keywords=record.get("keywords", []),
                    description=description,
                    tension_level=record.get("tension_level", ""),
                    polarity=record.get("polarity", ""),
                    degrees_apart=round(degrees, 2),
                    orb_delta=round(orb_delta, 2),
                    strength=strength,
                    axes=axes,
                    modulators=modulators,
                    section=section,
                    integration=integration,
                )
            )
        return models.AspectResponse(callouts=callouts)

    def _resolve_aspect(self, left_long: float, right_long: float) -> Tuple[str | None, float, float]:
        raw_difference = fabs(left_long - right_long) % 360
        if raw_difference > 180:
            raw_difference = 360 - raw_difference
        for aspect_id, record in self.aspect_map.items():
            angle = record.get("angle")
            orb = record.get("orb", 0)
            if angle is None:
                continue
            delta = fabs(raw_difference - angle)
            if delta <= orb:
                return aspect_id, raw_difference, delta
        return None, raw_difference, 0.0

    @staticmethod
    def _strength_label(delta: float) -> str:
        if delta <= 1.0:
            return "exact"
        if delta <= 3.0:
            return "tight"
        return "loose"


def get_aspect_engine() -> AspectEngine:
    """Синхронная фабрика (без I/O). Нужна и для Depends(...), и для прямого вызова из natal_chart."""
    return AspectEngine()
