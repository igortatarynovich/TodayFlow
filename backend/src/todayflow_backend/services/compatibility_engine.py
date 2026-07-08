"""Structured compatibility engine built on top of sign data, numerology, and synastry."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Iterable, List, Tuple

from todayflow_backend.core import models
from todayflow_backend.data import astrology as astrology_ref
from todayflow_backend.services.numerology import NumerologyService


_DIMENSION_LABELS = {
    "attraction": "Притяжение",
    "emotional": "Эмоциональная совместимость",
    "communication": "Коммуникация",
    "stability": "Стабильность",
    "long_term": "Долгий сценарий",
}


@dataclass
class CompatibilityEngineService:
    numerology_service: NumerologyService

    def __init__(self, numerology_service: NumerologyService | None = None) -> None:
        self.numerology_service = numerology_service or NumerologyService()

    def build_quick_payload(
        self,
        profile_1: Any,
        profile_2: Any,
        horoscopes_1: Dict[str, Any],
        horoscopes_2: Dict[str, Any],
        relation_mode: str | None = None,
    ) -> models.EnrichedCompatibilityResponse:
        astro_1 = horoscopes_1.get("astrology") or {}
        astro_2 = horoscopes_2.get("astrology") or {}

        sun_1 = astrology_ref.lookup_sign_metadata(astro_1.get("sun") or "")
        sun_2 = astrology_ref.lookup_sign_metadata(astro_2.get("sun") or "")
        moon_1 = astrology_ref.lookup_sign_metadata(astro_1.get("moon") or "")
        moon_2 = astrology_ref.lookup_sign_metadata(astro_2.get("moon") or "")
        rising_1 = astrology_ref.lookup_sign_metadata(astro_1.get("rising") or "")
        rising_2 = astrology_ref.lookup_sign_metadata(astro_2.get("rising") or "")

        quick_aspects: List[Dict[str, Any]] = []
        dimensions: List[models.CompatibilityDimension] = []

        attraction = self._score_sign_pair(sun_1, sun_2, base=52)
        emotional = self._score_sign_pair(moon_1, moon_2, base=54)
        communication = self._score_sign_pair(rising_1 or sun_1, rising_2 or sun_2, base=50)
        stability = self._score_life_path_pair(profile_1.birth_date, profile_2.birth_date)
        long_term = int(round((attraction + emotional + stability) / 3))

        if sun_1 and sun_2:
            quick_aspects.append({
                "type": "Солнечная пара",
                "description": self._build_sign_pair_text(sun_1, sun_2),
                "score": self._to_ten_scale(attraction),
            })
        if moon_1 and moon_2:
            quick_aspects.append({
                "type": "Лунная пара",
                "description": self._build_moon_pair_text(moon_1, moon_2),
                "score": self._to_ten_scale(emotional),
            })
        quick_aspects.append({
            "type": "Числа пути",
            "description": self._build_life_path_text(profile_1.birth_date, profile_2.birth_date),
            "score": self._to_ten_scale(stability),
        })

        dimensions.extend([
            self._dimension("attraction", attraction, "Быстрый вход в контакт, химия и интерес.", quick_aspects[:1]),
            self._dimension("emotional", emotional, "Насколько легко считывать чувства друг друга и не терять контакт в быту.", quick_aspects[1:2]),
            self._dimension("communication", communication, "Совпадение темпа, способа реагировать и входить в диалог.", []),
            self._dimension("stability", stability, "Удержание связи, бытовая опора и ресурс на длинной дистанции.", quick_aspects[2:3]),
            self._dimension("long_term", long_term, "Потенциал пары выдерживать не только яркость, но и время.", []),
        ])

        overall = int(round(sum(item.score for item in dimensions) / len(dimensions)))
        resolved_mode = self._resolve_relationship_mode(profile_1, profile_2, relation_mode)
        knowledge = self._build_knowledge_context(sun_1, sun_2, profile_1.birth_date, profile_2.birth_date, resolved_mode)

        deep_dive = models.CompatibilityDeepDive(
            relationship_archetype=self._relationship_archetype(overall, attraction, emotional, stability),
            strongest_axis=max(dimensions, key=lambda item: item.score).label,
            tension_axis=min(dimensions, key=lambda item: item.score).label,
            dimensions=dimensions,
            strengths=[str(item.get("description") or item.get("type") or "") for item in quick_aspects[:2]],
            challenges=[self._challenge_text(overall, communication, stability)],
            guidance=self._mode_guidance(resolved_mode, [self._guidance_text(overall, attraction, emotional)]),
            knowledge=knowledge,
        )

        return models.EnrichedCompatibilityResponse(
            overall_score=overall,
            summary=self._summary_text(overall, deep_dive.relationship_archetype),
            relationship_type=self._relationship_type(overall),
            aspects=quick_aspects,
            recommendations=deep_dive.guidance,
            synastry={
                "sun": {"profile_1": astro_1.get("sun"), "profile_2": astro_2.get("sun")},
                "moon": {"profile_1": astro_1.get("moon"), "profile_2": astro_2.get("moon")},
                "rising": {"profile_1": astro_1.get("rising"), "profile_2": astro_2.get("rising")},
            },
            deep_dive=deep_dive,
        )

    def build_deep_payload(
        self,
        profile_1: Any,
        profile_2: Any,
        chart1: Any,
        chart2: Any,
        synastry_report: models.SynastryReport,
        relation_mode: str | None = None,
    ) -> models.EnrichedCompatibilityResponse:
        positions_1 = {item.get("body"): item for item in chart1.positions if isinstance(item, dict) and item.get("body")}
        positions_2 = {item.get("body"): item for item in chart2.positions if isinstance(item, dict) and item.get("body")}

        sign_sun_1 = astrology_ref.lookup_sign_metadata((positions_1.get("Sun") or {}).get("sign") or "")
        sign_sun_2 = astrology_ref.lookup_sign_metadata((positions_2.get("Sun") or {}).get("sign") or "")

        attraction_markers = self._collect_aspects(synastry_report.planet_aspects, {("Venus", "Mars"), ("Mars", "Venus"), ("Venus", "Venus")})
        emotional_markers = self._collect_aspects(synastry_report.planet_aspects, {("Moon", "Moon"), ("Moon", "Venus"), ("Venus", "Moon"), ("Moon", "Sun"), ("Sun", "Moon")})
        communication_markers = self._collect_aspects(synastry_report.planet_aspects, {("Mercury", "Mercury"), ("Mercury", "Moon"), ("Moon", "Mercury"), ("Mercury", "Sun"), ("Sun", "Mercury")})
        stability_markers = self._collect_aspects(synastry_report.planet_aspects, {("Saturn", "Sun"), ("Sun", "Saturn"), ("Saturn", "Moon"), ("Moon", "Saturn"), ("Saturn", "Venus"), ("Venus", "Saturn")})
        long_term_markers = [
            *stability_markers,
            *[aspect for aspect in synastry_report.angle_aspects if aspect.angle in {"ASC", "MC"}],
        ]

        attraction = self._score_from_markers(attraction_markers, synastry_report.house_overlays, {5, 7, 8}, base=52)
        emotional = self._score_from_markers(emotional_markers, synastry_report.house_overlays, {4, 7}, base=50)
        communication = self._score_from_markers(communication_markers, synastry_report.house_overlays, {3, 9}, base=48)
        stability = self._score_from_markers(stability_markers, synastry_report.house_overlays, {4, 7, 10}, base=50)
        long_term = self._mix_scores(stability, self._score_life_path_pair(profile_1.birth_date, profile_2.birth_date), synastry_report.compatibility_summary.overall_score)

        dimension_markers = {
            "attraction": attraction_markers,
            "emotional": emotional_markers,
            "communication": communication_markers,
            "stability": stability_markers,
            "long_term": long_term_markers,
        }
        dimension_scores = {
            "attraction": attraction,
            "emotional": emotional,
            "communication": communication,
            "stability": stability,
            "long_term": long_term,
        }

        dimensions = [
            self._dimension(key, dimension_scores[key], self._dimension_summary(key, dimension_scores[key]), dimension_markers[key])
            for key in ["attraction", "emotional", "communication", "stability", "long_term"]
        ]

        quick_aspects = [
            {
                "type": "Суть связи",
                "description": synastry_report.compatibility_summary.strengths[0] if synastry_report.compatibility_summary.strengths else self._summary_text(synastry_report.compatibility_summary.overall_score, self._relationship_archetype(synastry_report.compatibility_summary.overall_score, attraction, emotional, stability)),
                "score": self._to_ten_scale(synastry_report.compatibility_summary.overall_score),
            }
        ]

        for key, markers in dimension_markers.items():
            marker = markers[0] if markers else None
            if marker is None:
                continue
            if isinstance(marker, models.SynastryAspect):
                description = marker.description
                label = f"{_DIMENSION_LABELS[key]}: {marker.planet1} {marker.aspect} {marker.planet2}"
            else:
                description = marker.description
                label = f"{_DIMENSION_LABELS[key]}: {marker.planet} {marker.aspect} {marker.angle}"
            quick_aspects.append({
                "type": label,
                "description": description,
                "score": self._to_ten_scale(dimension_scores[key]),
            })

        resolved_mode = self._resolve_relationship_mode(profile_1, profile_2, relation_mode)
        knowledge = self._build_knowledge_context(sign_sun_1, sign_sun_2, profile_1.birth_date, profile_2.birth_date, resolved_mode)
        strengths = synastry_report.compatibility_summary.strengths[:] + self._placement_meanings(positions_1, positions_2)
        challenges = synastry_report.compatibility_summary.triggers[:] + self._challenge_meanings(dimension_markers)
        if not challenges:
            challenges.append(self._challenge_text(synastry_report.compatibility_summary.overall_score, communication, stability))
        guidance = synastry_report.compatibility_summary.recommendations[:] + self._overlay_meanings(synastry_report.house_overlays)
        guidance = self._mode_guidance(resolved_mode, guidance)

        deep_dive = models.CompatibilityDeepDive(
            relationship_archetype=self._relationship_archetype(synastry_report.compatibility_summary.overall_score, attraction, emotional, stability),
            strongest_axis=max(dimensions, key=lambda item: item.score).label,
            tension_axis=min(dimensions, key=lambda item: item.score).label,
            dimensions=dimensions,
            strengths=self._unique(strengths)[:6],
            challenges=self._unique(challenges)[:6],
            guidance=guidance,
            knowledge=knowledge,
        )

        synastry_payload = synastry_report.model_dump()
        synastry_payload["deep_layers"] = {
            "dimensions": [item.model_dump() for item in dimensions],
            "relationship_archetype": deep_dive.relationship_archetype,
            "knowledge": knowledge.model_dump(),
        }

        return models.EnrichedCompatibilityResponse(
            overall_score=synastry_report.compatibility_summary.overall_score,
            summary=self._summary_text(synastry_report.compatibility_summary.overall_score, deep_dive.relationship_archetype),
            relationship_type=synastry_report.compatibility_summary.relationship_type,
            aspects=quick_aspects,
            recommendations=guidance,
            synastry=synastry_payload,
            deep_dive=deep_dive,
            profile_1={"id": getattr(profile_1, "id", None), "label": getattr(profile_1, "label", None)},
            profile_2={"id": getattr(profile_2, "id", None), "label": getattr(profile_2, "label", None)},
        )

    def _score_sign_pair(self, sign_1: Dict[str, Any] | None, sign_2: Dict[str, Any] | None, *, base: int) -> int:
        if not sign_1 or not sign_2:
            return base
        score = base
        if sign_1.get("element") == sign_2.get("element"):
            score += 18
        elif {sign_1.get("element"), sign_2.get("element")} in [{"fire", "air"}, {"earth", "water"}]:
            score += 14
        else:
            score -= 6
        if sign_1.get("modality") == sign_2.get("modality"):
            score += 6
        return max(35, min(92, score))

    def _score_life_path_pair(self, birth_date_1: date, birth_date_2: date) -> int:
        life_1 = self._life_path_value(birth_date_1)
        life_2 = self._life_path_value(birth_date_2)
        if not life_1 or not life_2:
            return 55
        diff = abs(life_1 - life_2)
        if life_1 == life_2:
            return 84
        if diff in {1, 2}:
            return 74
        if diff in {3, 6}:
            return 66
        return 58

    def _score_from_markers(
        self,
        markers: Iterable[Any],
        house_overlays: List[models.HouseOverlay],
        house_focus: set[int],
        *,
        base: int,
    ) -> int:
        score = base
        for marker in markers:
            aspect_id = getattr(marker, "aspect", "")
            aspect_meta = astrology_ref.lookup_aspect_metadata(aspect_id) or {}
            polarity = aspect_meta.get("polarity")
            strength = getattr(marker, "strength", "medium")
            weight = 8 if strength == "exact" else 6 if strength == "strong" else 4
            if polarity in {"supportive"}:
                score += weight
            elif polarity in {"challenging", "polarizing"}:
                score -= weight
            else:
                score += 2
        for overlay in house_overlays:
            if overlay.house in house_focus:
                score += 4
        return max(25, min(96, score))

    def _collect_aspects(self, aspects: Iterable[models.SynastryAspect], pairs: set[Tuple[str, str]]) -> List[models.SynastryAspect]:
        return [aspect for aspect in aspects if (aspect.planet1, aspect.planet2) in pairs]

    def _dimension(
        self,
        key: str,
        score: int,
        summary: str,
        markers: Iterable[Any],
    ) -> models.CompatibilityDimension:
        indicators: List[str] = []
        for marker in list(markers)[:3]:
            if isinstance(marker, models.SynastryAspect):
                indicators.append(f"{marker.planet1} {marker.aspect} {marker.planet2}")
            elif isinstance(marker, models.SynastryAngleAspect):
                indicators.append(f"{marker.planet} {marker.aspect} {marker.angle}")
            elif isinstance(marker, dict):
                indicators.append(str(marker.get("description") or marker.get("type") or ""))
        return models.CompatibilityDimension(
            key=key,
            label=_DIMENSION_LABELS[key],
            score=score,
            summary=self._enrich_dimension_summary(key, score, summary, list(markers)),
            indicators=[item for item in indicators if item],
        )

    def _enrich_dimension_summary(self, key: str, score: int, summary: str, markers: List[Any]) -> str:
        base = summary or self._dimension_summary(key, score)
        if not markers:
            return base
        marker = markers[0]
        if isinstance(marker, models.SynastryAspect):
            meaning = self._relationship_aspect_text(marker)
            if meaning:
                return f"{base} {meaning}"
        return base

    def _build_knowledge_context(
        self,
        sign_1: Dict[str, Any] | None,
        sign_2: Dict[str, Any] | None,
        birth_date_1: date,
        birth_date_2: date,
        relation_mode: str,
    ) -> models.CompatibilityKnowledgeContext:
        mode_record = astrology_ref.lookup_relationship_mode(relation_mode) or {}
        themes: List[str] = []
        rulers: List[str] = []
        stones: List[str] = []
        if sign_1:
            themes.extend(sign_1.get("themes") or [])
            rulers.extend(sign_1.get("rulers") or [])
            stones.extend(sign_1.get("stones") or [])
        if sign_2:
            themes.extend(sign_2.get("themes") or [])
            rulers.extend(sign_2.get("rulers") or [])
            stones.extend(sign_2.get("stones") or [])
        return models.CompatibilityKnowledgeContext(
            relationship_mode=relation_mode,
            mode_title=mode_record.get("title"),
            mode_summary=mode_record.get("summary"),
            sign_pair_summary=self._build_sign_pair_text(sign_1, sign_2) if sign_1 and sign_2 else None,
            elemental_dynamic=self._element_text(sign_1, sign_2),
            modality_dynamic=self._modality_text(sign_1, sign_2),
            rulers=self._unique(rulers)[:4],
            themes=self._unique(themes)[:6],
            stones=self._unique(stones)[:6],
            life_path_pair=self._build_life_path_text(birth_date_1, birth_date_2),
        )

    def _relationship_aspect_text(self, aspect: models.SynastryAspect) -> str | None:
        meaning = astrology_ref.lookup_relationship_aspect_meaning(aspect.planet1, aspect.planet2)
        if not meaning:
            return None
        aspect_meta = astrology_ref.lookup_aspect_metadata(aspect.aspect) or {}
        polarity = aspect_meta.get("polarity")
        aspect_description = str(aspect_meta.get("description") or "").strip()
        if polarity == "supportive":
            text = str(meaning.get("supportive") or "")
        elif polarity in {"challenging", "polarizing"}:
            text = str(meaning.get("challenging") or "")
        else:
            text = str(meaning.get("growth") or "")
        if aspect_description and text:
            return f"{text} {aspect_description}"
        return text

    def _placement_meanings(self, positions_1: Dict[str, Dict[str, Any]], positions_2: Dict[str, Dict[str, Any]]) -> List[str]:
        meanings: List[str] = []
        for planet in ["Sun", "Moon", "Venus", "Mars", "Mercury"]:
            sign_1 = (positions_1.get(planet) or {}).get("sign")
            sign_2 = (positions_2.get(planet) or {}).get("sign")
            if sign_1:
                record = astrology_ref.lookup_planet_in_sign_relationship(planet, sign_1)
                if record and record.get("meaning"):
                    meanings.append(f"{positions_1.get(planet, {}).get('body', planet)} 1: {record['meaning']}")
            if sign_2:
                record = astrology_ref.lookup_planet_in_sign_relationship(planet, sign_2)
                if record and record.get("meaning"):
                    meanings.append(f"{positions_2.get(planet, {}).get('body', planet)} 2: {record['meaning']}")
        return meanings[:4]

    def _overlay_meanings(self, overlays: List[models.HouseOverlay]) -> List[str]:
        meanings: List[str] = []
        for overlay in overlays:
            record = astrology_ref.lookup_planet_in_house_relationship(overlay.planet, overlay.house)
            if record and record.get("meaning"):
                meanings.append(str(record["meaning"]))
        return meanings[:3]

    def _challenge_meanings(self, dimension_markers: Dict[str, List[Any]]) -> List[str]:
        meanings: List[str] = []
        for markers in dimension_markers.values():
            for marker in markers[:2]:
                if isinstance(marker, models.SynastryAspect):
                    text = self._relationship_aspect_text(marker)
                    if text:
                        meanings.append(text)
        return meanings[:4]

    def _resolve_relationship_mode(self, profile_1: Any, profile_2: Any, requested_mode: str | None) -> str:
        if requested_mode and astrology_ref.lookup_relationship_mode(requested_mode):
            return requested_mode.strip().lower()
        labels = " ".join(
            str(value).lower()
            for value in [getattr(profile_1, "label", ""), getattr(profile_2, "label", ""), getattr(profile_1, "notes", ""), getattr(profile_2, "notes", "")]
            if value
        )
        if any(token in labels for token in ["коллег", "работ", "босс", "партнер по бизнесу", "cofound", "team", "команда"]):
            return "business"
        if any(token in labels for token in ["сын", "дочь", "реб", "child", "мама", "пап", "родител"]):
            return "parent_child" if any(token in labels for token in ["сын", "дочь", "реб", "child"]) else "family"
        if any(token in labels for token in ["друг", "сест", "брат", "тет", "дяд", "бабуш", "дедуш"]):
            return "family"
        return "romantic"

    def _mode_guidance(self, relation_mode: str, guidance: List[str]) -> List[str]:
        mode_record = astrology_ref.lookup_relationship_mode(relation_mode) or {}
        mode_guidance = [str(item) for item in (mode_record.get("guidance") or []) if item]
        return self._unique([*(guidance or []), *mode_guidance])[:6]

    def _build_sign_pair_text(self, sign_1: Dict[str, Any], sign_2: Dict[str, Any]) -> str:
        return f"{sign_1['name']} и {sign_2['name']} входят в контакт через {self._element_text(sign_1, sign_2)} и дают паре {self._modality_text(sign_1, sign_2)}."

    def _build_moon_pair_text(self, sign_1: Dict[str, Any], sign_2: Dict[str, Any]) -> str:
        return f"Лунный слой показывает {self._element_text(sign_1, sign_2)}. Это влияет на то, как быстро вы чувствуете безопасность, отклик и желание закрыться от мира вместе."

    def _build_life_path_text(self, birth_date_1: date, birth_date_2: date) -> str:
        life_1 = self._life_path_value(birth_date_1)
        life_2 = self._life_path_value(birth_date_2)
        if not life_1 or not life_2:
            return "Нумерологический слой пока неполный, но его можно использовать как дополнительную настройку пары."
        if life_1 == life_2:
            return f"Числа пути {life_1} и {life_2} дают похожий ритм задач и облегчают чувство «мы идем в одну сторону»."
        return f"Числа пути {life_1} и {life_2} добавляют паре разницу в темпе и приоритетах. Это не минус, но требует большей ясности в ожиданиях."

    def _life_path_value(self, value: date) -> int | None:
        try:
            result = self.numerology_service.life_path_calc(value.isoformat())
        except Exception:
            return None
        output = result.output or {}
        number = output.get("number")
        return int(number) if number is not None else None

    def _relationship_archetype(self, overall: int, attraction: int, emotional: int, stability: int) -> str:
        if attraction >= 75 and emotional >= 68:
            return "Сильное притяжение с живым эмоциональным откликом"
        if stability >= 74:
            return "Связь с потенциалом опоры и долгого пути"
        if overall < 58:
            return "Интенсивная связь, которой нужна зрелая настройка"
        return "Связь с потенциалом роста через осознанные договоренности"

    def _relationship_type(self, overall: int) -> str:
        if overall >= 76:
            return "Harmonious"
        if overall >= 58:
            return "Balanced"
        return "Challenging"

    def _summary_text(self, overall: int, archetype: str) -> str:
        if overall >= 76:
            return f"{archetype}. Между вами есть хорошая база, но лучше всего она раскрывается не сама собой, а через бережную настройку контакта."
        if overall >= 58:
            return f"{archetype}. Потенциал есть, но эта связь просит ясности в темпе, ожиданиях и способе проходить напряжение."
        return f"{archetype}. Здесь много материала для глубокого контакта, но без честных договоренностей связь легко уходит в перегруз и повторяющиеся конфликты."

    def _challenge_text(self, overall: int, communication: int, stability: int) -> str:
        if communication < 55:
            return "Самая уязвимая точка здесь — не чувства как таковые, а способ разговаривать о них. Без проговаривания ожиданий напряжение быстро копится."
        if stability < 60:
            return "Связь может ярко загораться, но хуже выдерживать рутину и долгую дистанцию. Здесь важно не жить только импульсом."
        if overall < 58:
            return "Связи может не хватать простоты и бытовой устойчивости. Лучше сразу договариваться о правилах, чем разбирать обиды постфактум."
        return "Риск здесь не в отсутствии потенциала, а в том, что сильные стороны можно принять за гарантию и перестать поддерживать контакт действиями."

    def _guidance_text(self, overall: int, attraction: int, emotional: int) -> str:
        if attraction >= 75 and emotional < 60:
            return "Притяжение здесь может идти быстрее, чем чувство безопасности. Не форсируйте глубину раньше, чем появится доверие."
        if overall >= 76:
            return "Лучшее, что вы можете сделать для этой связи, — беречь то, что уже работает, и не копить мелкое напряжение до крупного разговора."
        return "Этой связи помогает ясность: кто чего ждет, как вы проходите конфликт и что делаете, когда один хочет больше близости, а другой больше пространства."

    def _dimension_summary(self, key: str, score: int) -> str:
        if key == "attraction":
            return "Есть живая химия и импульс к сближению." if score >= 70 else "Притяжение здесь строится не только на химии, но и на том, насколько вы чувствуете безопасность."
        if key == "emotional":
            return "Эмоциональный отклик возникает сравнительно легко." if score >= 70 else "Чувства могут включаться в разном темпе, поэтому важны проверка реальности и прямой разговор."
        if key == "communication":
            return "Диалог может быть опорой пары." if score >= 70 else "Коммуникация требует настройки: вы не всегда считываете смысл друг друга с первого раза."
        if key == "stability":
            return "У связи есть ресурс на удержание и договоренности." if score >= 70 else "Удержание связи зависит от зрелости, ритма и способности возвращаться к важному."
        return "Есть хороший потенциал на длинную дистанцию." if score >= 70 else "Долгий сценарий возможен, но только если связь не строится на инерции."

    def _element_text(self, sign_1: Dict[str, Any] | None, sign_2: Dict[str, Any] | None) -> str:
        if not sign_1 or not sign_2:
            return "неполную совместимость стихий"
        left = sign_1.get("element")
        right = sign_2.get("element")
        if left == right:
            return "естественное понимание одной стихии"
        if {left, right} == {"fire", "air"}:
            return "быстрый обмен импульсом и идеями"
        if {left, right} == {"earth", "water"}:
            return "мягкую опору и бытовую устойчивость"
        if {left, right} == {"fire", "water"}:
            return "контраст напора и чувствительности"
        if {left, right} == {"earth", "air"}:
            return "разницу между практичностью и свободой"
        return "переменную динамику стихий"

    def _modality_text(self, sign_1: Dict[str, Any] | None, sign_2: Dict[str, Any] | None) -> str:
        if not sign_1 or not sign_2:
            return "разный рабочий ритм"
        left = sign_1.get("modality")
        right = sign_2.get("modality")
        if left == right:
            return "похожий ритм реакции"
        if {left, right} == {"cardinal", "fixed"}:
            return "связку старта и удержания"
        if {left, right} == {"cardinal", "mutable"}:
            return "быстрый вход в движение с риском спешки"
        if {left, right} == {"fixed", "mutable"}:
            return "разницу в гибкости и инерции"
        return "сложный, но рабочий ритм"

    def _mix_scores(self, left: int, right: int, third: int) -> int:
        return int(round((left * 0.4) + (right * 0.2) + (third * 0.4)))

    def _to_ten_scale(self, score: int) -> int:
        return max(1, min(10, int(round(score / 10))))

    def _unique(self, values: Iterable[str]) -> List[str]:
        result: List[str] = []
        seen = set()
        for value in values:
            if not value or value in seen:
                continue
            seen.add(value)
            result.append(value)
        return result


_COMPATIBILITY_ENGINE = CompatibilityEngineService()


def get_compatibility_engine_service() -> CompatibilityEngineService:
    return _COMPATIBILITY_ENGINE
