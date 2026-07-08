"""P1.1 — DayModel v1 interpretation rules (machine-readable, no LLM/UI)."""

from __future__ import annotations

from typing import Any

from todayflow_backend.data.reference_machine_loader import VECTOR_AXIS_KEYS
from todayflow_backend.services.day_model_v1_aggregator import DAY_MODEL_V1_CONTRACT_VERSION

DAY_MODEL_INTERPRETATION_V1_CONTRACT = "day_model_interpretation_v1"

DOMINANCE_THRESHOLD = 0.45
REFLECTION_LIGHT_THRESHOLD = -0.15
LOW_CONFIDENCE_THRESHOLD = 0.5
DEGRADED_CONFIDENCE_MULTIPLIER = 0.5

STRATEGY_VALUES = frozenset(
    {
        "act",
        "reflect",
        "stabilize",
        "simplify",
        "connect",
        "plan",
        "recover",
        "decide",
        "observe",
    }
)

OPPORTUNITY_CLASS_VALUES = frozenset(
    {
        "action_window",
        "planning_window",
        "recovery_window",
        "communication_window",
        "learning_window",
        "completion_window",
    }
)

RISK_CLASS_VALUES = frozenset(
    {
        "overpressure",
        "avoidance",
        "conflict",
        "scattered_focus",
        "emotional_overload",
        "stagnation",
        "impulsivity",
    }
)

TEMPO_INSTRUCTION_VALUES = frozenset({"slow_down", "keep_steady", "move", "accelerate"})

ACTION_MODE_VALUES = frozenset({"plan", "execute", "adapt", "pause"})

REFLECTION_MODE_VALUES = frozenset({"none", "light", "deep"})

PRESSURE_LEVEL_VALUES = frozenset({"low", "medium", "high"})

DAY_MODEL_INTERPRETATION_V1_KEYS = frozenset(
    {
        "contract_version",
        "strategy",
        "opportunity_class",
        "risk_class",
        "tempo_instruction",
        "action_mode",
        "reflection_mode",
        "pressure_level",
        "confidence",
        "degraded",
        "reasons",
    }
)


class DayModelInterpretationError(ValueError):
    """Raised when input is not a valid day_model_v1 payload."""


def _require_day_model_v1(day_model: dict[str, Any]) -> None:
    if day_model.get("contract_version") != DAY_MODEL_V1_CONTRACT_VERSION:
        raise DayModelInterpretationError(
            f"expected contract_version={DAY_MODEL_V1_CONTRACT_VERSION!r}, "
            f"got {day_model.get('contract_version')!r}"
        )
    for key in ("vector", "tempo", "risk", "emotional_load", "confidence"):
        if key not in day_model:
            raise DayModelInterpretationError(f"missing required day_model field: {key}")
    vector = day_model["vector"]
    if set(vector.keys()) != set(VECTOR_AXIS_KEYS):
        raise DayModelInterpretationError("vector must contain all four axes")


def _hit(reasons: list[str], rule_id: str, detail: str) -> None:
    reasons.append(f"{rule_id}:{detail}")


def _derive_action_mode(vector: dict[str, float], action: float, reasons: list[str]) -> str:
    structure = vector["structure_flow"]
    if structure > DOMINANCE_THRESHOLD:
        _hit(reasons, "R-ACTION-MODE", "structure_flow>0.45→plan")
        return "plan"
    if structure < -DOMINANCE_THRESHOLD:
        _hit(reasons, "R-ACTION-MODE", "structure_flow<-0.45→adapt")
        return "adapt"
    if action > DOMINANCE_THRESHOLD:
        _hit(reasons, "R-ACTION-MODE", "action_reflection>0.45→execute")
        return "execute"
    if action < -DOMINANCE_THRESHOLD:
        _hit(reasons, "R-ACTION-MODE", "action_reflection<-0.45→pause")
        return "pause"
    _hit(reasons, "R-ACTION-MODE", "balanced→execute")
    return "execute"


