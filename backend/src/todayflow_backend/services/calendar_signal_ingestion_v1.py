"""E1.2 — Calendar signal ingestion (verified artifacts → calendar_day_record_v1 marks/refs)."""

from __future__ import annotations

import copy
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from todayflow_backend.services.calendar_day_record_v1 import (
    ALLOWED_DAY_TYPE_LABELS,
    CALENDAR_DAY_RECORD_V1_CONTRACT,
    build_completion_mark_ref_v1,
    validate_calendar_day_record_v1,
)
from todayflow_backend.services.day_model_v1_hint_application import compute_state_snapshot_hash
from todayflow_backend.services.practice_runtime_event_v1 import PRACTICE_RUNTIME_EVENT_V1_CONTRACT
from todayflow_backend.services.progression_signal_v1 import (
    PROGRESSION_SIGNAL_V1_CONTRACT,
    VERIFICATION_STATUS_VERIFIED,
)

CALENDAR_SIGNAL_INGESTION_V1_VERSION = "1.0.0"

CALENDAR_SIGNAL_INGESTION_RESULT_V1_CONTRACT = "calendar_signal_ingestion_result_v1"

MUTATION_SCOPE_CALENDAR_DAY_RECORD_ONLY = "calendar_day_record_only"

SOURCE_PROGRESSION_SIGNAL = "progression_signal"
SOURCE_RUNTIME_EVENT = "runtime_event"
SOURCE_DAYMODEL = "daymodel"
SOURCE_COSMIC = "cosmic"
SOURCE_TRACKING = "tracking"
SOURCE_EVOLUTION_SCORE = "evolution_score"

ALLOWED_SOURCE_ARTIFACT_TYPES = frozenset(
    {
        SOURCE_PROGRESSION_SIGNAL,
        SOURCE_RUNTIME_EVENT,
        SOURCE_DAYMODEL,
        SOURCE_COSMIC,
        SOURCE_TRACKING,
        SOURCE_EVOLUTION_SCORE,
    }
)

MARK_PRACTICE = "practice"
MARK_HABIT = "habit"
MARK_RITUAL = "ritual"
MARK_CYCLE = "cycle"
MARK_GOAL = "goal"
MARK_EVOLUTION = "evolution"
MARK_DAYMODEL = "daymodel"
MARK_COSMIC = "cosmic"
MARK_TRACKING = "tracking"

OPERATION_APPEND = "append"
OPERATION_UPSERT = "upsert"
OPERATION_IGNORE = "ignore"
OPERATION_REJECT = "reject"

ALLOWED_OPERATIONS = frozenset(
    {OPERATION_APPEND, OPERATION_UPSERT, OPERATION_IGNORE, OPERATION_REJECT}
)

SIGNAL_TYPE_TO_COMPLETION_FIELD: dict[str, str] = {
    "practice_completed": "completed_practices",
    "habit_streak_confirmed": "completed_habits",
    "ritual_streak_confirmed": "completed_rituals",
    "cycle_completed": "completed_cycles",
    "weekly_goal_completed": "completed_goals",
    "goal_milestone_reached": "completed_goals",
}

SIGNAL_TYPE_TO_MARK_TYPE: dict[str, str] = {
    "practice_completed": MARK_PRACTICE,
    "habit_streak_confirmed": MARK_HABIT,
    "ritual_streak_confirmed": MARK_RITUAL,
    "cycle_completed": MARK_CYCLE,
    "weekly_goal_completed": MARK_GOAL,
    "goal_milestone_reached": MARK_GOAL,
}

RUNTIME_EVENT_KIND_TO_COMPLETION_FIELD: dict[str, str] = {
    "practice_completed_event": "completed_practices",
    "habit_streak_event": "completed_habits",
    "ritual_streak_event": "completed_rituals",
    "cycle_completion_event": "completed_cycles",
    "goal_progress_event": "completed_goals",
}

RUNTIME_EVENT_KIND_TO_MARK_TYPE: dict[str, str] = {
    "practice_completed_event": MARK_PRACTICE,
    "habit_streak_event": MARK_HABIT,
    "ritual_streak_event": MARK_RITUAL,
    "cycle_completion_event": MARK_CYCLE,
    "goal_progress_event": MARK_GOAL,
}

DAYMODEL_REF_FIELDS = (
    "day_model_snapshot_id",
    "interpretation_id",
    "content_package_id",
)

COSMIC_REF_FIELDS = (
    "tarot_entity_code",
    "numerology_entity_code",
    "astrology_snapshot_ref",
)

TRACKING_FIELDS = (
    "energy_score",
    "mood_score",
    "day_type_labels",
)

