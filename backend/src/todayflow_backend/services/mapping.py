"""Map astrology chart results into the internal axis/modulator model."""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable

from todayflow_backend.core import models

SIGN_META = {
    "Aries": {"element": "fire", "modality": "cardinal"},
    "Taurus": {"element": "earth", "modality": "fixed"},
    "Gemini": {"element": "air", "modality": "mutable"},
    "Cancer": {"element": "water", "modality": "cardinal"},
    "Leo": {"element": "fire", "modality": "fixed"},
    "Virgo": {"element": "earth", "modality": "mutable"},
    "Libra": {"element": "air", "modality": "cardinal"},
    "Scorpio": {"element": "water", "modality": "fixed"},
    "Sagittarius": {"element": "fire", "modality": "mutable"},
    "Capricorn": {"element": "earth", "modality": "cardinal"},
    "Aquarius": {"element": "air", "modality": "fixed"},
    "Pisces": {"element": "water", "modality": "mutable"},
}

ORIENTATION_SCORES = {"fire": 80, "air": 50, "earth": -45, "water": -75}
EMOTIONAL_SCORES = {"fire": 65, "air": 30, "earth": -35, "water": -70}
DECISION_SCORES = {"fire": -45, "air": 70, "earth": 45, "water": -60}
CONTROL_SCORES = {"fire": 75, "air": -35, "earth": 45, "water": -60}
RELATIONSHIP_SCORES = {"fire": -40, "air": -30, "earth": 35, "water": 70}
ENERGY_SCORES = {"fire": 75, "air": 35, "earth": -35, "water": -65}
CHANGE_BONUS = {"fire": 15, "air": 10, "earth": -10, "water": -15}

STRESS_MOON = {"fire": -15, "air": -10, "earth": 10, "water": 25}
STRESS_SATURN = {"fire": 5, "air": -5, "earth": -10, "water": 15}
ADAPTATION_MERCURY = {"fire": 5, "air": 10, "earth": -5, "water": -12}
REFLECTION_MERCURY = {"fire": -10, "air": 20, "earth": 15, "water": 5}
REFLECTION_SATURN = {"fire": -5, "air": 0, "earth": 10, "water": 5}
PRESSURE_SATURN = {"fire": 5, "air": -10, "earth": -15, "water": 20}
PRESSURE_HOUSE = {"fire": 5, "air": -5, "earth": -10, "water": 12}

PRIMARY_MODALITY_BODIES = ("sun", "moon", "mercury", "venus", "mars")


def clamp(value: float, lower: float = -100.0, upper: float = 100.0) -> float:
    return round(max(lower, min(upper, value)), 2)


def element_for(sign: str | None) -> str | None:
    if not sign:
        return None
    meta = SIGN_META.get(sign)
    if not meta:
        return None
    return meta["element"]


def modality_for(sign: str | None) -> str | None:
    if not sign:
        return None
    meta = SIGN_META.get(sign)
    if not meta:
        return None
    return meta["modality"]


def score_from_sign(sign: str | None, table: Dict[str, float]) -> float:
    element = element_for(sign)
    if not element:
        return 0.0
    return table.get(element, 0.0)