def _derive_strategy(
    vector: dict[str, float],
    *,
    tempo: str,
    risk: str,
    action: float,
    reasons: list[str],
) -> str:
    expansion = vector["expansion_consolidation"]
    self_others = vector["self_others"]

    if action > DOMINANCE_THRESHOLD:
        _hit(reasons, "R-STRATEGY", "action_reflection>0.45→action_dominant")
        if tempo in ("dynamic", "fast") and expansion > 0.25:
            _hit(reasons, "R-STRATEGY", "tempo_active+expansion→decide")
            return "decide"
        if self_others > DOMINANCE_THRESHOLD:
            _hit(reasons, "R-STRATEGY", "self_others>0.45→connect")
            return "connect"
        if expansion < -0.25:
            _hit(reasons, "R-STRATEGY", "expansion<-0.25→simplify")
            return "simplify"
        if vector["structure_flow"] > DOMINANCE_THRESHOLD:
            _hit(reasons, "R-STRATEGY", "structure>0.45→plan")
            return "plan"
        _hit(reasons, "R-STRATEGY", "default_action→act")
        return "act"

    if action < -DOMINANCE_THRESHOLD:
        _hit(reasons, "R-STRATEGY", "action_reflection<-0.45→reflection_dominant")
        if tempo == "slow":
            _hit(reasons, "R-STRATEGY", "tempo_slow→observe")
            return "observe"
        _hit(reasons, "R-STRATEGY", "default_reflection→reflect")
        return "reflect"

    if tempo == "slow" and action < 0:
        _hit(reasons, "R-STRATEGY", "slow+reflection_lean→observe")
        return "observe"
    if action < -0.25:
        _hit(reasons, "R-STRATEGY", "action<-0.25→reflect")
        return "reflect"
    if vector["structure_flow"] > DOMINANCE_THRESHOLD:
        _hit(reasons, "R-STRATEGY", "structure>0.45→plan")
        return "plan"
    if expansion < -0.25:
        _hit(reasons, "R-STRATEGY", "expansion<-0.25→stabilize")
        return "stabilize"
    if risk == "high":
        _hit(reasons, "R-STRATEGY", "risk_high→recover")
        return "recover"
    _hit(reasons, "R-STRATEGY", "balanced→stabilize")
    return "stabilize"


def _derive_opportunity_class(
    vector: dict[str, float],
    *,
    strategy: str,
    tempo: str,
    action: float,
    reasons: list[str],
) -> str:
    if strategy in ("act", "decide") and tempo in ("dynamic", "fast"):
        _hit(reasons, "R-OPPORTUNITY", "strategy_action+tempo→action_window")
        return "action_window"
    if strategy == "plan" or vector["structure_flow"] > DOMINANCE_THRESHOLD:
        _hit(reasons, "R-OPPORTUNITY", "structure/plan→planning_window")
        return "planning_window"
    if strategy == "recover" or strategy == "observe":
        _hit(reasons, "R-OPPORTUNITY", "recover/observe→recovery_window")
        return "recovery_window"
    if strategy == "connect" or vector["self_others"] > DOMINANCE_THRESHOLD:
        _hit(reasons, "R-OPPORTUNITY", "connect/others→communication_window")
        return "communication_window"
    if strategy in ("reflect", "observe"):
        _hit(reasons, "R-OPPORTUNITY", "reflect/observe→learning_window")
        return "learning_window"
    if vector["expansion_consolidation"] < -0.25 or strategy == "simplify":
        _hit(reasons, "R-OPPORTUNITY", "consolidation→completion_window")
        return "completion_window"
    if action > 0.2:
        _hit(reasons, "R-OPPORTUNITY", "default→action_window")
        return "action_window"
    _hit(reasons, "R-OPPORTUNITY", "default→planning_window")
    return "planning_window"


def _derive_risk_class(
    vector: dict[str, float],
    *,
    tempo: str,
    risk: str,
    emotional_load: str,
    action: float,
    reasons: list[str],
) -> str:
    if risk == "high" and emotional_load == "intense":
        _hit(reasons, "R-RISK", "high+intense→emotional_overload")
        return "emotional_overload"
    if risk == "high" and tempo in ("fast", "dynamic") and action > DOMINANCE_THRESHOLD:
        _hit(reasons, "R-RISK", "high+fast_action→impulsivity")
        return "impulsivity"
    if risk == "high" and action < -0.15:
        _hit(reasons, "R-RISK", "high+reflection_lean→avoidance")
        return "avoidance"
    if risk == "high":
        _hit(reasons, "R-RISK", "risk_high→overpressure")
        return "overpressure"
    if emotional_load == "intense" and tempo == "fast":
        _hit(reasons, "R-RISK", "intense+fast→scattered_focus")
        return "scattered_focus"
    expansion = vector["expansion_consolidation"]
    if tempo == "slow" and action < -0.15 and expansion < 0:
        _hit(reasons, "R-RISK", "slow+reflection→stagnation")
        return "stagnation"
    if abs(vector["structure_flow"]) < 0.15 and abs(action) < 0.15:
        _hit(reasons, "R-RISK", "weak_vector→scattered_focus")
        return "scattered_focus"
    if emotional_load == "intense":
        _hit(reasons, "R-RISK", "intense→conflict")
        return "conflict"
    _hit(reasons, "R-RISK", "default→stagnation")
    return "stagnation"


