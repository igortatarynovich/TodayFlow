"""Load Reference Layer machine contracts from DATA/reference (P0.4)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

# Monorepo: DATA/ at repository root.
DEFAULT_DATA_ROOT = Path(__file__).resolve().parents[4] / "DATA"
DATA_ROOT = Path(os.getenv("TODAYFLOW_DATA_DIR", DEFAULT_DATA_ROOT))
REFERENCE_ROOT = DATA_ROOT / "reference"
TAROT_MAJOR_MACHINE_DIR = REFERENCE_ROOT / "tarot" / "machine"
NUMEROLOGY_MACHINE_DIR = REFERENCE_ROOT / "numerology" / "machine"
ASTROLOGY_MACHINE_DIR = REFERENCE_ROOT / "astrology" / "machine"

ALLOWED_MACHINE_STATUSES = frozenset({"draft", "review", "active"})
EXPECTED_TAROT_MAJOR_COUNT = 22
EXPECTED_NUMEROLOGY_CORE_COUNT = 9
EXPECTED_NUMEROLOGY_MASTER_COUNT = 3
EXPECTED_NUMEROLOGY_PERSONAL_CYCLE_COUNT = 9
EXPECTED_NUMEROLOGY_MACHINE_COUNT = (
    EXPECTED_NUMEROLOGY_CORE_COUNT
    + EXPECTED_NUMEROLOGY_MASTER_COUNT
    + 3 * EXPECTED_NUMEROLOGY_PERSONAL_CYCLE_COUNT
)
EXPECTED_ASTROLOGY_SIGN_COUNT = 12
EXPECTED_ASTROLOGY_PLANET_COUNT = 10
EXPECTED_ASTROLOGY_HOUSE_COUNT = 12
EXPECTED_ASTROLOGY_ASPECT_COUNT = 5
EXPECTED_ASTROLOGY_MACHINE_COUNT = (
    EXPECTED_ASTROLOGY_SIGN_COUNT
    + EXPECTED_ASTROLOGY_PLANET_COUNT
    + EXPECTED_ASTROLOGY_HOUSE_COUNT
    + EXPECTED_ASTROLOGY_ASPECT_COUNT
)
ASTROLOGY_ATOMIC_ENTITY_TYPES = frozenset({"ZodiacSign", "Planet", "House", "Aspect"})
FORBIDDEN_ASTROLOGY_ENTITY_CODE_PREFIXES = (
    "astrology.planet_in_sign.",
    "astrology.planet_in_house.",
    "astrology.transit.",
    "astrology.aspect_pair.",
    "astrology.foundation.",
)

VECTOR_AXIS_KEYS = (
    "action_reflection",
    "expansion_consolidation",
    "self_others",
    "structure_flow",
)
TEMPO_VALUES = frozenset({"slow", "steady", "dynamic", "fast"})
RISK_VALUES = frozenset({"low", "medium", "high"})
EMOTIONAL_LOAD_VALUES = frozenset({"calm", "neutral", "intense"})


class ReferenceMachineError(Exception):
    """Base error for reference machine loader."""


class ReferenceMachineNotFoundError(ReferenceMachineError):
    """Raised when no machine record matches domain + entity_code."""

    def __init__(self, domain: str, entity_code: str) -> None:
        self.domain = domain
        self.entity_code = entity_code
        super().__init__(f"Reference machine record not found: domain={domain!r} entity_code={entity_code!r}")


class ReferenceMachineValidationError(ReferenceMachineError):
    """Raised when a record fails structural validation."""


@dataclass(frozen=True)
class VectorAxes:
    action_reflection: float
    expansion_consolidation: float
    self_others: float
    structure_flow: float

    def as_dict(self) -> dict[str, float]:
        return {
            "action_reflection": self.action_reflection,
            "expansion_consolidation": self.expansion_consolidation,
            "self_others": self.self_others,
            "structure_flow": self.structure_flow,
        }


@dataclass(frozen=True)
class ReferenceMachineContract:
    """Normalized machine slice used by DayModel v1 preview (tarot-only P0.4)."""

    vector: VectorAxes
    tempo: str
    risk: str
    risk_modifier: float
    emotional_load: str
    confidence: float


@dataclass(frozen=True)
class ReferenceMachineRecord:
    contract_version: str
    domain: str
    entity_code: str
    version: str
    status: str
    machine_contract: ReferenceMachineContract

    @property
    def source_id(self) -> str:
        return self.entity_code


def _require_float_in_range(value: Any, *, field: str, lo: float, hi: float) -> float:
    if not isinstance(value, (int, float)):
        raise ReferenceMachineValidationError(f"{field} must be a number, got {type(value).__name__}")
    num = float(value)
    if num < lo or num > hi:
        raise ReferenceMachineValidationError(f"{field} must be in [{lo}, {hi}], got {num}")
    return num


def _parse_vector(raw: Any, *, path: str) -> VectorAxes:
    if not isinstance(raw, dict):
        raise ReferenceMachineValidationError(f"{path} must be an object")
    axes: dict[str, float] = {}
    for key in VECTOR_AXIS_KEYS:
        if key not in raw:
            raise ReferenceMachineValidationError(f"{path}.{key} is required")
        axes[key] = _require_float_in_range(raw[key], field=f"{path}.{key}", lo=-1.0, hi=1.0)
    return VectorAxes(**axes)


def _parse_machine_contract(raw: Any) -> ReferenceMachineContract:
    if not isinstance(raw, dict):
        raise ReferenceMachineValidationError("machine_contract must be an object")
    vector = _parse_vector(raw.get("vector"), path="machine_contract.vector")
    tempo = raw.get("tempo")
    if tempo not in TEMPO_VALUES:
        raise ReferenceMachineValidationError(f"machine_contract.tempo invalid: {tempo!r}")
    risk = raw.get("risk")
    if risk not in RISK_VALUES:
        raise ReferenceMachineValidationError(f"machine_contract.risk invalid: {risk!r}")
    emotional_load = raw.get("emotional_load")
    if emotional_load not in EMOTIONAL_LOAD_VALUES:
        raise ReferenceMachineValidationError(f"machine_contract.emotional_load invalid: {emotional_load!r}")
    risk_modifier = _require_float_in_range(
        raw.get("risk_modifier"), field="machine_contract.risk_modifier", lo=-1.0, hi=1.0
    )
    confidence = _require_float_in_range(
        raw.get("confidence"), field="machine_contract.confidence", lo=0.0, hi=1.0
    )
    return ReferenceMachineContract(
        vector=vector,
        tempo=str(tempo),
        risk=str(risk),
        risk_modifier=risk_modifier,
        emotional_load=str(emotional_load),
        confidence=confidence,
    )


def _parse_record(payload: dict[str, Any]) -> ReferenceMachineRecord:
    for key in ("contract_version", "domain", "entity_code", "version", "status", "machine_contract"):
        if key not in payload:
            raise ReferenceMachineValidationError(f"Missing required field: {key}")
    if payload["contract_version"] != "reference_machine_contract_v1":
        raise ReferenceMachineValidationError(
            f"Unsupported contract_version: {payload['contract_version']!r}"
        )
    return ReferenceMachineRecord(
        contract_version=str(payload["contract_version"]),
        domain=str(payload["domain"]),
        entity_code=str(payload["entity_code"]),
        version=str(payload["version"]),
        status=str(payload["status"]),
        machine_contract=_parse_machine_contract(payload["machine_contract"]),
    )


def _iter_json_files(directory: Path) -> Iterable[Path]:
    if not directory.is_dir():
        raise ReferenceMachineError(f"Reference machine directory missing: {directory}")
    yield from sorted(directory.glob("*.json"))


def _load_json_file(path: Path) -> ReferenceMachineRecord:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ReferenceMachineValidationError(f"{path.name}: root must be an object")
    return _parse_record(payload)


def _assert_atomic_astrology_record(record: ReferenceMachineRecord, *, path: str) -> None:
    if record.domain != "astrology":
        return
    for prefix in FORBIDDEN_ASTROLOGY_ENTITY_CODE_PREFIXES:
        if record.entity_code.startswith(prefix):
            raise ReferenceMachineValidationError(
                f"{path}: composite astrology entity_code forbidden in Reference Layer: {record.entity_code!r}"
            )


def _machine_dir_for_domain(domain: str) -> Path:
    if domain == "tarot":
        return TAROT_MAJOR_MACHINE_DIR
    if domain == "numerology":
        return NUMEROLOGY_MACHINE_DIR
    if domain == "astrology":
        return ASTROLOGY_MACHINE_DIR
    raise ReferenceMachineError(f"Unsupported reference machine domain: {domain!r}")


def _load_astrology_json_file(path: Path) -> ReferenceMachineRecord:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ReferenceMachineValidationError(f"{path.name}: root must be an object")
    entity_type = payload.get("entity_type")
    if entity_type not in ASTROLOGY_ATOMIC_ENTITY_TYPES:
        raise ReferenceMachineValidationError(
            f"{path.name}: entity_type must be one of {sorted(ASTROLOGY_ATOMIC_ENTITY_TYPES)}, got {entity_type!r}"
        )
    record = _parse_record(payload)
    _assert_atomic_astrology_record(record, path=path.name)
    return record


@lru_cache(maxsize=1)
def load_astrology_machine_contracts(
    *,
    allowed_statuses: frozenset[str] | None = None,
) -> tuple[ReferenceMachineRecord, ...]:
    """Load atomic astrology machine drafts from DATA/reference/astrology/machine/ (P0.8)."""
    statuses = allowed_statuses or ALLOWED_MACHINE_STATUSES
    records: list[ReferenceMachineRecord] = []
    for path in _iter_json_files(ASTROLOGY_MACHINE_DIR):
        record = _load_astrology_json_file(path)
        if record.status not in statuses:
            continue
        records.append(record)
    records.sort(key=lambda r: r.entity_code)
    return tuple(records)


@lru_cache(maxsize=1)
def load_numerology_machine_contracts(
    *,
    allowed_statuses: frozenset[str] | None = None,
) -> tuple[ReferenceMachineRecord, ...]:
    """Load all numerology machine drafts from DATA/reference/numerology/machine/."""
    statuses = allowed_statuses or ALLOWED_MACHINE_STATUSES
    records: list[ReferenceMachineRecord] = []
    for path in _iter_json_files(NUMEROLOGY_MACHINE_DIR):
        record = _load_json_file(path)
        if record.domain != "numerology":
            raise ReferenceMachineValidationError(f"{path.name}: domain must be numerology")
        if record.status not in statuses:
            continue
        records.append(record)
    records.sort(key=lambda r: r.entity_code)
    return tuple(records)


@lru_cache(maxsize=1)
def load_tarot_major_machine_contracts(
    *,
    allowed_statuses: frozenset[str] | None = None,
) -> tuple[ReferenceMachineRecord, ...]:
    """Load all tarot major machine drafts from DATA/reference/tarot/machine/."""
    statuses = allowed_statuses or ALLOWED_MACHINE_STATUSES
    records: list[ReferenceMachineRecord] = []
    for path in _iter_json_files(TAROT_MAJOR_MACHINE_DIR):
        record = _load_json_file(path)
        if record.domain != "tarot":
            raise ReferenceMachineValidationError(f"{path.name}: domain must be tarot")
        if record.status not in statuses:
            continue
        records.append(record)
    records.sort(key=lambda r: r.entity_code)
    return tuple(records)


def load_reference_machine_contract(
    domain: str,
    entity_code: str,
    *,
    allowed_statuses: frozenset[str] | None = None,
) -> ReferenceMachineRecord:
    """Load one machine record by domain and entity_code."""
    statuses = allowed_statuses or ALLOWED_MACHINE_STATUSES
    directory = _machine_dir_for_domain(domain)
    for path in _iter_json_files(directory):
        if domain == "astrology":
            record = _load_astrology_json_file(path)
        else:
            record = _load_json_file(path)
        if record.domain == domain and record.entity_code == entity_code:
            if record.status not in statuses:
                raise ReferenceMachineNotFoundError(domain, entity_code)
            return record
    raise ReferenceMachineNotFoundError(domain, entity_code)


def clear_reference_machine_cache() -> None:
    """Test helper: reset cached reference machine loads."""
    load_tarot_major_machine_contracts.cache_clear()
    load_numerology_machine_contracts.cache_clear()
    load_astrology_machine_contracts.cache_clear()