class InternalModelMapper:
    """Mapping layer aligned with SPEC/Model_Mapping_v1.md."""

    def map(self, chart_response: Dict[str, Any]) -> models.InternalModelSnapshot:
        positions = self._index_positions(chart_response.get("positions", []))
        houses = chart_response.get("houses") or {}
        mode = chart_response.get("mode", "unknown_time")

        axes = [
            self._axis_identity(positions, mode),
            self._axis_emotional(positions, mode),
            self._axis_decision(positions),
            self._axis_stability(positions),
            self._axis_control(positions),
            self._axis_relational(positions),
            self._axis_energy(positions, mode),
        ]

        modulators = [
            self._modulator_stress(positions, mode),
            self._modulator_adaptation(positions),
            self._modulator_reflection(positions),
            self._modulator_pressure(positions, houses, mode),
        ]

        return models.InternalModelSnapshot(axes=axes, modulators=modulators, mode=mode)

    def _axis_identity(self, positions: Dict[str, Dict[str, Any]], mode: str) -> models.AxisValue:
        sun_sign = self._sign_for(positions, "sun")
        asc_sign = self._sign_for(positions, "rising")
        if not sun_sign and not asc_sign:
            return models.AxisValue(axis_id="A1", value=0.0, confidence="low")

        value = score_from_sign(sun_sign, ORIENTATION_SCORES) * 0.6
        if asc_sign:
            asc_weight = 0.4 if mode == "precise" else 0.2
            value += score_from_sign(asc_sign, ORIENTATION_SCORES) * asc_weight
        confidence = "high" if asc_sign and mode == "precise" else "medium"
        return models.AxisValue(axis_id="A1", value=clamp(value), confidence=confidence)

    def _axis_emotional(self, positions: Dict[str, Dict[str, Any]], mode: str) -> models.AxisValue:
        moon_sign = self._sign_for(positions, "moon")
        if not moon_sign:
            return models.AxisValue(axis_id="A2", value=0.0, confidence="low")
        value = score_from_sign(moon_sign, EMOTIONAL_SCORES)
        if mode != "precise":
            value *= 0.75
            confidence = "medium"
        else:
            confidence = "high"
        return models.AxisValue(axis_id="A2", value=clamp(value), confidence=confidence)

    def _axis_decision(self, positions: Dict[str, Dict[str, Any]]) -> models.AxisValue:
        mercury_sign = self._sign_for(positions, "mercury")
        if not mercury_sign:
            return models.AxisValue(axis_id="A3", value=0.0, confidence="low")
        value = score_from_sign(mercury_sign, DECISION_SCORES)
        return models.AxisValue(axis_id="A3", value=clamp(value), confidence="high")

    def _axis_stability(self, positions: Dict[str, Dict[str, Any]]) -> models.AxisValue:
        counts = self._modality_counts(positions, PRIMARY_MODALITY_BODIES)
        total = sum(counts.values())
        if not total:
            return models.AxisValue(axis_id="A4", value=0.0, confidence="low")

        change_ratio = (counts["mutable"] + 0.5 * counts["cardinal"]) / total
        stability_ratio = counts["fixed"] / total
        value = (change_ratio - stability_ratio) * 100
        uranus_sign = self._sign_for(positions, "uranus")
        value += score_from_sign(uranus_sign, CHANGE_BONUS)
        confidence = "high" if total >= 4 else "medium"
        return models.AxisValue(axis_id="A4", value=clamp(value), confidence=confidence)

    def _axis_control(self, positions: Dict[str, Dict[str, Any]]) -> models.AxisValue:
        mars_sign = self._sign_for(positions, "mars")
        if not mars_sign:
            return models.AxisValue(axis_id="A5", value=0.0, confidence="low")
        value = score_from_sign(mars_sign, CONTROL_SCORES)
        return models.AxisValue(axis_id="A5", value=clamp(value), confidence="high")

    def _axis_relational(self, positions: Dict[str, Dict[str, Any]]) -> models.AxisValue:
        venus_sign = self._sign_for(positions, "venus")
        if not venus_sign:
            return models.AxisValue(axis_id="A6", value=0.0, confidence="low")
        value = score_from_sign(venus_sign, RELATIONSHIP_SCORES)
        return models.AxisValue(axis_id="A6", value=clamp(value), confidence="high")

    def _axis_energy(self, positions: Dict[str, Dict[str, Any]], mode: str) -> models.AxisValue:
        sun_sign = self._sign_for(positions, "sun")
        mars_sign = self._sign_for(positions, "mars")
        if not sun_sign and not mars_sign:
            return models.AxisValue(axis_id="A7", value=0.0, confidence="low")

        value = score_from_sign(sun_sign, ENERGY_SCORES) * 0.55
        if mars_sign:
            value += score_from_sign(mars_sign, ENERGY_SCORES) * 0.45
        if mode != "precise":
            value *= 0.9
        confidence = "high" if sun_sign and mars_sign else "medium"
        return models.AxisValue(axis_id="A7", value=clamp(value), confidence=confidence)

    def _modulator_stress(self, positions: Dict[str, Dict[str, Any]], mode: str) -> models.ModulatorValue:
        moon_sign = self._sign_for(positions, "moon")
        saturn_sign = self._sign_for(positions, "saturn")
        value = 50.0
        value += score_from_sign(moon_sign, STRESS_MOON)
        value += score_from_sign(saturn_sign, STRESS_SATURN)
        if mode != "precise":
            value -= 5.0
        confidence = "high" if moon_sign and saturn_sign and mode == "precise" else "medium" if moon_sign else "low"
        return models.ModulatorValue(modulator_id="M1", value=clamp(value, 0.0, 100.0), confidence=confidence)

    def _modulator_adaptation(self, positions: Dict[str, Dict[str, Any]]) -> models.ModulatorValue:
        counts = self._modality_counts(positions, PRIMARY_MODALITY_BODIES)
        total = sum(counts.values())
        value = 50.0
        if total:
            cardinal_ratio = counts["cardinal"] / total
            fixed_ratio = counts["fixed"] / total
            value += (cardinal_ratio - fixed_ratio) * 60
        mercury_sign = self._sign_for(positions, "mercury")
        value += score_from_sign(mercury_sign, ADAPTATION_MERCURY)
        confidence = "high" if total >= 3 else "medium"
        return models.ModulatorValue(modulator_id="M2", value=clamp(value, 0.0, 100.0), confidence=confidence)

    def _modulator_reflection(self, positions: Dict[str, Dict[str, Any]]) -> models.ModulatorValue:
        mercury_sign = self._sign_for(positions, "mercury")
        saturn_sign = self._sign_for(positions, "saturn")
        value = 50.0
        value += score_from_sign(mercury_sign, REFLECTION_MERCURY)
        value += score_from_sign(saturn_sign, REFLECTION_SATURN)
        if mercury_sign and saturn_sign:
            confidence = "high"
        elif mercury_sign or saturn_sign:
            confidence = "medium"
        else:
            confidence = "low"
        return models.ModulatorValue(modulator_id="M3", value=clamp(value, 0.0, 100.0), confidence=confidence)

    def _modulator_pressure(
        self,
        positions: Dict[str, Dict[str, Any]],
        houses: Dict[str, Any],
        mode: str,
    ) -> models.ModulatorValue:
        saturn_sign = self._sign_for(positions, "saturn")
        value = 50.0
        value += score_from_sign(saturn_sign, PRESSURE_SATURN)
        house10_sign = self._house_sign(houses, "house_10")
        house6_sign = self._house_sign(houses, "house_6")
        value += score_from_sign(house10_sign, PRESSURE_HOUSE)
        value += score_from_sign(house6_sign, PRESSURE_HOUSE) * 0.5
        confidence = "high" if mode == "precise" and (house10_sign or house6_sign) else "medium"
        return models.ModulatorValue(modulator_id="M4", value=clamp(value, 0.0, 100.0), confidence=confidence)

    def _index_positions(self, raw_positions: Iterable[Any]) -> Dict[str, Dict[str, Any]]:
        indexed: Dict[str, Dict[str, Any]] = {}
        for entry in raw_positions or []:
            if hasattr(entry, "model_dump"):
                data = entry.model_dump()
            elif hasattr(entry, "dict"):
                data = entry.dict()
            else:
                data = dict(entry)
            body = data.get("body")
            if not body:
                continue
            indexed[body] = data
        return indexed

    @staticmethod
    def _sign_for(positions: Dict[str, Dict[str, Any]], body: str) -> str | None:
        data = positions.get(body)
        if not data:
            return None
        return data.get("sign")

    def _modality_counts(
        self,
        positions: Dict[str, Dict[str, Any]],
        bodies: Iterable[str],
    ) -> Counter:
        counts: Counter = Counter()
        for body in bodies:
            sign = self._sign_for(positions, body)
            modality = modality_for(sign)
            if modality:
                counts[modality] += 1
        return counts

    @staticmethod
    def _house_sign(houses: Dict[str, Any], key: str) -> str | None:
        data = houses.get(key)
        if not data:
            return None
        if isinstance(data, dict):
            return data.get("sign")
        if hasattr(data, "get"):
            return data.get("sign")
        return None