FORBIDDEN_SOURCE_ARTIFACT_FIELDS = frozenset(
    {
        "rhythm_pattern",
        "rhythm_pattern_id",
        "pattern_candidate",
        "pattern_confirmation",
        "monthly_summary",
        "month_map",
        "recommendation",
        "recommendation_id",
        "insight",
        "insight_text",
        "llm_output",
        "llm_call",
        "prompt",
        "commerce",
        "evolution_stage",
        "current_stage",
        "promoted_stage",
        "profile",
        "memory",
        "knowledge_candidates",
    }
)

CALENDAR_SIGNAL_INGESTION_RESULT_V1_KEYS = frozenset(
    {
        "contract_version",
        "ingestion_id",
        "record_id",
        "user_id",
        "date",
        "source_artifact_type",
        "source_artifact_id",
        "mark_type",
        "operation",
        "written_paths",
        "ignored_reason",
        "rejected_reason",
        "record_before_hash",
        "record_after_hash",
        "created_at",
        "mutation_scope",
    }
)


class CalendarSignalIngestionError(ValueError):
    """Raised when calendar signal ingestion inputs or payload are invalid."""


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def generate_calendar_signal_ingestion_id() -> str:
    return f"csi-{uuid4()}"


def _record_hash(record: dict[str, Any]) -> str:
    return compute_state_snapshot_hash(record)


def _iso_date_prefix(value: str | None) -> str | None:
    if not value or not isinstance(value, str):
        return None
    if len(value) >= 10 and value[4] == "-" and value[7] == "-":
        return value[:10]
    return None


def _source_artifact_id(source_artifact: dict[str, Any], source_artifact_type: str) -> str:
    if source_artifact_type == SOURCE_PROGRESSION_SIGNAL:
        return str(source_artifact.get("progression_signal_id") or "")
    if source_artifact_type == SOURCE_RUNTIME_EVENT:
        return str(source_artifact.get("event_id") or "")
    if source_artifact_type == SOURCE_EVOLUTION_SCORE:
        return str(source_artifact.get("evolution_score_snapshot_id") or "")
    if source_artifact_type == SOURCE_DAYMODEL:
        return str(
            source_artifact.get("day_model_snapshot_id")
            or source_artifact.get("interpretation_id")
            or source_artifact.get("content_package_id")
            or ""
        )
    if source_artifact_type == SOURCE_COSMIC:
        return str(
            source_artifact.get("tarot_entity_code")
            or source_artifact.get("numerology_entity_code")
            or source_artifact.get("astrology_snapshot_ref")
            or ""
        )
    if source_artifact_type == SOURCE_TRACKING:
        parts = [
            str(source_artifact.get("energy_score")),
            str(source_artifact.get("mood_score")),
            ",".join(source_artifact.get("day_type_labels") or []),
        ]
        return "|".join(parts)
    return ""