def _derive_tempo_instruction(tempo: str, action: float, reasons: list[str]) -> str:
    if tempo == "slow" and action < 0:
        _hit(reasons, "R-TEMPO", "slow+reflection→slow_down")
        return "slow_down"
    if tempo == "slow":
        _hit(reasons, "R-TEMPO", "slow→slow_down")
        return "slow_down"
    if tempo == "fast" and action > DOMINANCE_THRESHOLD:
        _hit(reasons, "R-TEMPO", "fast+action→accelerate")
        return "accelerate"
    if tempo == "fast":
        _hit(reasons, "R-TEMPO", "fast→move")
        return "move"
    if tempo == "dynamic" and action > DOMINANCE_THRESHOLD:
        _hit(reasons, "R-TEMPO", "dynamic+action→move")
        return "move"
    if tempo == "steady":
        _hit(reasons, "R-TEMPO", "steady→keep_steady")
        return "keep_steady"
    _hit(reasons, "R-TEMPO", "default→keep_steady")
    return "keep_steady"


def _derive_reflection_mode(action: float, reasons: list[str]) -> str:
    if action < -DOMINANCE_THRESHOLD:
        _hit(reasons, "R-REFLECTION", "action<-0.45→deep")
        return "deep"
    if action < REFLECTION_LIGHT_THRESHOLD:
        _hit(reasons, "R-REFLECTION", "action<-0.15→light")
        return "light"
    _hit(reasons, "R-REFLECTION", "action_neutral→none")
    return "none"


def _derive_pressure_level(risk: str, emotional_load: str, reasons: list[str]) -> str:
    if risk == "high" and emotional_load == "intense":
        _hit(reasons, "R-PRESSURE", "high+intense→low_caution")
        return "low"
    if risk == "medium" and emotional_load == "intense":
        _hit(reasons, "R-PRESSURE", "medium+intense→low_caution")
        return "low"
    if risk == "high":
        _hit(reasons, "R-PRESSURE", "risk_high→medium")
        return "medium"
    if risk == "medium":
        _hit(reasons, "R-PRESSURE", "risk_medium→medium")
        return "medium"
    _hit(reasons, "R-PRESSURE", "risk_low→high")
    return "high"


def _adjust_confidence(day_model: dict[str, Any], reasons: list[str]) -> tuple[float, bool]:
    confidence = float(day_model["confidence"])
    degraded = bool(day_model.get("degraded", False))
    if degraded:
        confidence = round(confidence * DEGRADED_CONFIDENCE_MULTIPLIER, 2)
        _hit(reasons, "R-CONFIDENCE", "day_model.degraded→halve")
    if confidence < LOW_CONFIDENCE_THRESHOLD:
        _hit(reasons, "R-CONFIDENCE", f"confidence<{LOW_CONFIDENCE_THRESHOLD}→degraded")
        degraded = True
    return confidence, degraded


def interpret_day_model_v1(day_model: dict[str, Any]) -> dict[str, Any]:
    """
    P1.1 — map aggregated day_model_v1 to machine-readable interpretation.

    Input: only day_model_v1 (from aggregate_day_model_v1). No LLM, check-in, behavior, or prose.
    """
    _require_day_model_v1(day_model)
    reasons: list[str] = []

    vector = day_model["vector"]
    action = float(vector["action_reflection"])
    tempo = str(day_model["tempo"])
    risk = str(day_model["risk"])
    emotional_load = str(day_model["emotional_load"])

    strategy = _derive_strategy(vector, tempo=tempo, risk=risk, action=action, reasons=reasons)
    action_mode = _derive_action_mode(vector, action, reasons)
    opportunity_class = _derive_opportunity_class(
        vector, strategy=strategy, tempo=tempo, action=action, reasons=reasons
    )
    risk_class = _derive_risk_class(
        vector,
        tempo=tempo,
        risk=risk,
        emotional_load=emotional_load,
        action=action,
        reasons=reasons,
    )
    tempo_instruction = _derive_tempo_instruction(tempo, action, reasons)
    reflection_mode = _derive_reflection_mode(action, reasons)
    pressure_level = _derive_pressure_level(risk, emotional_load, reasons)
    confidence, degraded = _adjust_confidence(day_model, reasons)

    return {
        "contract_version": DAY_MODEL_INTERPRETATION_V1_CONTRACT,
        "strategy": strategy,
        "opportunity_class": opportunity_class,
        "risk_class": risk_class,
        "tempo_instruction": tempo_instruction,
        "action_mode": action_mode,
        "reflection_mode": reflection_mode,
        "pressure_level": pressure_level,
        "confidence": confidence,
        "degraded": degraded,
        "reasons": reasons,
    }