def _validate_source_artifact(source_artifact: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(source_artifact, dict):
        return ["source_artifact must be object"]
    forbidden = set(source_artifact.keys()) & FORBIDDEN_SOURCE_ARTIFACT_FIELDS
    if forbidden:
        errors.append(f"forbidden source artifact fields: {sorted(forbidden)}")
    return errors


def _validate_tracking_scores(source_artifact: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field_name in ("energy_score", "mood_score"):
        value = source_artifact.get(field_name)
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errors.append(f"{field_name} must be a number between 0 and 10")
        elif value < 0 or value > 10:
            errors.append(f"{field_name} must be between 0 and 10")
    labels = source_artifact.get("day_type_labels")
    if labels is not None:
        if not isinstance(labels, list):
            errors.append("day_type_labels must be array")
        else:
            for label in labels:
                if label not in ALLOWED_DAY_TYPE_LABELS:
                    errors.append(f"invalid day_type_label: {label!r}")
    return errors


def _mark_exists(
    marks: list[dict[str, Any]],
    *,
    progression_signal_id: str | None = None,
    entity_ref: str | None = None,
) -> bool:
    for mark in marks:
        if progression_signal_id and mark.get("progression_signal_id") == progression_signal_id:
            return True
        if entity_ref and mark.get("entity_ref") == entity_ref:
            if progression_signal_id is None or mark.get("progression_signal_id") == progression_signal_id:
                return True
    return False


def _append_progression_signal_id(record: dict[str, Any], signal_id: str) -> bool:
    ids = record.setdefault("progression_signal_ids", [])
    if signal_id in ids:
        return False
    ids.append(signal_id)
    return True


def _append_completion_mark(
    record: dict[str, Any],
    field_name: str,
    mark: dict[str, Any],
) -> tuple[str, list[str]]:
    marks = record.setdefault(field_name, [])
    signal_id = mark.get("progression_signal_id")
    entity_ref = mark.get("entity_ref")
    if _mark_exists(marks, progression_signal_id=signal_id, entity_ref=entity_ref):
        return OPERATION_IGNORE, []
    marks.append(mark)
    written = [field_name]
    if signal_id and _append_progression_signal_id(record, signal_id):
        written.append("progression_signal_ids")
    return OPERATION_APPEND, written


def _ingest_progression_signal(
    record: dict[str, Any],
    source_artifact: dict[str, Any],
) -> tuple[str, str, list[str], str | None, str | None]:
    if source_artifact.get("contract_version") != PROGRESSION_SIGNAL_V1_CONTRACT:
        return OPERATION_REJECT, MARK_EVOLUTION, [], None, "invalid_progression_signal_contract"

    if source_artifact.get("verification_status") != VERIFICATION_STATUS_VERIFIED:
        return OPERATION_REJECT, MARK_EVOLUTION, [], None, "signal_not_verified"

    if source_artifact.get("user_id") != record.get("user_id"):
        return OPERATION_REJECT, MARK_EVOLUTION, [], None, "user_mismatch"

    observed_date = _iso_date_prefix(source_artifact.get("observed_at"))
    if observed_date and observed_date != record.get("date"):
        return OPERATION_REJECT, MARK_EVOLUTION, [], None, "date_mismatch"

    signal_type = str(source_artifact.get("signal_type") or "")
    signal_id = str(source_artifact.get("progression_signal_id") or "")
    mark_type = SIGNAL_TYPE_TO_MARK_TYPE.get(signal_type, MARK_EVOLUTION)

    completion_field = SIGNAL_TYPE_TO_COMPLETION_FIELD.get(signal_type)
    if completion_field is None:
        if signal_id in (record.get("progression_signal_ids") or []):
            return OPERATION_IGNORE, mark_type, [], "duplicate_progression_signal_id", None
        if _append_progression_signal_id(record, signal_id):
            return OPERATION_APPEND, mark_type, ["progression_signal_ids"], None, None
        return OPERATION_IGNORE, mark_type, [], "duplicate_progression_signal_id", None

    entity_ref = f"{source_artifact.get('source_engine')}:{source_artifact.get('source_event_id')}"
    mark = build_completion_mark_ref_v1(
        entity_ref=entity_ref,
        progression_signal_id=signal_id,
        verified_at=source_artifact.get("verified_at") or source_artifact.get("observed_at"),
    )
    operation, written = _append_completion_mark(record, completion_field, mark)
    ignore_reason = "duplicate_progression_signal_id" if operation == OPERATION_IGNORE else None
    return operation, mark_type, written, ignore_reason, None


def _ingest_runtime_event(
    record: dict[str, Any],
    source_artifact: dict[str, Any],
) -> tuple[str, str, list[str], str | None, str | None]:
    if source_artifact.get("contract_version") != PRACTICE_RUNTIME_EVENT_V1_CONTRACT:
        return OPERATION_REJECT, MARK_PRACTICE, [], None, "invalid_runtime_event_contract"

    if source_artifact.get("verification_status") != VERIFICATION_STATUS_VERIFIED:
        return OPERATION_REJECT, MARK_PRACTICE, [], None, "event_not_verified"

    if source_artifact.get("user_id") != record.get("user_id"):
        return OPERATION_REJECT, MARK_PRACTICE, [], None, "user_mismatch"

    occurred_date = _iso_date_prefix(source_artifact.get("occurred_at"))
    if occurred_date and occurred_date != record.get("date"):
        return OPERATION_REJECT, MARK_PRACTICE, [], None, "date_mismatch"

    event_kind = str(source_artifact.get("event_kind") or "")
    completion_field = RUNTIME_EVENT_KIND_TO_COMPLETION_FIELD.get(event_kind)
    mark_type = RUNTIME_EVENT_KIND_TO_MARK_TYPE.get(event_kind, MARK_PRACTICE)
    if completion_field is None:
        return OPERATION_REJECT, mark_type, [], None, "unsupported_runtime_event_kind"

    entity_ref = (
        f"{source_artifact.get('runtime_entity_type')}:"
        f"{source_artifact.get('definition_code')}:"
        f"{source_artifact.get('event_id')}"
    )
    mark = build_completion_mark_ref_v1(
        entity_ref=entity_ref,
        verified_at=source_artifact.get("occurred_at"),
    )
    operation, written = _append_completion_mark(record, completion_field, mark)
    ignore_reason = "duplicate_runtime_event" if operation == OPERATION_IGNORE else None
    return operation, mark_type, written, ignore_reason, None


def _upsert_scalar_fields(
    record: dict[str, Any],
    source_artifact: dict[str, Any],
    field_names: tuple[str, ...],
) -> list[str]:
    written: list[str] = []
    for field_name in field_names:
        if field_name not in source_artifact:
            continue
        value = source_artifact[field_name]
        if value is None:
            continue
        if field_name == "day_type_labels":
            existing = set(record.get("day_type_labels") or [])
            incoming = [label for label in value if label in ALLOWED_DAY_TYPE_LABELS]
            merged = sorted(existing | set(incoming))
            record["day_type_labels"] = merged
        else:
            record[field_name] = value
        written.append(field_name)
    return written


def _ingest_daymodel(
    record: dict[str, Any],
    source_artifact: dict[str, Any],
) -> tuple[str, str, list[str], str | None, str | None]:
    written = _upsert_scalar_fields(record, source_artifact, DAYMODEL_REF_FIELDS)
    if not written:
        return OPERATION_IGNORE, MARK_DAYMODEL, [], "no_daymodel_refs_provided", None
    return OPERATION_UPSERT, MARK_DAYMODEL, written, None, None


def _ingest_cosmic(
    record: dict[str, Any],
    source_artifact: dict[str, Any],
) -> tuple[str, str, list[str], str | None, str | None]:
    written = _upsert_scalar_fields(record, source_artifact, COSMIC_REF_FIELDS)
    if not written:
        return OPERATION_IGNORE, MARK_COSMIC, [], "no_cosmic_refs_provided", None
    return OPERATION_UPSERT, MARK_COSMIC, written, None, None


def _ingest_tracking(
    record: dict[str, Any],
    source_artifact: dict[str, Any],
) -> tuple[str, str, list[str], str | None, str | None]:
    score_errors = _validate_tracking_scores(source_artifact)
    if score_errors:
        return OPERATION_REJECT, MARK_TRACKING, [], None, score_errors[0]

    written = _upsert_scalar_fields(record, source_artifact, TRACKING_FIELDS)
    if not written:
        return OPERATION_IGNORE, MARK_TRACKING, [], "no_tracking_fields_provided", None
    return OPERATION_UPSERT, MARK_TRACKING, written, None, None


def _ingest_evolution_score(
    record: dict[str, Any],
    source_artifact: dict[str, Any],
) -> tuple[str, str, list[str], str | None, str | None]:
    snapshot_id = source_artifact.get("evolution_score_snapshot_id")
    if not snapshot_id:
        return OPERATION_REJECT, MARK_EVOLUTION, [], None, "missing_evolution_score_snapshot_id"

    if source_artifact.get("user_id") and source_artifact.get("user_id") != record.get("user_id"):
        return OPERATION_REJECT, MARK_EVOLUTION, [], None, "user_mismatch"

    if record.get("evolution_score_snapshot_id") == snapshot_id:
        return OPERATION_IGNORE, MARK_EVOLUTION, [], "duplicate_evolution_score_snapshot_id", None

    record["evolution_score_snapshot_id"] = snapshot_id
    return OPERATION_UPSERT, MARK_EVOLUTION, ["evolution_score_snapshot_id"], None, None


def build_calendar_signal_ingestion_result_v1(
    *,
    record: dict[str, Any],
    source_artifact_type: str,
    source_artifact: dict[str, Any],
    operation: str,
    mark_type: str,
    written_paths: list[str],
    record_before_hash: str,
    record_after_hash: str,
    ignored_reason: str | None = None,
    rejected_reason: str | None = None,
    ingestion_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    result = {
        "contract_version": CALENDAR_SIGNAL_INGESTION_RESULT_V1_CONTRACT,
        "ingestion_id": ingestion_id or generate_calendar_signal_ingestion_id(),
        "record_id": record.get("record_id"),
        "user_id": record.get("user_id"),
        "date": record.get("date"),
        "source_artifact_type": source_artifact_type,
        "source_artifact_id": _source_artifact_id(source_artifact, source_artifact_type),
        "mark_type": mark_type,
        "operation": operation,
        "written_paths": written_paths,
        "ignored_reason": ignored_reason,
        "rejected_reason": rejected_reason,
        "record_before_hash": record_before_hash,
        "record_after_hash": record_after_hash,
        "created_at": created_at or _utc_now_iso(),
        "mutation_scope": MUTATION_SCOPE_CALENDAR_DAY_RECORD_ONLY,
    }
    errors = validate_calendar_signal_ingestion_result_v1(result)
    if errors:
        raise CalendarSignalIngestionError("; ".join(errors))
    return result


def ingest_calendar_signal_v1(
    calendar_day_record: dict[str, Any],
    *,
    source_artifact: dict[str, Any],
    source_artifact_type: str,
    ingestion_id: str | None = None,
    created_at: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Ingest a verified source artifact into calendar_day_record_v1.

    Ingestion writes marks/refs only — no interpretations, patterns, or recommendations.
    """
    if calendar_day_record.get("contract_version") != CALENDAR_DAY_RECORD_V1_CONTRACT:
        raise CalendarSignalIngestionError("invalid calendar_day_record contract_version")

    record_errors = validate_calendar_day_record_v1(calendar_day_record)
    if record_errors:
        raise CalendarSignalIngestionError("; ".join(record_errors[:8]))

    if source_artifact_type not in ALLOWED_SOURCE_ARTIFACT_TYPES:
        raise CalendarSignalIngestionError(f"unsupported source_artifact_type: {source_artifact_type!r}")

    artifact_errors = _validate_source_artifact(source_artifact)
    if artifact_errors:
        raise CalendarSignalIngestionError("; ".join(artifact_errors))

    before_hash = _record_hash(calendar_day_record)
    updated = copy.deepcopy(calendar_day_record)

    if source_artifact_type == SOURCE_PROGRESSION_SIGNAL:
        operation, mark_type, written, ignored, rejected = _ingest_progression_signal(
            updated, source_artifact
        )
    elif source_artifact_type == SOURCE_RUNTIME_EVENT:
        operation, mark_type, written, ignored, rejected = _ingest_runtime_event(
            updated, source_artifact
        )
    elif source_artifact_type == SOURCE_DAYMODEL:
        operation, mark_type, written, ignored, rejected = _ingest_daymodel(updated, source_artifact)
    elif source_artifact_type == SOURCE_COSMIC:
        operation, mark_type, written, ignored, rejected = _ingest_cosmic(updated, source_artifact)
    elif source_artifact_type == SOURCE_TRACKING:
        operation, mark_type, written, ignored, rejected = _ingest_tracking(updated, source_artifact)
    else:
        operation, mark_type, written, ignored, rejected = _ingest_evolution_score(
            updated, source_artifact
        )

    if operation in {OPERATION_APPEND, OPERATION_UPSERT}:
        updated["updated_at"] = created_at or _utc_now_iso()

    after_hash = _record_hash(updated)

    if operation != OPERATION_REJECT:
        post_errors = validate_calendar_day_record_v1(updated)
        if post_errors:
            raise CalendarSignalIngestionError("; ".join(post_errors[:8]))

    result = build_calendar_signal_ingestion_result_v1(
        record=updated if operation != OPERATION_REJECT else calendar_day_record,
        source_artifact_type=source_artifact_type,
        source_artifact=source_artifact,
        operation=operation,
        mark_type=mark_type,
        written_paths=written,
        record_before_hash=before_hash,
        record_after_hash=after_hash if operation != OPERATION_REJECT else before_hash,
        ignored_reason=ignored,
        rejected_reason=rejected,
        ingestion_id=ingestion_id,
        created_at=created_at,
    )

    if operation == OPERATION_REJECT:
        return calendar_day_record, result

    return updated, result


def validate_calendar_signal_ingestion_result_v1(result: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if result.get("contract_version") != CALENDAR_SIGNAL_INGESTION_RESULT_V1_CONTRACT:
        errors.append("invalid contract_version")

    for key in CALENDAR_SIGNAL_INGESTION_RESULT_V1_KEYS:
        if key not in result:
            errors.append(f"missing field: {key}")

    if result.get("operation") not in ALLOWED_OPERATIONS:
        errors.append("invalid operation")

    if result.get("mutation_scope") != MUTATION_SCOPE_CALENDAR_DAY_RECORD_ONLY:
        errors.append("mutation_scope must be calendar_day_record_only")

    if not isinstance(result.get("written_paths"), list):
        errors.append("written_paths must be array")

    if not result.get("record_before_hash"):
        errors.append("record_before_hash required")
    if not result.get("record_after_hash"):
        errors.append("record_after_hash required")

    operation = result.get("operation")
    if operation == OPERATION_IGNORE and not result.get("ignored_reason"):
        errors.append("ignored_reason required when operation is ignore")
    if operation == OPERATION_REJECT and not result.get("rejected_reason"):
        errors.append("rejected_reason required when operation is reject")

    forbidden = set(result.keys()) & FORBIDDEN_SOURCE_ARTIFACT_FIELDS
    if forbidden:
        errors.append(f"forbidden result fields: {sorted(forbidden)}")

    return errors
