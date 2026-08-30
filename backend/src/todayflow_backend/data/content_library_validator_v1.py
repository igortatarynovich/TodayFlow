"""Validate Practice Content Library items against taxonomy + coverage ledger."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PAYLOAD_LOGIC_MARKERS = (
    "item_id",
    "content_class",
    "semantic_version",
    "need.",
    "purpose",
    "direction",
    "retrieval",
    "input_state",
    "content-taxonomy",
    "seed_cell",
    "technique_id",
)

IDENTITY_REQUIRED = ("item_id", "content_class", "type", "status", "semantic_version")
RETRIEVAL_REQUIRED = (
    "purpose",
    "input_state",
    "direction",
    "intensity",
    "energy_effect",
    "context",
    "delivery",
)
PAYLOAD_REQUIRED = ("body_kind", "locales")
DISCIPLINE_RETRIEVAL_EXTRA = (
    "duration_days",
    "frequency",
    "difficulty",
    "failure_policy",
    "check_in_frequency",
)
DISCIPLINE_PAYLOAD_EXTRA = (
    "commitment_rule",
    "restriction",
    "start_condition",
    "completion_condition",
)
ALLOWED_STATUS = frozenset({"draft", "active", "retired"})
TECHNIQUE_ID_PREFIX = "technique."
ARCHITECTURE_PROBE_COUNT = 16
ALLOWED_SOURCE_FAMILY = frozenset(
    {
        "clinical_psychology",
        "mindfulness_protocol",
        "behavioral_science",
        "official_health",
        "academic_description",
        "recognized_school",
        "tradition_primary",
        "historical_philosophical",
    }
)
ALLOWED_EVIDENCE_LEVEL = frozenset(
    {
        "unverified",
        "tradition_attested",
        "protocol_attested",
        "academic_described",
        "product_only",
    }
)
ALLOWED_EFFICACY_CLAIM_LEVEL = frozenset(
    {"not_claimed", "anecdote", "single_study", "review", "guideline"}
)
ALLOWED_TECHNIQUE_REVIEW_STATUS = frozenset(
    {
        "empty",
        "landscape",
        "extracted",
        "normalized",
        "safety_reviewed",
        "canonical",
        "rejected",
    }
)
ALLOWED_CLAIM_RISK = frozenset(
    {
        "none_until_ingest",
        "product_only",
        "likely_invention",
        "construct_mismatch",
        "family_collapse",
        "medical_protocol_bleed",
        "manifestation",
        "efficacy_bleed",
    }
)
LANDSCAPE_REQUIRED = (
    "family_id",
    "candidate_family",
    "content_class",
    "candidate_types",
    "mechanism_shape",
    "bounds_to_research",
    "variant_axes",
    "source_families",
    "claim_risk",
    "probe_links",
    "shortlist_status",
)
LANDSCAPE_CONTENT_CLASS = frozenset(
    {"practice", "meditation", "affirmation", "discipline"}
)
TECHNIQUE_REQUIRED = (
    "technique_id",
    "content_class",
    "type",
    "canonical_description",
    "source_refs",
    "safety_notes",
    "allowed_claims",
    "status",
)
ALLOWED_TECHNIQUE_STATUS = frozenset({"accepted", "skipped"})
ALLOWED_BODY_KIND = frozenset(
    {"instruction", "script", "affirmation_text", "commitment_rule"}
)
CELL_STATUS_FOR_ITEMS = {"seed", "covered"}


def _as_str_list(value: Any, *, allow_empty: bool = True) -> list[str] | None:
    if not isinstance(value, list):
        return None
    if not value and not allow_empty:
        return None
    if not all(isinstance(x, str) and x.strip() for x in value):
        return None
    return [str(x) for x in value]


def _payload_text(payload: dict[str, Any]) -> str:
    chunks: list[str] = []
    locales = payload.get("locales")
    if isinstance(locales, dict):
        for loc in locales.values():
            if isinstance(loc, dict):
                chunks.append(str(loc.get("title") or ""))
                chunks.append(str(loc.get("body") or ""))
    presentation = payload.get("presentation")
    if isinstance(presentation, dict):
        chunks.append(json.dumps(presentation, ensure_ascii=False))
    for key in DISCIPLINE_PAYLOAD_EXTRA:
        value = payload.get(key)
        if isinstance(value, str):
            chunks.append(value)
    exceptions = payload.get("allowed_exceptions")
    if isinstance(exceptions, list):
        chunks.extend(str(x) for x in exceptions if x is not None)
    return " ".join(chunks).lower()


def validate_content_item_v1(
    item: dict[str, Any],
    *,
    vocab: dict[str, Any],
    prefix: str,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(item, dict):
        return [f"{prefix}: must be object"]

    identity = item.get("identity")
    retrieval = item.get("retrieval")
    payload = item.get("payload")
    if not isinstance(identity, dict):
        errors.append(f"{prefix}: identity must be object")
        return errors
    if not isinstance(retrieval, dict):
        errors.append(f"{prefix}: retrieval must be object")
        return errors
    if not isinstance(payload, dict):
        errors.append(f"{prefix}: payload must be object")
        return errors

    for key in IDENTITY_REQUIRED:
        if key not in identity:
            errors.append(f"{prefix}: identity missing {key}")
    item_id = identity.get("item_id")
    if not isinstance(item_id, str) or not item_id.strip():
        errors.append(f"{prefix}: identity.item_id must be non-empty string")

    content_class = identity.get("content_class")
    types_by_class = vocab.get("types") or {}
    class_types = {
        row["code"]: row
        for row in types_by_class.get(content_class, [])
        if isinstance(row, dict) and row.get("code")
    }
    if content_class not in types_by_class:
        errors.append(f"{prefix}: invalid content_class {content_class!r}")

    type_code = identity.get("type")
    type_row = class_types.get(type_code) if isinstance(type_code, str) else None
    if type_row is None:
        errors.append(f"{prefix}: type {type_code!r} not in vocab for {content_class!r}")

    family = identity.get("family")
    if content_class == "practice":
        if not isinstance(family, str) or not family:
            errors.append(f"{prefix}: practice requires identity.family")
        elif type_row is not None and type_row.get("family") != family:
            errors.append(
                f"{prefix}: family {family!r} does not match type {type_code!r}"
            )
    elif family not in (None,):
        errors.append(f"{prefix}: family must be absent/null unless practice")

    technique_id = identity.get("technique_id")
    if technique_id is not None:
        if not isinstance(technique_id, str) or not technique_id.startswith(
            TECHNIQUE_ID_PREFIX
        ):
            errors.append(
                f"{prefix}: identity.technique_id must be string starting with {TECHNIQUE_ID_PREFIX!r}"
            )

    if identity.get("status") not in ALLOWED_STATUS:
        errors.append(f"{prefix}: invalid identity.status")

    if identity.get("status") == "draft":
        seed_cell = identity.get("seed_cell")
        if not isinstance(seed_cell, str) or not seed_cell.startswith("need."):
            errors.append(f"{prefix}: draft item requires identity.seed_cell")

    for key in RETRIEVAL_REQUIRED:
        if key not in retrieval:
            errors.append(f"{prefix}: retrieval missing {key}")

    def _enum_list(field: str, allowed: list[str], *, allow_empty: bool) -> None:
        values = _as_str_list(retrieval.get(field), allow_empty=allow_empty)
        if values is None:
            errors.append(f"{prefix}: retrieval.{field} must be string list")
            return
        bad = [x for x in values if x not in allowed]
        if bad:
            errors.append(f"{prefix}: retrieval.{field} unknown {bad}")

    _enum_list("purpose", list(vocab.get("purpose") or []), allow_empty=False)
    _enum_list("input_state", list(vocab.get("input_state") or []), allow_empty=False)
    _enum_list("direction", list(vocab.get("direction") or []), allow_empty=False)
    _enum_list("context", list(vocab.get("context") or []), allow_empty=False)
    _enum_list("delivery", list(vocab.get("delivery") or []), allow_empty=False)

    domain = retrieval.get("domain", [])
    domain_values = _as_str_list(domain, allow_empty=True)
    if domain_values is None:
        errors.append(f"{prefix}: retrieval.domain must be string list")
    else:
        bad = [x for x in domain_values if x not in (vocab.get("domain") or [])]
        if bad:
            errors.append(f"{prefix}: retrieval.domain unknown {bad}")

    if retrieval.get("intensity") not in (vocab.get("intensity") or []):
        errors.append(f"{prefix}: invalid intensity")
    if retrieval.get("energy_effect") not in (vocab.get("energy_effect") or []):
        errors.append(f"{prefix}: invalid energy_effect")

    duration = retrieval.get("duration")
    duration_unit = retrieval.get("duration_unit")
    if content_class != "discipline":
        if not isinstance(duration, int) or duration < 1:
            errors.append(f"{prefix}: duration must be positive int")
        if duration_unit not in (vocab.get("duration_unit") or []):
            errors.append(f"{prefix}: invalid duration_unit")
        extra = [k for k in DISCIPLINE_RETRIEVAL_EXTRA if k in retrieval]
        if extra:
            errors.append(f"{prefix}: non-discipline must not set {extra}")

    if content_class == "discipline":
        for key in DISCIPLINE_RETRIEVAL_EXTRA:
            if key not in retrieval:
                errors.append(f"{prefix}: discipline retrieval missing {key}")
        duration_days = retrieval.get("duration_days")
        if not isinstance(duration_days, int) or duration_days < 1:
            errors.append(f"{prefix}: duration_days must be positive int")
        if retrieval.get("frequency") not in (vocab.get("discipline_frequency") or []):
            errors.append(f"{prefix}: invalid frequency")
        if retrieval.get("difficulty") not in (vocab.get("discipline_difficulty") or []):
            errors.append(f"{prefix}: invalid difficulty")
        if retrieval.get("failure_policy") not in (
            vocab.get("discipline_failure_policy") or []
        ):
            errors.append(f"{prefix}: invalid failure_policy")
        if retrieval.get("check_in_frequency") not in (
            vocab.get("discipline_check_in_frequency") or []
        ):
            errors.append(f"{prefix}: invalid check_in_frequency")
        if "duration" in retrieval or "duration_unit" in retrieval:
            errors.append(f"{prefix}: discipline must not set session duration")
        for key in DISCIPLINE_PAYLOAD_EXTRA:
            value = payload.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{prefix}: discipline payload missing {key}")
        exceptions = payload.get("allowed_exceptions", [])
        if _as_str_list(exceptions, allow_empty=True) is None:
            errors.append(f"{prefix}: allowed_exceptions must be string list")
    else:
        extra_payload = [k for k in DISCIPLINE_PAYLOAD_EXTRA if k in payload]
        if extra_payload:
            errors.append(f"{prefix}: non-discipline must not set {extra_payload}")

    for key in PAYLOAD_REQUIRED:
        if key not in payload:
            errors.append(f"{prefix}: payload missing {key}")
    if payload.get("body_kind") not in ALLOWED_BODY_KIND:
        errors.append(f"{prefix}: invalid body_kind")
    locales = payload.get("locales")
    if not isinstance(locales, dict) or "ru" not in locales:
        errors.append(f"{prefix}: payload.locales.ru required")
    else:
        ru = locales.get("ru")
        if not isinstance(ru, dict):
            errors.append(f"{prefix}: payload.locales.ru must be object")
        else:
            if not str(ru.get("title") or "").strip():
                errors.append(f"{prefix}: ru.title empty")
            if not str(ru.get("body") or "").strip():
                errors.append(f"{prefix}: ru.body empty")

    blob = _payload_text(payload)
    hits = [m for m in PAYLOAD_LOGIC_MARKERS if m in blob]
    type_code = identity.get("type")
    if isinstance(type_code, str) and type_code and type_code.lower() in blob:
        hits.append(type_code)
    item_id = identity.get("item_id")
    if isinstance(item_id, str) and item_id and item_id.lower() in blob:
        hits.append(item_id)
    if hits:
        errors.append(f"{prefix}: payload contains semantic/retrieval markers {hits}")

    return errors


def validate_technique_canon_v1(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if registry.get("contract_version") != "technique_canon_v1":
        errors.append("invalid technique canon contract_version")
    if registry.get("research_ladder_required") is True:
        errors.append("research ladder must not be required for technique rows")
    techniques = registry.get("techniques")
    if not isinstance(techniques, list):
        errors.append("techniques must be list")
        return errors
    seen: set[str] = set()
    for i, row in enumerate(techniques):
        prefix = f"technique[{i}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix}: must be object")
            continue
        status = row.get("status")
        if status not in ALLOWED_TECHNIQUE_STATUS:
            errors.append(f"{prefix}: status must be accepted or skipped")
        required = TECHNIQUE_REQUIRED
        if status == "skipped":
            required = (
                "technique_id",
                "content_class",
                "type",
                "status",
                "skip_reason",
            )
        for key in required:
            if key not in row:
                errors.append(f"{prefix}: missing {key}")
        technique_id = row.get("technique_id")
        if not isinstance(technique_id, str) or not technique_id.startswith(
            TECHNIQUE_ID_PREFIX
        ):
            errors.append(f"{prefix}: technique_id must start with {TECHNIQUE_ID_PREFIX!r}")
        elif technique_id in seen:
            errors.append(f"{prefix}: duplicate technique_id {technique_id!r}")
        else:
            seen.add(technique_id)
        if row.get("content_class") not in LANDSCAPE_CONTENT_CLASS:
            errors.append(f"{prefix}: invalid content_class")
        source_refs = row.get("source_refs")
        if source_refs is not None:
            if not isinstance(source_refs, list):
                errors.append(f"{prefix}: source_refs must be list")
            elif not all(isinstance(x, dict) for x in source_refs):
                errors.append(f"{prefix}: source_refs must be object list")
        for list_key in ("safety_notes", "allowed_claims"):
            if list_key in row and _as_str_list(row.get(list_key), allow_empty=True) is None:
                errors.append(f"{prefix}: {list_key} must be string list")
        if status == "accepted":
            description = str(row.get("canonical_description") or "").strip()
            if not description:
                errors.append(f"{prefix}: accepted row needs canonical_description")
            if not isinstance(source_refs, list) or not source_refs:
                errors.append(f"{prefix}: accepted row needs source_refs")
        if status == "skipped":
            reason = str(row.get("skip_reason") or "").strip()
            if not reason:
                errors.append(f"{prefix}: skipped row needs skip_reason")
    return errors


def validate_technique_landscape_v1(
    landscape: dict[str, Any],
    *,
    vocab: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if landscape.get("contract_version") != "technique_landscape_v1":
        errors.append("invalid technique landscape contract_version")
    if landscape.get("shortlist_opened") is not False:
        errors.append("shortlist_opened must be false (full corpus still closed)")
    if landscape.get("writes_technique_canon") is not False:
        errors.append("writes_technique_canon must be false")
    if landscape.get("criteria_canon") not in (
        None,
        "PRACTICE_TECHNIQUE_SHORTLIST_CRITERIA_V1",
    ):
        errors.append("landscape.criteria_canon must point at Criteria V1 or be absent")
    shortlist_mode = landscape.get("shortlist_mode")
    if shortlist_mode not in (None, "closed", "vertical_slice"):
        errors.append("shortlist_mode must be closed or vertical_slice")
    slice_family = landscape.get("shortlist_slice_family")
    if shortlist_mode == "vertical_slice":
        if not isinstance(slice_family, str) or not slice_family.startswith("family."):
            errors.append("vertical_slice requires shortlist_slice_family")
        if landscape.get("shortlist_canon") not in (
            None,
            "PRACTICE_TECHNIQUE_SHORTLIST_V1",
        ):
            errors.append("landscape.shortlist_canon must point at Shortlist V1 or be absent")
    elif slice_family not in (None, ""):
        errors.append("shortlist_slice_family only allowed with vertical_slice")
    families = landscape.get("families")
    if not isinstance(families, list) or not families:
        errors.append("families must be non-empty list")
        return errors

    allowed_types: dict[str, set[str]] = {}
    if vocab:
        for cls, rows in (vocab.get("types") or {}).items():
            allowed_types[str(cls)] = {
                row["code"]
                for row in rows
                if isinstance(row, dict) and row.get("code")
            }

    seen_ids: set[str] = set()
    classes_seen: set[str] = set()
    sliced_ids: list[str] = []
    types_by_family: dict[str, set[str]] = {}
    for i, row in enumerate(families):
        prefix = f"family[{i}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix}: must be object")
            continue
        for key in LANDSCAPE_REQUIRED:
            if key not in row:
                errors.append(f"{prefix}: missing {key}")
        family_id = row.get("family_id")
        if not isinstance(family_id, str) or not family_id.startswith("family."):
            errors.append(f"{prefix}: family_id must start with 'family.'")
        elif family_id in seen_ids:
            errors.append(f"{prefix}: duplicate family_id {family_id!r}")
        else:
            seen_ids.add(family_id)
        content_class = row.get("content_class")
        if content_class not in LANDSCAPE_CONTENT_CLASS:
            errors.append(f"{prefix}: invalid content_class")
        else:
            classes_seen.add(str(content_class))
        status = row.get("shortlist_status")
        if status not in ("not_opened", "sliced"):
            errors.append(f"{prefix}: shortlist_status must be not_opened or sliced")
        elif status == "sliced":
            sliced_ids.append(str(family_id))
        if row.get("claim_risk") not in ALLOWED_CLAIM_RISK:
            errors.append(f"{prefix}: invalid claim_risk")
        if not isinstance(row.get("candidate_family"), str) or not str(
            row.get("candidate_family") or ""
        ).strip():
            errors.append(f"{prefix}: candidate_family empty")
        if not isinstance(row.get("mechanism_shape"), str) or not str(
            row.get("mechanism_shape") or ""
        ).strip():
            errors.append(f"{prefix}: mechanism_shape empty")
        for list_key in (
            "candidate_types",
            "bounds_to_research",
            "variant_axes",
            "source_families",
            "probe_links",
        ):
            values = _as_str_list(row.get(list_key), allow_empty=True)
            if values is None:
                errors.append(f"{prefix}: {list_key} must be string list")
                continue
            if list_key == "source_families":
                bad = [x for x in values if x not in ALLOWED_SOURCE_FAMILY]
                if bad:
                    errors.append(f"{prefix}: unknown source_families {bad}")
            if list_key == "candidate_types" and vocab and content_class in allowed_types:
                bad = [x for x in values if x not in allowed_types[str(content_class)]]
                if bad:
                    errors.append(f"{prefix}: candidate_types not in vocab {bad}")
                types_by_family[str(family_id)] = set(values)

    missing_cls = LANDSCAPE_CONTENT_CLASS - classes_seen
    if missing_cls:
        errors.append(f"landscape missing content_class {sorted(missing_cls)}")

    def _types(fid: str) -> set[str]:
        return types_by_family.get(fid, set())

    if "energizing_breath" in _types("family.practice.activating_forceful_breath"):
        errors.append("energizing_breath must not map to activating_forceful_breath")
    if "energizing_breath" not in _types("family.practice.unattested_short_exhale"):
        errors.append("energizing_breath must sit on unattested_short_exhale")
    if "capability" in _types("family.affirmation.values_self_affirmation"):
        errors.append("capability must not map to values_self_affirmation")
    if "capability" not in _types("family.affirmation.coping_statement"):
        errors.append("capability must sit on coping_statement")
    if "body_release" in _types("family.practice.progressive_muscle_relaxation"):
        errors.append("body_release must not map to PMR")
    if "body_release" not in _types("family.practice.informal_somatic_release"):
        errors.append("body_release must sit on informal_somatic_release")
    if "sleep_discipline" in _types("family.discipline.clinical_insomnia_protocol"):
        errors.append("sleep_discipline must not map to clinical_insomnia_protocol")
    if "sleep_discipline" not in _types("family.discipline.schedule_window"):
        errors.append("sleep_discipline must sit on schedule_window")
    if _types("family.discipline.clinical_insomnia_protocol"):
        errors.append("clinical_insomnia_protocol candidate_types must stay empty")
    if _types("family.affirmation.values_self_affirmation"):
        errors.append("values_self_affirmation candidate_types must stay empty until a type exists")

    if shortlist_mode == "vertical_slice":
        if len(sliced_ids) != 1:
            errors.append("vertical_slice requires exactly one sliced family")
        elif sliced_ids[0] != slice_family:
            errors.append("sliced family must equal shortlist_slice_family")
    elif sliced_ids:
        errors.append("sliced families require shortlist_mode=vertical_slice")

    return errors


CRITERIA_GATE_IDS = tuple(f"C{i}" for i in range(1, 10))
CRITERIA_REQUIRED = (
    "contract_version",
    "unit_of_shortlist",
    "shortlist_opened",
    "writes_technique_canon",
    "technique_id_allowed_at",
    "pipeline_after_open",
    "gates",
)


def validate_technique_shortlist_criteria_v1(criteria: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in CRITERIA_REQUIRED:
        if key not in criteria:
            errors.append(f"criteria missing {key}")
    if criteria.get("contract_version") != "technique_shortlist_criteria_v1":
        errors.append("invalid shortlist criteria contract_version")
    if criteria.get("shortlist_opened") is not False:
        errors.append("criteria must not open shortlist")
    if criteria.get("writes_technique_canon") is not False:
        errors.append("criteria must not write technique canon")
    if criteria.get("unit_of_shortlist") != "candidate_family":
        errors.append("unit_of_shortlist must be candidate_family")
    if criteria.get("technique_id_allowed_at") != "canonical":
        errors.append("technique_id_allowed_at must be canonical")
    pipeline = criteria.get("pipeline_after_open")
    if not isinstance(pipeline, list) or "canonical_or_rejected" not in pipeline:
        errors.append("pipeline_after_open must include canonical_or_rejected")
    if isinstance(pipeline, list) and pipeline and pipeline[0] != "candidate_family":
        errors.append("pipeline_after_open must start at candidate_family")
    gates = criteria.get("gates")
    if not isinstance(gates, list):
        errors.append("gates must be list")
        return errors
    ids = [g.get("id") for g in gates if isinstance(g, dict)]
    if tuple(ids) != CRITERIA_GATE_IDS:
        errors.append(f"gates must be {CRITERIA_GATE_IDS} in order, got {tuple(ids)}")
    return errors


SHORTLIST_DECISIONS = frozenset({"selected", "supporting", "rejected"})
SHORTLIST_GATE_RESULTS = frozenset(
    {"pass", "fail", "n_a", "unknown", "preference_match", "preference_weak"}
)
SHORTLIST_HARD_GATES = ("C1", "C2", "C3", "C4", "C5", "C6", "C8")
SHORTLIST_SOURCE_REQUIRED = (
    "source_id",
    "source_family",
    "bibliographic_identity",
    "authority_provenance",
    "locus",
    "gates",
    "extractable",
    "conflicts_unknowns",
    "research_function",
    "selection_decision",
    "rejection_reason",
)
SLICE_FAMILY_V1 = "family.practice.equal_count_breath"


def validate_technique_shortlist_v1(shortlist: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if shortlist.get("contract_version") != "technique_shortlist_v1":
        errors.append("invalid technique shortlist contract_version")
    if shortlist.get("writes_technique_canon") is not False:
        errors.append("shortlist must not write technique canon")
    if shortlist.get("technique_id_allowed") is not False:
        errors.append("shortlist must not allow technique_id")
    if shortlist.get("unit_of_shortlist") != "candidate_family":
        errors.append("unit_of_shortlist must be candidate_family")
    if shortlist.get("selected_means") != "allowed_for_next_ingest_pass":
        errors.append("selected_means must be allowed_for_next_ingest_pass")
    if shortlist.get("boundary_held") != (
        "landscape_candidate_family_to_selected_loci_not_canonical"
    ):
        errors.append("boundary_held must record family→loci, not canonical")
    families = shortlist.get("families")
    if not isinstance(families, list) or len(families) != 1:
        errors.append("V1 shortlist must contain exactly one family slice")
        return errors
    row = families[0]
    if not isinstance(row, dict):
        errors.append("family slice must be object")
        return errors
    if row.get("family_id") != SLICE_FAMILY_V1:
        errors.append(f"V1 slice family must be {SLICE_FAMILY_V1}")
    if row.get("candidate_family") in (None, ""):
        errors.append("candidate_family empty")
    hypothesis = row.get("expression_hypothesis")
    if not isinstance(hypothesis, dict):
        errors.append("expression_hypothesis must be object")
    else:
        if hypothesis.get("type") != "box_breathing":
            errors.append("equal_count expression hypothesis type must be box_breathing")
        if hypothesis.get("status") != "not_attested":
            errors.append("expression hypothesis must stay not_attested")
        if hypothesis.get("probe_item_id") != "practice.box_breathing.001":
            errors.append("expression hypothesis must name the box_breathing probe")
    conflicts = row.get("conflicts")
    if not isinstance(conflicts, list) or len(conflicts) < 2:
        errors.append("family must record unresolved conflicts (not averaged)")
    else:
        conflict_ids = [c.get("id") for c in conflicts if isinstance(c, dict)]
        if "conflict.phase_count" not in conflict_ids:
            errors.append("must record three-phase vs four-phase conflict")
    sources = row.get("candidate_sources")
    if not isinstance(sources, list) or not sources:
        errors.append("candidate_sources must be non-empty list")
        return errors
    seen_sources: set[str] = set()
    selected_ids: list[str] = []
    for i, src in enumerate(sources):
        prefix = f"source[{i}]"
        if not isinstance(src, dict):
            errors.append(f"{prefix}: must be object")
            continue
        for key in SHORTLIST_SOURCE_REQUIRED:
            if key not in src:
                errors.append(f"{prefix}: missing {key}")
        source_id = src.get("source_id")
        if not isinstance(source_id, str) or not source_id.startswith("src."):
            errors.append(f"{prefix}: source_id must start with src.")
        elif source_id in seen_sources:
            errors.append(f"{prefix}: duplicate source_id")
        else:
            seen_sources.add(source_id)
        decision = src.get("selection_decision")
        if decision not in SHORTLIST_DECISIONS:
            errors.append(f"{prefix}: invalid selection_decision")
        reason = src.get("rejection_reason")
        if decision == "selected":
            if reason is not None:
                errors.append(f"{prefix}: selected must have rejection_reason null")
            selected_ids.append(str(source_id))
        elif decision == "rejected":
            if not isinstance(reason, str) or not reason.strip():
                errors.append(f"{prefix}: rejected must have rejection_reason")
        source_family = src.get("source_family")
        if decision in {"selected", "supporting"}:
            if source_family not in ALLOWED_SOURCE_FAMILY:
                errors.append(f"{prefix}: source_family must be a provenance class")
        elif not isinstance(source_family, str) or not source_family.strip():
            errors.append(f"{prefix}: source_family empty")
        if not isinstance(src.get("bibliographic_identity"), dict):
            errors.append(f"{prefix}: bibliographic_identity must be object")
        if not isinstance(src.get("locus"), str) or not str(src.get("locus") or "").strip():
            errors.append(f"{prefix}: locus empty")
        gates = src.get("gates")
        if not isinstance(gates, dict):
            errors.append(f"{prefix}: gates must be object")
        else:
            if tuple(gates.keys()) != CRITERIA_GATE_IDS:
                errors.append(f"{prefix}: gates must be C1–C9")
            for gid, body in gates.items():
                if not isinstance(body, dict) or body.get("result") not in SHORTLIST_GATE_RESULTS:
                    errors.append(f"{prefix}.{gid}: invalid gate result")
            if decision == "selected":
                for gid in SHORTLIST_HARD_GATES:
                    result = (gates.get(gid) or {}).get("result")
                    if result != "pass":
                        errors.append(f"{prefix}: selected requires {gid}=pass")
        extractable = src.get("extractable")
        if not isinstance(extractable, dict):
            errors.append(f"{prefix}: extractable must be object")
        else:
            for key in ("mechanism", "kernel", "bounds", "safety", "variants"):
                if key not in extractable:
                    errors.append(f"{prefix}: extractable missing {key}")
    listed = row.get("selected_loci")
    if not isinstance(listed, list) or [x for x in listed if not isinstance(x, str)]:
        errors.append("selected_loci must be string list")
    elif listed != selected_ids:
        errors.append("selected_loci must match sources with selection_decision=selected")
    if len(selected_ids) < 2:
        errors.append("slice must select more than one locus (kernel vs conflict/safety)")
    return errors


INGEST_REQUIRED = (
    "evidence_id",
    "candidate_family",
    "source_ref",
    "locus",
    "source_family",
    "paraphrase",
    "observed_mechanism",
    "observed_steps",
    "observed_bounds",
    "observed_safety",
    "observed_variants",
    "claim_scope",
    "conflict_tags",
    "ingest_status",
)
INGEST_CLAIM_SCOPE = frozenset(
    {
        "method_sequence_only",
        "method_sequence_and_stop_rules",
        "conflicting_method_sequence",
    }
)
INGEST_FORBIDDEN_SYNTHESIS = (
    "common kernel",
    "общим ядром",
    "second hold is optional",
    "вторая задержка optional",
    "optional hold",
    "variant of",
)
SELECTED_LOCI_V1 = (
    "src.bhf.heart_matters.box",
    "src.nhs.sfh.box_leaflet",
    "src.nhs.newcastle.square",
)


def _ingest_blob(row: dict[str, Any]) -> str:
    parts = [
        str(row.get("paraphrase") or ""),
        str(row.get("observed_mechanism") or ""),
        " ".join(_as_str_list(row.get("observed_steps"), allow_empty=True) or []),
        " ".join(_as_str_list(row.get("observed_bounds"), allow_empty=True) or []),
        " ".join(_as_str_list(row.get("observed_safety"), allow_empty=True) or []),
        " ".join(_as_str_list(row.get("observed_variants"), allow_empty=True) or []),
        " ".join(_as_str_list(row.get("conflict_tags"), allow_empty=True) or []),
    ]
    return " ".join(parts).lower()


def validate_technique_ingest_v1(
    ingest: dict[str, Any],
    *,
    shortlist: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if ingest.get("contract_version") != "technique_ingest_v1":
        errors.append("invalid technique ingest contract_version")
    if ingest.get("writes_technique_canon") is not False:
        errors.append("ingest must not write technique canon")
    if ingest.get("technique_id_allowed") is not False:
        errors.append("ingest must not allow technique_id")
    if ingest.get("does_not_normalize") is not True:
        errors.append("ingest must declare does_not_normalize")
    if ingest.get("family_id") != SLICE_FAMILY_V1:
        errors.append(f"V1 ingest family must be {SLICE_FAMILY_V1}")
    if ingest.get("boundary_held") != (
        "selected_loci_to_ingested_evidence_not_canonical_kernel"
    ):
        errors.append("boundary_held must record loci→evidence, not a kernel")
    rows = ingest.get("evidence")
    if not isinstance(rows, list) or len(rows) != 3:
        errors.append("V1 ingest must contain exactly three evidence records")
        return errors

    expected_sources = list(SELECTED_LOCI_V1)
    if shortlist:
        families = shortlist.get("families")
        if isinstance(families, list) and families and isinstance(families[0], dict):
            listed = families[0].get("selected_loci")
            if isinstance(listed, list) and all(isinstance(x, str) for x in listed):
                expected_sources = listed

    seen_ids: set[str] = set()
    source_ids: list[str] = []
    by_source: dict[str, dict[str, Any]] = {}
    for i, row in enumerate(rows):
        prefix = f"evidence[{i}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix}: must be object")
            continue
        for key in INGEST_REQUIRED:
            if key not in row:
                errors.append(f"{prefix}: missing {key}")
        evidence_id = row.get("evidence_id")
        if not isinstance(evidence_id, str) or not evidence_id.startswith("ev."):
            errors.append(f"{prefix}: evidence_id must start with ev.")
        elif evidence_id in seen_ids:
            errors.append(f"{prefix}: duplicate evidence_id")
        else:
            seen_ids.add(evidence_id)
        if row.get("candidate_family") != SLICE_FAMILY_V1:
            errors.append(f"{prefix}: candidate_family must be the slice family")
        if row.get("source_family") not in ALLOWED_SOURCE_FAMILY:
            errors.append(f"{prefix}: invalid source_family")
        if row.get("ingest_status") != "ingested":
            errors.append(f"{prefix}: ingest_status must be ingested")
        if row.get("claim_scope") not in INGEST_CLAIM_SCOPE:
            errors.append(f"{prefix}: invalid claim_scope")
        source_ref = row.get("source_ref")
        if not isinstance(source_ref, dict):
            errors.append(f"{prefix}: source_ref must be object")
            continue
        source_id = source_ref.get("source_id")
        if not isinstance(source_id, str) or not source_id.startswith("src."):
            errors.append(f"{prefix}: source_ref.source_id invalid")
        else:
            source_ids.append(source_id)
            by_source[source_id] = row
        if not isinstance(row.get("paraphrase"), str) or not str(
            row.get("paraphrase") or ""
        ).strip():
            errors.append(f"{prefix}: paraphrase empty")
        if not isinstance(row.get("observed_mechanism"), str) or not str(
            row.get("observed_mechanism") or ""
        ).strip():
            errors.append(f"{prefix}: observed_mechanism empty")
        if not isinstance(row.get("locus"), str) or not str(row.get("locus") or "").strip():
            errors.append(f"{prefix}: locus empty")
        for list_key in (
            "observed_steps",
            "observed_bounds",
            "observed_safety",
            "observed_variants",
            "conflict_tags",
        ):
            if _as_str_list(row.get(list_key), allow_empty=True) is None:
                errors.append(f"{prefix}: {list_key} must be string list")
        steps = _as_str_list(row.get("observed_steps"), allow_empty=True) or []
        if len(steps) < 3:
            errors.append(f"{prefix}: observed_steps too short for a method observation")
        blob = _ingest_blob(row)
        for phrase in INGEST_FORBIDDEN_SYNTHESIS:
            if phrase in blob:
                errors.append(f"{prefix}: synthesis phrase {phrase!r} is normalization")

    if source_ids != expected_sources:
        errors.append("ingest source_ids must match selected_loci in order")

    sfh = by_source.get("src.nhs.sfh.box_leaflet")
    if sfh:
        steps_blob = " ".join(
            _as_str_list(sfh.get("observed_steps"), allow_empty=True) or []
        ).lower()
        safety = _as_str_list(sfh.get("observed_safety"), allow_empty=True) or []
        if any(token in steps_blob for token in ("dizz", "light-head", "grounding")):
            errors.append("SFH sequence must not carry stop/safety text")
        if not safety:
            errors.append("SFH must record stop/safety in observed_safety")
        if sfh.get("claim_scope") != "method_sequence_and_stop_rules":
            errors.append("SFH claim_scope must keep sequence and stop-rules distinct")

    newcastle = by_source.get("src.nhs.newcastle.square")
    if newcastle:
        tags = _as_str_list(newcastle.get("conflict_tags"), allow_empty=True) or []
        if "recorded_as_conflicting_description_not_variant" not in tags:
            errors.append("Newcastle must be tagged as conflicting description, not variant")
        variants = _as_str_list(newcastle.get("observed_variants"), allow_empty=True) or []
        if variants:
            errors.append("Newcastle must not declare observed_variants this pass")
        if newcastle.get("claim_scope") != "conflicting_method_sequence":
            errors.append("Newcastle claim_scope must be conflicting_method_sequence")
        steps_blob = " ".join(
            _as_str_list(newcastle.get("observed_steps"), allow_empty=True) or []
        ).lower()
        if "after the exhale" not in steps_blob and "post-exhale" not in steps_blob:
            errors.append("Newcastle must observe that it does not write a hold after exhale")

    bhf = by_source.get("src.bhf.heart_matters.box")
    if bhf:
        safety = _as_str_list(bhf.get("observed_safety"), allow_empty=True) or []
        if safety:
            errors.append("BHF box section must not invent observed_safety")
        if bhf.get("claim_scope") != "method_sequence_only":
            errors.append("BHF claim_scope must be method_sequence_only")

    return errors


NORMALIZATION_DECISIONS = frozenset(
    {"normalize_one", "split_family", "insufficient_evidence"}
)
NORMALIZATION_LEVELS = (
    "mechanism",
    "identity_bearing_steps",
    "bounds",
    "variants_vs_conflicts",
)
NORMALIZATION_EVIDENCE_V1 = (
    "ev.equal_count.bhf.heart_matters.box",
    "ev.equal_count.nhs_sfh.box_leaflet",
    "ev.equal_count.nhs_newcastle.square",
)


def validate_technique_normalization_v1(
    normalization: dict[str, Any],
    *,
    ingest: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if normalization.get("contract_version") != "technique_normalization_v1":
        errors.append("invalid technique normalization contract_version")
    if normalization.get("writes_technique_canon") is not False:
        errors.append("normalization must not write technique canon")
    if normalization.get("technique_id_allowed") is not False:
        errors.append("normalization must not allow technique_id")
    if normalization.get("normalize_one_is_not_canonical") is not True:
        errors.append("normalize_one must remain not-canonical")
    if normalization.get("does_not_rewrite_landscape_kernel") is not True:
        errors.append("normalization must not rewrite landscape kernel this pass")
    if normalization.get("family_id") != SLICE_FAMILY_V1:
        errors.append(f"V1 normalization family must be {SLICE_FAMILY_V1}")
    if normalization.get("boundary_held") != (
        "ingested_evidence_to_normalization_decision_not_canonical"
    ):
        errors.append("boundary_held must record evidence→decision, not canon")
    decision = normalization.get("decision")
    if decision not in NORMALIZATION_DECISIONS:
        errors.append("decision must be normalize_one, split_family, or insufficient_evidence")
    if decision != "insufficient_evidence":
        errors.append("equal_count_breath V1 must close as insufficient_evidence")
    comparison = normalization.get("comparison")
    if not isinstance(comparison, dict):
        errors.append("comparison must be object")
    else:
        if tuple(comparison.keys()) != NORMALIZATION_LEVELS:
            errors.append("comparison must be the four levels in order")
        for level in NORMALIZATION_LEVELS:
            body = comparison.get(level)
            if not isinstance(body, dict):
                errors.append(f"comparison.{level} must be object")
                continue
            if not str(body.get("question") or "").strip():
                errors.append(f"comparison.{level}: question empty")
            if body.get("status") in (None, ""):
                errors.append(f"comparison.{level}: status empty")
        identity = comparison.get("identity_bearing_steps") or {}
        if identity.get("status") != "unresolved":
            errors.append("identity_bearing_steps must stay unresolved this pass")
        variants = comparison.get("variants_vs_conflicts") or {}
        if variants.get("status") != "unresolved":
            errors.append("variants_vs_conflicts must stay unresolved this pass")
    evidence_ids = normalization.get("evidence_ids")
    expected = list(NORMALIZATION_EVIDENCE_V1)
    if ingest:
        rows = ingest.get("evidence")
        if isinstance(rows, list):
            expected = [
                str(row.get("evidence_id"))
                for row in rows
                if isinstance(row, dict) and row.get("evidence_id")
            ]
    if evidence_ids != expected:
        errors.append("evidence_ids must match ingest records in order")
    if not str(normalization.get("research_question") or "").strip():
        errors.append("insufficient_evidence requires a research_question")
    question = str(normalization.get("research_question") or "").lower()
    if "post-exhale hold" not in question and "post-exhale" not in question:
        errors.append("research_question must name post-exhale hold identity")
    if normalization.get("next_named_pass") != (
        "targeted_shortlist_post_exhale_hold_identity"
    ):
        errors.append("next_named_pass must be targeted shortlist, not safety review")
    blob = " ".join(
        [
            str(normalization.get("research_question") or ""),
            " ".join(str(x) for x in (normalization.get("why_not_normalize_one") or [])),
            " ".join(str(x) for x in (normalization.get("why_not_split_family") or [])),
        ]
    ).lower()
    if "optional hold" in blob or "second hold is optional" in blob:
        errors.append("must not declare an optional hold")
    if not isinstance(normalization.get("why_not_normalize_one"), list) or len(
        normalization.get("why_not_normalize_one") or []
    ) < 2:
        errors.append("must record why_not_normalize_one")
    if not isinstance(normalization.get("why_not_split_family"), list) or len(
        normalization.get("why_not_split_family") or []
    ) < 2:
        errors.append("must record why_not_split_family")
    return errors


TARGETED_SHORTLIST_RESOLUTION_ROLES = frozenset(
    {"definition", "contrast", "variant", "replication", "non_resolving"}
)
TARGETED_SHORTLIST_SELECTABLE_ROLES = frozenset({"definition", "contrast", "variant"})
TARGETED_SHORTLIST_IDENTITY = frozenset(
    {
        "required",
        "optional",
        "absent_but_unaddressed",
        "distinguishes_method",
        "unknown",
    }
)
TARGETED_SHORTLIST_DECISIONS = frozenset(
    {"selected", "supporting", "rejected", "already_ingested"}
)
TARGETED_SHORTLIST_STOP = frozenset(
    {
        "resolution_candidates_found_for_targeted_ingest",
        "unresolved_reasonable_search_found_no_resolution_evidence",
    }
)
TARGETED_SHORTLIST_REQUIRED = (
    "source_id",
    "source_family",
    "bibliographic_identity",
    "authority_provenance",
    "locus",
    "gates",
    "extractable",
    "resolution_role",
    "identity_statement",
    "conflicts_unknowns",
    "research_function",
    "selection_decision",
    "rejection_reason",
)
ALREADY_INGESTED_LOCI_V1 = SELECTED_LOCI_V1


def validate_technique_targeted_shortlist_v1(
    targeted: dict[str, Any],
    *,
    ingest: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if targeted.get("contract_version") != "technique_targeted_shortlist_v1":
        errors.append("invalid targeted shortlist contract_version")
    if targeted.get("writes_technique_canon") is not False:
        errors.append("targeted shortlist must not write technique canon")
    if targeted.get("technique_id_allowed") is not False:
        errors.append("targeted shortlist must not allow technique_id")
    if targeted.get("unit_of_shortlist") != "research_question":
        errors.append("unit_of_shortlist must be research_question")
    if targeted.get("selected_means") != "allowed_for_targeted_ingest_pass":
        errors.append("selected_means must be allowed_for_targeted_ingest_pass")
    if targeted.get("does_not_rewrite_landscape_kernel") is not True:
        errors.append("targeted shortlist must not rewrite landscape kernel")
    if targeted.get("boundary_held") != (
        "research_question_to_resolution_loci_not_canonical"
    ):
        errors.append("boundary_held must record question→resolution loci, not canon")
    if targeted.get("family_id") != SLICE_FAMILY_V1:
        errors.append(f"V1 targeted shortlist family must be {SLICE_FAMILY_V1}")
    question = str(targeted.get("research_question") or "").lower()
    if "post-exhale hold" not in question and "post-exhale" not in question:
        errors.append("research_question must name post-exhale hold identity")
    not_in_scope = targeted.get("not_in_scope")
    if not isinstance(not_in_scope, list) or "box_breathing_in_general" not in not_in_scope:
        errors.append("must declare box_breathing_in_general out of scope")
    hypothesis = targeted.get("expression_hypothesis")
    if not isinstance(hypothesis, dict):
        errors.append("expression_hypothesis must be object")
    else:
        if hypothesis.get("type") != "box_breathing":
            errors.append("expression hypothesis type must stay box_breathing")
        if hypothesis.get("status") != "not_attested":
            errors.append("expression hypothesis must stay not_attested")
    stop = targeted.get("stop_reason")
    if stop not in TARGETED_SHORTLIST_STOP:
        errors.append("stop_reason must be a declared stopping criterion")
    if targeted.get("next_named_pass") != "targeted_ingest_post_exhale_hold_identity":
        errors.append("next_named_pass must be targeted ingest, then Normalization V1.1")
    not_next = targeted.get("not_next")
    if not isinstance(not_next, list) or "safety_review" not in not_next:
        errors.append("not_next must include safety_review")
    if targeted.get("repeat_insufficient_evidence_after_v1_1_is_allowed") is not True:
        errors.append("repeat insufficient_evidence after V1.1 must remain allowed")
    if targeted.get("variant_found_in_preferred_class") is not False:
        errors.append("this pass must record that preferred-class variant was not found")

    already = targeted.get("already_ingested_loci")
    expected_already = list(ALREADY_INGESTED_LOCI_V1)
    if ingest:
        rows = ingest.get("evidence")
        if isinstance(rows, list):
            expected_already = []
            for row in rows:
                if not isinstance(row, dict):
                    continue
                ref = row.get("source_ref")
                if isinstance(ref, dict) and ref.get("source_id"):
                    expected_already.append(str(ref.get("source_id")))
    if already != expected_already:
        errors.append("already_ingested_loci must match Ingest V1 selected sources")

    loci = targeted.get("candidate_loci")
    if not isinstance(loci, list) or not loci:
        errors.append("candidate_loci must be non-empty list")
        return errors

    seen: set[str] = set()
    selected_ids: list[str] = []
    already_ids: list[str] = []
    selected_roles: set[str] = set()
    by_id: dict[str, dict[str, Any]] = {}
    for i, src in enumerate(loci):
        prefix = f"locus[{i}]"
        if not isinstance(src, dict):
            errors.append(f"{prefix}: must be object")
            continue
        for key in TARGETED_SHORTLIST_REQUIRED:
            if key not in src:
                errors.append(f"{prefix}: missing {key}")
        source_id = src.get("source_id")
        if not isinstance(source_id, str) or not source_id.startswith("src."):
            errors.append(f"{prefix}: source_id must start with src.")
        elif source_id in seen:
            errors.append(f"{prefix}: duplicate source_id")
        else:
            seen.add(source_id)
            by_id[source_id] = src
        decision = src.get("selection_decision")
        if decision not in TARGETED_SHORTLIST_DECISIONS:
            errors.append(f"{prefix}: invalid selection_decision")
        role = src.get("resolution_role")
        if role not in TARGETED_SHORTLIST_RESOLUTION_ROLES:
            errors.append(f"{prefix}: invalid resolution_role")
        identity = src.get("identity_statement")
        if identity not in TARGETED_SHORTLIST_IDENTITY:
            errors.append(f"{prefix}: invalid identity_statement")
        reason = src.get("rejection_reason")
        if decision == "selected":
            if reason is not None:
                errors.append(f"{prefix}: selected must have rejection_reason null")
            if role not in TARGETED_SHORTLIST_SELECTABLE_ROLES:
                errors.append(f"{prefix}: selected must be definition, contrast, or variant")
            selected_ids.append(str(source_id))
            if isinstance(role, str):
                selected_roles.add(role)
        elif decision == "already_ingested":
            if reason is not None:
                errors.append(f"{prefix}: already_ingested must have rejection_reason null")
            already_ids.append(str(source_id))
        elif decision == "rejected":
            if not isinstance(reason, str) or not reason.strip():
                errors.append(f"{prefix}: rejected must have rejection_reason")
        source_family = src.get("source_family")
        if decision in {"selected", "supporting", "already_ingested"}:
            if source_family not in ALLOWED_SOURCE_FAMILY:
                errors.append(f"{prefix}: source_family must be a provenance class")
        elif not isinstance(source_family, str) or not source_family.strip():
            errors.append(f"{prefix}: source_family empty")
        if not isinstance(src.get("bibliographic_identity"), dict):
            errors.append(f"{prefix}: bibliographic_identity must be object")
        if not isinstance(src.get("locus"), str) or not str(src.get("locus") or "").strip():
            errors.append(f"{prefix}: locus empty")
        gates = src.get("gates")
        if not isinstance(gates, dict):
            errors.append(f"{prefix}: gates must be object")
        else:
            if tuple(gates.keys()) != CRITERIA_GATE_IDS:
                errors.append(f"{prefix}: gates must be C1–C9")
            for gid, body in gates.items():
                if not isinstance(body, dict) or body.get("result") not in SHORTLIST_GATE_RESULTS:
                    errors.append(f"{prefix}.{gid}: invalid gate result")
            if decision == "selected":
                for gid in SHORTLIST_HARD_GATES:
                    result = (gates.get(gid) or {}).get("result")
                    if result != "pass":
                        errors.append(f"{prefix}: selected requires {gid}=pass")
        extractable = src.get("extractable")
        if not isinstance(extractable, dict):
            errors.append(f"{prefix}: extractable must be object")
        else:
            for key in ("mechanism", "kernel", "bounds", "safety", "variants"):
                if key not in extractable:
                    errors.append(f"{prefix}: extractable missing {key}")
        blob = " ".join(
            [
                str(src.get("conflicts_unknowns") or ""),
                str((extractable or {}).get("kernel") or ""),
                str(src.get("research_function") or ""),
            ]
        ).lower()
        if decision == "selected" and (
            "optional hold" in blob or "second hold is optional" in blob
        ):
            errors.append(f"{prefix}: must not synthesize an optional hold")

    listed = targeted.get("selected_loci")
    if not isinstance(listed, list) or [x for x in listed if not isinstance(x, str)]:
        errors.append("selected_loci must be string list")
    elif listed != selected_ids:
        errors.append("selected_loci must match loci with selection_decision=selected")
    if already_ids != expected_already:
        errors.append("already_ingested candidate rows must match already_ingested_loci")

    if stop == "resolution_candidates_found_for_targeted_ingest" and not selected_ids:
        errors.append("stop_reason requires at least one selected resolution locus")
    if (
        stop == "unresolved_reasonable_search_found_no_resolution_evidence"
        and selected_ids
    ):
        errors.append("unresolved stop cannot select resolution loci")

    bhf = by_id.get("src.bhf.heart_matters.box")
    if bhf:
        if bhf.get("selection_decision") != "already_ingested":
            errors.append("BHF must stay already_ingested this pass")
        if bhf.get("resolution_role") != "replication":
            errors.append("BHF is replication for this question, not new resolution")
    sfh = by_id.get("src.nhs.sfh.box_leaflet")
    if sfh:
        if sfh.get("resolution_role") != "replication":
            errors.append("SFH is replication for this question, not new resolution")
    newcastle = by_id.get("src.nhs.newcastle.square")
    if newcastle:
        if newcastle.get("resolution_role") != "non_resolving":
            errors.append("Newcastle does not contrast 3-phase vs 4-phase")
        if newcastle.get("identity_statement") != "absent_but_unaddressed":
            errors.append("Newcastle identity_statement must be absent_but_unaddressed")

    kinds = targeted.get("resolution_kinds_found")
    if not isinstance(kinds, list) or set(kinds) != selected_roles:
        errors.append("resolution_kinds_found must match selected resolution_role values")

    return errors


TARGETED_INGEST_CLAIM_SCOPE = frozenset(
    {
        "experimental_named_conditions",
        "method_sequence_and_label",
    }
)
TARGETED_INGEST_FORBIDDEN_SYNTHESIS = INGEST_FORBIDDEN_SYNTHESIS + (
    "universal definition",
    "family definition",
    "allowed variant",
    "допустимым variant",
)
TARGETED_INGEST_SELECTED_LOCI = (
    "src.byu.marchant.2025.square",
    "src.nhs.wales.cavuhb.square",
)
TARGETED_INGEST_AXES = (
    "shape_phase_structure",
    "timing_ratio",
)
V1_1_HOLD_ANSWERS = frozenset({"required", "optional", "unresolved"})
V1_1_EQUAL_COUNT_ANSWERS = frozenset(
    {"identity_bearing", "common_parameter", "unresolved"}
)


def _targeted_ingest_blob(row: dict[str, Any]) -> str:
    contrast = row.get("observed_contrast_condition")
    contrast_steps = []
    if isinstance(contrast, dict):
        contrast_steps = _as_str_list(contrast.get("observed_steps"), allow_empty=True) or []
    named = row.get("observed_named_conditions")
    named_blob = ""
    if isinstance(named, list):
        named_blob = " ".join(
            str(item.get("name_in_source") or "")
            for item in named
            if isinstance(item, dict)
        )
    return " ".join(
        [
            _ingest_blob(row),
            named_blob,
            " ".join(contrast_steps),
            str((contrast or {}).get("note") or "") if isinstance(contrast, dict) else "",
        ]
    ).lower()


def validate_technique_targeted_ingest_v1(
    targeted_ingest: dict[str, Any],
    *,
    targeted_shortlist: dict[str, Any] | None = None,
    family_ingest: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if targeted_ingest.get("contract_version") != "technique_targeted_ingest_v1":
        errors.append("invalid targeted ingest contract_version")
    if targeted_ingest.get("writes_technique_canon") is not False:
        errors.append("targeted ingest must not write technique canon")
    if targeted_ingest.get("technique_id_allowed") is not False:
        errors.append("targeted ingest must not allow technique_id")
    if targeted_ingest.get("does_not_normalize") is not True:
        errors.append("targeted ingest must declare does_not_normalize")
    if targeted_ingest.get("does_not_glue_axes") is not True:
        errors.append("targeted ingest must not glue phase structure to equal-count")
    if targeted_ingest.get("does_not_replace_family_ingest") is not True:
        errors.append("targeted ingest must not replace family ingest V1")
    if targeted_ingest.get("does_not_rewrite_landscape_kernel") is not True:
        errors.append("targeted ingest must not rewrite landscape kernel")
    if targeted_ingest.get("family_id") != SLICE_FAMILY_V1:
        errors.append(f"targeted ingest family must be {SLICE_FAMILY_V1}")
    if targeted_ingest.get("boundary_held") != (
        "selected_resolution_loci_to_ingested_evidence_not_canonical_kernel"
    ):
        errors.append("boundary_held must record resolution loci→evidence, not a kernel")
    if targeted_ingest.get("next_named_pass") != "technique_normalization_v1_1":
        errors.append("next_named_pass must be Normalization V1.1, not safety review")
    not_next = targeted_ingest.get("not_next")
    if not isinstance(not_next, list) or "safety_review" not in not_next:
        errors.append("not_next must include safety_review")

    axes = targeted_ingest.get("axes_observed_not_decided")
    if not isinstance(axes, list) or [a.get("axis_id") for a in axes if isinstance(a, dict)] != list(
        TARGETED_INGEST_AXES
    ):
        errors.append("axes_observed_not_decided must be shape_phase_structure then timing_ratio")
    else:
        for axis in axes:
            if not isinstance(axis, dict):
                continue
            if axis.get("status") != "signal_only":
                errors.append(f"axis {axis.get('axis_id')} must stay signal_only this pass")

    questions = targeted_ingest.get("v1_1_identity_questions")
    if not isinstance(questions, list) or len(questions) != 2:
        errors.append("v1_1_identity_questions must lock two identity questions")
    else:
        by_qid = {
            q.get("id"): q for q in questions if isinstance(q, dict) and q.get("id")
        }
        hold = by_qid.get("post_exhale_hold") or {}
        equal = by_qid.get("equal_count") or {}
        if set(hold.get("allowed") or []) != V1_1_HOLD_ANSWERS:
            errors.append("post_exhale_hold allowed answers must be required|optional|unresolved")
        if set(equal.get("allowed") or []) != V1_1_EQUAL_COUNT_ANSWERS:
            errors.append(
                "equal_count allowed answers must be identity_bearing|common_parameter|unresolved"
            )
    verdicts = targeted_ingest.get("v1_1_overall_verdict_unchanged")
    if list(verdicts or []) != ["normalize_one", "split_family", "insufficient_evidence"]:
        errors.append("V1.1 overall verdicts must stay the three Normalization outcomes")

    expected_prior = list(NORMALIZATION_EVIDENCE_V1)
    if family_ingest:
        rows = family_ingest.get("evidence")
        if isinstance(rows, list):
            expected_prior = [
                str(row.get("evidence_id"))
                for row in rows
                if isinstance(row, dict) and row.get("evidence_id")
            ]
    if targeted_ingest.get("prior_ingest_corpus") != expected_prior:
        errors.append("prior_ingest_corpus must match family ingest V1 evidence ids")

    expected_sources = list(TARGETED_INGEST_SELECTED_LOCI)
    if targeted_shortlist:
        listed = targeted_shortlist.get("selected_loci")
        if isinstance(listed, list) and all(isinstance(x, str) for x in listed):
            expected_sources = listed

    rows = targeted_ingest.get("evidence")
    if not isinstance(rows, list) or len(rows) != 2:
        errors.append("targeted ingest must contain exactly two evidence records")
        return errors

    seen_ids: set[str] = set()
    source_ids: list[str] = []
    by_source: dict[str, dict[str, Any]] = {}
    for i, row in enumerate(rows):
        prefix = f"evidence[{i}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix}: must be object")
            continue
        for key in INGEST_REQUIRED:
            if key not in row:
                errors.append(f"{prefix}: missing {key}")
        evidence_id = row.get("evidence_id")
        if not isinstance(evidence_id, str) or not evidence_id.startswith("ev."):
            errors.append(f"{prefix}: evidence_id must start with ev.")
        elif evidence_id in seen_ids:
            errors.append(f"{prefix}: duplicate evidence_id")
        else:
            seen_ids.add(evidence_id)
        if row.get("candidate_family") != SLICE_FAMILY_V1:
            errors.append(f"{prefix}: candidate_family must be the slice family")
        if row.get("source_family") not in ALLOWED_SOURCE_FAMILY:
            errors.append(f"{prefix}: invalid source_family")
        if row.get("ingest_status") != "ingested":
            errors.append(f"{prefix}: ingest_status must be ingested")
        if row.get("claim_scope") not in TARGETED_INGEST_CLAIM_SCOPE:
            errors.append(f"{prefix}: invalid claim_scope")
        source_ref = row.get("source_ref")
        if not isinstance(source_ref, dict):
            errors.append(f"{prefix}: source_ref must be object")
            continue
        source_id = source_ref.get("source_id")
        if not isinstance(source_id, str) or not source_id.startswith("src."):
            errors.append(f"{prefix}: source_ref.source_id invalid")
        else:
            source_ids.append(source_id)
            by_source[source_id] = row
        if not isinstance(row.get("paraphrase"), str) or not str(row.get("paraphrase") or "").strip():
            errors.append(f"{prefix}: paraphrase empty")
        if not isinstance(row.get("observed_mechanism"), str) or not str(
            row.get("observed_mechanism") or ""
        ).strip():
            errors.append(f"{prefix}: observed_mechanism empty")
        if not isinstance(row.get("locus"), str) or not str(row.get("locus") or "").strip():
            errors.append(f"{prefix}: locus empty")
        for list_key in (
            "observed_steps",
            "observed_bounds",
            "observed_safety",
            "observed_variants",
            "conflict_tags",
        ):
            if _as_str_list(row.get(list_key), allow_empty=True) is None:
                errors.append(f"{prefix}: {list_key} must be string list")
        steps = _as_str_list(row.get("observed_steps"), allow_empty=True) or []
        if len(steps) < 4:
            errors.append(f"{prefix}: observed_steps too short for a method observation")
        blob = _targeted_ingest_blob(row)
        for phrase in TARGETED_INGEST_FORBIDDEN_SYNTHESIS:
            if phrase in blob:
                errors.append(f"{prefix}: synthesis phrase {phrase!r} is normalization")

    if source_ids != expected_sources:
        errors.append("targeted ingest source_ids must match selected_loci in order")

    marchant = by_source.get("src.byu.marchant.2025.square")
    if marchant:
        if marchant.get("does_not_generalize_author_contrast") is not True:
            errors.append("Marchant must declare author contrast is not a family definition")
        if marchant.get("claim_scope") != "experimental_named_conditions":
            errors.append("Marchant claim_scope must be experimental_named_conditions")
        variants = _as_str_list(marchant.get("observed_variants"), allow_empty=True) or []
        if variants:
            errors.append("Marchant must not declare observed_variants this pass")
        named = marchant.get("observed_named_conditions")
        if not isinstance(named, list) or len(named) != 2:
            errors.append("Marchant must record square and 5:5 as separate named conditions")
        else:
            names = [c.get("name_in_source") for c in named if isinstance(c, dict)]
            if names != ["Square breathing", "5:5 breathing"]:
                errors.append("Marchant named conditions must be Square breathing then 5:5 breathing")
            square = named[0] if isinstance(named[0], dict) else {}
            five = named[1] if isinstance(named[1], dict) else {}
            if square.get("holds") != "after_inhale_and_after_exhale":
                errors.append("Marchant square must observe holds after inhale and after exhale")
            if five.get("holds") != "none_written":
                errors.append("Marchant 5:5 must observe that holds are not written")
        contrast = marchant.get("observed_contrast_condition")
        if not isinstance(contrast, dict):
            errors.append("Marchant must store 5:5 as a separate contrast condition")
        else:
            contrast_blob = " ".join(
                _as_str_list(contrast.get("observed_steps"), allow_empty=True) or []
            ).lower()
            if "hold" in contrast_blob and "does not write a hold" not in contrast_blob:
                errors.append("Marchant 5:5 contrast must not add holds the methods did not write")
        tags = _as_str_list(marchant.get("conflict_tags"), allow_empty=True) or []
        if "author_contrast_not_family_definition" not in tags:
            errors.append("Marchant must tag author contrast as not a family definition")

    cavuhb = by_source.get("src.nhs.wales.cavuhb.square")
    if cavuhb:
        if cavuhb.get("does_not_treat_unequal_counts_as_variant") is not True:
            errors.append("CAVUHB must not treat unequal counts as a variant")
        if cavuhb.get("claim_scope") != "method_sequence_and_label":
            errors.append("CAVUHB claim_scope must be method_sequence_and_label")
        variants = _as_str_list(cavuhb.get("observed_variants"), allow_empty=True) or []
        if variants:
            errors.append("CAVUHB must not declare observed_variants this pass")
        tags = _as_str_list(cavuhb.get("conflict_tags"), allow_empty=True) or []
        if "recorded_as_label_observation_not_variant" not in tags:
            errors.append("CAVUHB must be tagged as label observation, not variant")
        steps_blob = " ".join(
            _as_str_list(cavuhb.get("observed_steps"), allow_empty=True) or []
        ).lower()
        if "six" not in steps_blob or "two" not in steps_blob:
            errors.append("CAVUHB must observe the 4-4-6-2 counts")

    return errors


V1_1_HOLD_DECISIONS = frozenset({"required", "optional", "unresolved"})
V1_1_EQUAL_DECISIONS = frozenset(
    {"identity_bearing", "common_parameter", "unresolved"}
)
V1_1_EVIDENCE = (
    "ev.equal_count.bhf.heart_matters.box",
    "ev.equal_count.nhs_sfh.box_leaflet",
    "ev.equal_count.nhs_newcastle.square",
    "ev.equal_count.byu.marchant.2025.square",
    "ev.equal_count.nhs_wales.cavuhb.square",
)
LANDSCAPE_V1_EQUAL_COUNT_SHAPE = (
    "four equal phases including pauses; ratio identity is the kernel"
)


def validate_technique_normalization_v1_1(
    normalization: dict[str, Any],
    *,
    family_ingest: dict[str, Any] | None = None,
    targeted_ingest: dict[str, Any] | None = None,
    landscape: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if normalization.get("contract_version") != "technique_normalization_v1_1":
        errors.append("invalid technique normalization v1.1 contract_version")
    if normalization.get("writes_technique_canon") is not False:
        errors.append("V1.1 must not write technique canon")
    if normalization.get("technique_id_allowed") is not False:
        errors.append("V1.1 must not allow technique_id")
    if normalization.get("normalize_one_is_not_canonical") is not True:
        errors.append("normalize_one must remain not-canonical")
    if normalization.get("does_not_erase_v1") is not True:
        errors.append("V1.1 must not erase the V1 insufficient_evidence record")
    if normalization.get("family_id") != SLICE_FAMILY_V1:
        errors.append(f"V1.1 family_id must stay {SLICE_FAMILY_V1} as ledger key")
    if normalization.get("family_id_is_ledger_key_not_identity_claim") is not True:
        errors.append("family_id must be declared a ledger key, not the identity claim")
    if normalization.get("boundary_held") != (
        "ingested_evidence_to_normalized_candidate_not_canonical"
    ):
        errors.append("boundary_held must record evidence→candidate, not canon")
    prior = normalization.get("prior_decision")
    if not isinstance(prior, dict) or prior.get("decision") != "insufficient_evidence":
        errors.append("V1.1 must record V1 insufficient_evidence as prior_decision")

    expected_ids = list(V1_1_EVIDENCE)
    if family_ingest or targeted_ingest:
        expected_ids = []
        for blob in (family_ingest, targeted_ingest):
            if not blob:
                continue
            rows = blob.get("evidence")
            if isinstance(rows, list):
                expected_ids.extend(
                    str(row.get("evidence_id"))
                    for row in rows
                    if isinstance(row, dict) and row.get("evidence_id")
                )
    if normalization.get("evidence_ids") != expected_ids:
        errors.append("evidence_ids must be family ingest then targeted ingest, in order")

    axes = normalization.get("axes")
    if not isinstance(axes, dict) or tuple(axes.keys()) != ("post_exhale_hold", "equal_count"):
        errors.append("axes must be post_exhale_hold then equal_count")
        return errors
    hold = axes.get("post_exhale_hold") if isinstance(axes.get("post_exhale_hold"), dict) else {}
    equal = axes.get("equal_count") if isinstance(axes.get("equal_count"), dict) else {}
    if hold.get("decision") not in V1_1_HOLD_DECISIONS:
        errors.append("post_exhale_hold decision invalid")
    if equal.get("decision") not in V1_1_EQUAL_DECISIONS:
        errors.append("equal_count decision invalid")
    if hold.get("not_used") != "locus count":
        errors.append("hold axis must not use locus count")
    if equal.get("not_used") != "locus count":
        errors.append("equal_count axis must not use locus count")
    if hold.get("decision") != "required":
        errors.append("this corpus must close post_exhale_hold as required under N-H1")
    if hold.get("criterion") != "N-H1":
        errors.append("hold criterion must be N-H1")
    if equal.get("decision") != "common_parameter":
        errors.append("this corpus must close equal_count as common_parameter under N-E2")
    if equal.get("criterion") != "N-E2":
        errors.append("equal_count criterion must be N-E2")

    decision = normalization.get("decision")
    if decision not in NORMALIZATION_DECISIONS:
        errors.append("decision must be normalize_one, split_family, or insufficient_evidence")
    if hold.get("decision") == "unresolved" and decision != "insufficient_evidence":
        errors.append("unresolved hold requires overall insufficient_evidence")
    if decision != "normalize_one":
        errors.append("this V1.1 corpus must close as normalize_one")
    if decision == "normalize_one" and (
        hold.get("decision") == "unresolved" or equal.get("decision") == "unresolved"
    ):
        errors.append("normalize_one requires both axes resolved")

    candidate = normalization.get("normalized_candidate")
    if not isinstance(candidate, dict):
        errors.append("normalize_one requires a normalized_candidate object")
    else:
        if candidate.get("status") != "normalized_candidate":
            errors.append("candidate status must be normalized_candidate")
        if candidate.get("not_canonical") is not True:
            errors.append("candidate must declare not_canonical")
        kernel = candidate.get("identity_kernel")
        if not isinstance(kernel, dict):
            errors.append("identity_kernel must be object")
        else:
            if kernel.get("post_exhale_hold") != "required":
                errors.append("candidate kernel must keep post_exhale_hold required")
            if kernel.get("equal_count") != "common_parameter":
                errors.append("candidate kernel must keep equal_count as common_parameter")
            if kernel.get("shape") != "four_timed_phases":
                errors.append("candidate kernel shape must be four_timed_phases")
        not_in = candidate.get("not_in_kernel")
        if not isinstance(not_in, list) or len(not_in) < 2:
            errors.append("candidate must record Newcastle and 5:5 as not-in-kernel")

    remap = normalization.get("landscape_remap")
    if not isinstance(remap, dict):
        errors.append("normalize_one on this family requires landscape_remap")
    else:
        if remap.get("family_id_unchanged") != SLICE_FAMILY_V1:
            errors.append("remap must keep family_id as ledger key")
        if "ratio identity is the kernel" not in str(remap.get("from_hypothesis") or ""):
            errors.append("remap must cite the landscape V1 equal-count hypothesis")
        if "common parameter" not in str(remap.get("to_hypothesis") or "").lower():
            errors.append("remap must move equal duration to a common parameter")

    if normalization.get("next_named_pass") != "technique_safety_review_v1":
        errors.append("next_named_pass after normalize_one must be safety review")
    not_next = normalization.get("not_next")
    if not isinstance(not_next, list) or "canonical" not in not_next:
        errors.append("not_next must include canonical")

    blob = " ".join(
        [
            str(hold.get("decision") or ""),
            " ".join(str(x) for x in (normalization.get("why_normalize_one") or [])),
            " ".join(str(x) for x in (normalization.get("why_not_split_family") or [])),
        ]
    ).lower()
    if "optional hold" in blob or "second hold is optional" in blob:
        errors.append("must not declare an optional hold")
    if not isinstance(normalization.get("why_not_split_family"), list) or len(
        normalization.get("why_not_split_family") or []
    ) < 2:
        errors.append("must record why_not_split_family")

    if landscape:
        families = landscape.get("families")
        eq = None
        if isinstance(families, list):
            eq = next(
                (
                    row
                    for row in families
                    if isinstance(row, dict)
                    and row.get("family_id") == SLICE_FAMILY_V1
                ),
                None,
            )
        if not isinstance(eq, dict):
            errors.append("landscape missing equal_count family")
        else:
            if eq.get("normalization_status") != "normalize_one":
                errors.append("landscape normalization_status must follow V1.1")
            if eq.get("mechanism_shape_at_landscape_v1") != LANDSCAPE_V1_EQUAL_COUNT_SHAPE:
                errors.append("landscape must preserve the V1 mechanism_shape beside the remap")
            shape = str(eq.get("mechanism_shape") or "").lower()
            if "four timed phases" not in shape or "common parameter" not in shape:
                errors.append("landscape mechanism_shape must be the remapped four-phase hypothesis")
            if str(eq.get("mechanism_shape") or "").startswith("four equal phases"):
                errors.append("current mechanism_shape must not remain the premature equal-count kernel")

    hypothesis = normalization.get("expression_hypothesis")
    if not isinstance(hypothesis, dict) or hypothesis.get("status") != "not_attested":
        errors.append("expression hypothesis must stay not_attested")

    return errors


SAFETY_REVIEW_DECISIONS = frozenset(
    {"may_release", "insufficient_safety", "may_not_release"}
)
SAFETY_REVIEW_AXIS_IDS = (
    "bounds",
    "stop_rules",
    "who_must_not_hold",
    "prohibition",
    "claim_surface",
)
WHO_UNKNOWN_MARKERS = (
    "does not state who should avoid",
    "not a general who-must-not-hold",
)
PROHIBITION_MARKERS = (
    "must not offer",
    "must not release",
    "do not publish this",
    "product must not",
)


def _safety_evidence_rows(
    family_ingest: dict[str, Any] | None,
    targeted_ingest: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for blob in (family_ingest, targeted_ingest):
        if not blob:
            continue
        evidence = blob.get("evidence")
        if isinstance(evidence, list):
            rows.extend(row for row in evidence if isinstance(row, dict))
    return rows


def _safety_blob(row: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("observed_bounds", "observed_safety"):
        values = row.get(key)
        if isinstance(values, list):
            parts.extend(str(item) for item in values)
    return " ".join(parts).lower()


def _who_must_not_from_corpus(rows: list[dict[str, Any]]) -> str:
    """closed if any locus states a hold exclusion; else unknown. Silence is not closed."""
    for row in rows:
        blob = _safety_blob(row)
        if any(marker in blob for marker in WHO_UNKNOWN_MARKERS):
            continue
        safety = row.get("observed_safety")
        if not isinstance(safety, list) or not safety:
            continue
        if "who-must-not" in blob or "must not hold" in blob or "should not hold" in blob:
            return "closed"
        # SFH stop-rules / redirect are not a population exclusion for required hold.
    return "unknown"


def _stop_rules_from_corpus(rows: list[dict[str, Any]]) -> str:
    for row in rows:
        if row.get("claim_scope") != "method_sequence_and_stop_rules":
            continue
        safety = row.get("observed_safety")
        steps = row.get("observed_steps")
        if not isinstance(safety, list) or not safety:
            continue
        step_text = " ".join(str(item) for item in steps).lower() if isinstance(steps, list) else ""
        if "grounding" in step_text:
            continue
        return "present"
    return "absent"


def _prohibition_from_corpus(rows: list[dict[str, Any]]) -> str:
    for row in rows:
        blob = _safety_blob(row)
        if any(marker in blob for marker in PROHIBITION_MARKERS):
            return "present"
    return "none"


def _expected_safety_decision(
    *,
    hold_required: bool,
    stop_rules: str,
    who_must_not: str,
    prohibition: str,
    claim_surface: str,
    bounds: str,
) -> str:
    if prohibition == "present":
        return "may_not_release"
    if hold_required and who_must_not != "closed":
        # S-B2: required hold without who-must-not is not may_release; missing ≠ ban.
        return "insufficient_safety"
    if (
        bounds == "recorded"
        and stop_rules == "present"
        and who_must_not == "closed"
        and claim_surface == "default_closed"
    ):
        return "may_release"
    return "insufficient_safety"


def validate_technique_safety_review_v1(
    review: dict[str, Any],
    *,
    family_ingest: dict[str, Any] | None = None,
    targeted_ingest: dict[str, Any] | None = None,
    normalization_v1_1: dict[str, Any] | None = None,
    landscape: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if review.get("contract_version") != "technique_safety_review_v1":
        errors.append("invalid technique safety review contract_version")
    if review.get("writes_technique_canon") is not False:
        errors.append("safety review must not write technique canon")
    if review.get("technique_id_allowed") is not False:
        errors.append("safety review must not allow technique_id")
    if review.get("safety_review_is_not_canonical") is not True:
        errors.append("safety review must remain not-canonical")
    if review.get("does_not_reopen_kernel") is not True:
        errors.append("safety review must not reopen the kernel")
    if review.get("does_not_erase_v1") is not True:
        errors.append("safety review must not erase the V1 insufficient_evidence record")
    if review.get("does_not_open_next_pass") is not True:
        errors.append("insufficient_safety must not auto-open a next named pass")
    if review.get("does_not_advance_to_safety_reviewed") is not True:
        errors.append("insufficient_safety must not advance review_status to safety_reviewed")
    if review.get("family_id") != SLICE_FAMILY_V1:
        errors.append(f"safety review family_id must stay {SLICE_FAMILY_V1} as ledger key")
    if review.get("family_id_is_ledger_key_not_identity_claim") is not True:
        errors.append("family_id must be declared a ledger key, not the identity claim")
    if review.get("boundary_held") != (
        "normalized_candidate_to_safety_verdict_not_canonical"
    ):
        errors.append("boundary_held must record candidate→verdict, not canon")

    prior = review.get("prior_decision")
    if not isinstance(prior, dict) or prior.get("decision") != "normalize_one":
        errors.append("safety review requires prior_decision normalize_one")

    kernel = review.get("identity_kernel_unchanged")
    if not isinstance(kernel, dict):
        errors.append("identity_kernel_unchanged must be object")
    else:
        if kernel.get("shape") != "four_timed_phases":
            errors.append("safety review must keep four_timed_phases")
        if kernel.get("post_exhale_hold") != "required":
            errors.append("safety review must not reopen hold as optional or unresolved")
        if kernel.get("equal_count") != "common_parameter":
            errors.append("safety review must keep equal_count as common_parameter")

    if normalization_v1_1:
        prior_kernel = (
            (normalization_v1_1.get("normalized_candidate") or {}).get("identity_kernel")
            if isinstance(normalization_v1_1.get("normalized_candidate"), dict)
            else None
        )
        if prior_kernel != kernel:
            errors.append("safety review kernel must match the V1.1 normalized candidate")

    expected_ids = list(V1_1_EVIDENCE)
    ingest_rows = _safety_evidence_rows(family_ingest, targeted_ingest)
    if ingest_rows:
        expected_ids = [
            str(row.get("evidence_id"))
            for row in ingest_rows
            if row.get("evidence_id")
        ]
    if review.get("evidence_ids") != expected_ids:
        errors.append("evidence_ids must be family ingest then targeted ingest, in order")

    axes = review.get("axes")
    if not isinstance(axes, dict) or tuple(axes.keys()) != SAFETY_REVIEW_AXIS_IDS:
        errors.append(
            "axes must be bounds, stop_rules, who_must_not_hold, prohibition, claim_surface"
        )
        return errors

    bounds = axes.get("bounds") if isinstance(axes.get("bounds"), dict) else {}
    stop_rules = axes.get("stop_rules") if isinstance(axes.get("stop_rules"), dict) else {}
    who = axes.get("who_must_not_hold") if isinstance(axes.get("who_must_not_hold"), dict) else {}
    prohibition = axes.get("prohibition") if isinstance(axes.get("prohibition"), dict) else {}
    claims = axes.get("claim_surface") if isinstance(axes.get("claim_surface"), dict) else {}

    if bounds.get("decision") not in {"recorded", "unresolved"}:
        errors.append("bounds decision invalid")
    if stop_rules.get("decision") not in {"present", "absent"}:
        errors.append("stop_rules decision invalid")
    if who.get("decision") not in {"closed", "unknown"}:
        errors.append("who_must_not_hold decision invalid")
    if prohibition.get("decision") not in {"none", "present"}:
        errors.append("prohibition decision invalid")
    if claims.get("decision") not in {"default_closed", "invalid_fill"}:
        errors.append("claim_surface decision invalid")
    if who.get("not_used") != "locus count":
        errors.append("who_must_not_hold must not use locus count")
    if who.get("locked_rule") != "S-B2":
        errors.append("who_must_not_hold must lock S-B2")
    if who.get("criterion") != "S-W2" and who.get("decision") == "unknown":
        errors.append("unknown who_must_not_hold must cite S-W2")
    if stop_rules.get("not_mixed_into_kernel") is not True and stop_rules.get("decision") == "present":
        errors.append("SFH stop-rules must stay out of the kernel")
    if stop_rules.get("evidence_id") != "ev.equal_count.nhs_sfh.box_leaflet" and (
        stop_rules.get("decision") == "present"
    ):
        errors.append("present stop-rules must cite the SFH evidence record")

    allowed = claims.get("allowed_claims")
    if not isinstance(allowed, list) or allowed:
        errors.append("allowed_claims must stay empty until a later claims review")
    if claims.get("efficacy_claim_level") != "not_claimed":
        errors.append("efficacy_claim_level must stay not_claimed")
    prohibited = claims.get("prohibited_claims")
    if not isinstance(prohibited, list) or len(prohibited) < 4:
        errors.append("prohibited_claims must include the provenance minimum")
    else:
        joined = " ".join(str(item).lower() for item in prohibited)
        for needle in ("treatment", "guaranteed", "anxiety", "manifestation"):
            if needle not in joined:
                errors.append(f"prohibited_claims missing {needle}")

    corpus_who = _who_must_not_from_corpus(ingest_rows) if ingest_rows else who.get("decision")
    corpus_stop = _stop_rules_from_corpus(ingest_rows) if ingest_rows else stop_rules.get("decision")
    corpus_ban = _prohibition_from_corpus(ingest_rows) if ingest_rows else prohibition.get("decision")
    if ingest_rows:
        if who.get("decision") != corpus_who:
            errors.append("who_must_not_hold must follow the ingested corpus, not a pre-written result")
        if stop_rules.get("decision") != corpus_stop:
            errors.append("stop_rules must follow the ingested corpus")
        if prohibition.get("decision") != corpus_ban:
            errors.append("prohibition must follow the ingested corpus")

    expected = _expected_safety_decision(
        hold_required=kernel.get("post_exhale_hold") == "required" if isinstance(kernel, dict) else True,
        stop_rules=str(stop_rules.get("decision") or ""),
        who_must_not=str(who.get("decision") or ""),
        prohibition=str(prohibition.get("decision") or ""),
        claim_surface=str(claims.get("decision") or ""),
        bounds=str(bounds.get("decision") or ""),
    )
    decision = review.get("decision")
    if decision not in SAFETY_REVIEW_DECISIONS:
        errors.append("decision must be may_release, insufficient_safety, or may_not_release")
    elif decision != expected:
        errors.append(
            f"overall must apply the contract to the axes ({expected}), not a pre-written result"
        )

    if decision == "insufficient_safety" and review.get("candidate_review_status") != "normalized":
        errors.append("insufficient_safety must leave candidate_review_status normalized")
    if review.get("next_named_pass") != "owner_decides_next_named_pass":
        errors.append("insufficient_safety must not auto-open a next named pass")
    not_next = review.get("not_next")
    if not isinstance(not_next, list) or "canonical" not in not_next:
        errors.append("not_next must include canonical")
    if not isinstance(not_next, list) or "auto_open_targeted_safety_research" not in not_next:
        errors.append("not_next must include auto_open_targeted_safety_research")

    blob = " ".join(
        [
            " ".join(str(x) for x in (review.get("why_insufficient_safety") or [])),
            " ".join(str(x) for x in (review.get("why_not_may_release") or [])),
            " ".join(str(x) for x in (review.get("why_not_may_not_release") or [])),
            str(who.get("why_sfh_is_not_enough") or ""),
        ]
    ).lower()
    if "optional hold" in blob or "hold is optional" in blob:
        errors.append("must not declare an optional hold")
    if decision == "insufficient_safety":
        if not isinstance(review.get("why_not_may_release"), list) or not review.get(
            "why_not_may_release"
        ):
            errors.append("must record why_not_may_release")
        if not isinstance(review.get("why_not_may_not_release"), list) or not review.get(
            "why_not_may_not_release"
        ):
            errors.append("must record why_not_may_not_release")

    hypothesis = review.get("expression_hypothesis")
    if not isinstance(hypothesis, dict) or hypothesis.get("status") != "not_attested":
        errors.append("expression hypothesis must stay not_attested")

    if landscape:
        families = landscape.get("families")
        eq = None
        if isinstance(families, list):
            eq = next(
                (
                    row
                    for row in families
                    if isinstance(row, dict) and row.get("family_id") == SLICE_FAMILY_V1
                ),
                None,
            )
        if not isinstance(eq, dict):
            errors.append("landscape missing equal_count family")
        else:
            if eq.get("mechanism_shape_at_landscape_v1") != LANDSCAPE_V1_EQUAL_COUNT_SHAPE:
                errors.append("landscape must preserve the V1 mechanism_shape beside the remap")
            if eq.get("normalization_status") != "normalize_one":
                errors.append("landscape normalization_status must remain normalize_one")
            if eq.get("safety_review_status") != decision:
                errors.append("landscape safety_review_status must follow this review decision")

    return errors


SAFETY_SHORTLIST_STOP = frozenset(
    {
        "preferred_class_hold_evidence_found_for_targeted_safety_ingest",
        "unresolved_only_general_breathwork_precautions",
        "structural_finding_universal_who_list_incorrect",
    }
)
SAFETY_SHORTLIST_SPEECH = frozenset(
    {
        "hold_exclusion",
        "hold_precaution",
        "general_breathwork_precaution",
        "experimental_script",
        "none",
    }
)
SAFETY_SHORTLIST_SELECTABLE_SPEECH = frozenset({"hold_exclusion", "hold_precaution"})
SAFETY_SHORTLIST_SELECTABLE_FAMILIES = frozenset(
    {"official_health", "clinical_psychology", "academic_description"}
)
SAFETY_SHORTLIST_REQUIRED = (
    "source_id",
    "source_family",
    "bibliographic_identity",
    "authority_provenance",
    "locus",
    "gates",
    "extractable",
    "safety_speech",
    "conflicts_unknowns",
    "research_function",
    "selection_decision",
    "rejection_reason",
)
ALREADY_INGESTED_SAFETY_SOURCE_IDS = (
    "src.bhf.heart_matters.box",
    "src.nhs.sfh.box_leaflet",
    "src.nhs.newcastle.square",
    "src.byu.marchant.2025.square",
    "src.nhs.wales.cavuhb.square",
)


def _safety_shortlist_already_expected(
    family_ingest: dict[str, Any] | None,
    targeted_ingest: dict[str, Any] | None,
) -> list[str]:
    expected: list[str] = []
    for blob in (family_ingest, targeted_ingest):
        if not blob:
            continue
        rows = blob.get("evidence")
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            ref = row.get("source_ref")
            if isinstance(ref, dict) and ref.get("source_id"):
                expected.append(str(ref.get("source_id")))
    return expected or list(ALREADY_INGESTED_SAFETY_SOURCE_IDS)


def validate_technique_targeted_safety_shortlist_v1(
    targeted: dict[str, Any],
    *,
    family_ingest: dict[str, Any] | None = None,
    targeted_ingest: dict[str, Any] | None = None,
    normalization_v1_1: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if targeted.get("contract_version") != "technique_targeted_safety_shortlist_v1":
        errors.append("invalid targeted safety shortlist contract_version")
    if targeted.get("writes_technique_canon") is not False:
        errors.append("targeted safety shortlist must not write technique canon")
    if targeted.get("technique_id_allowed") is not False:
        errors.append("targeted safety shortlist must not allow technique_id")
    if targeted.get("does_not_reopen_kernel") is not True:
        errors.append("must not reopen the kernel")
    if targeted.get("does_not_rewrite_safety_contract") is not True:
        errors.append("must not rewrite the Safety Review V1 contract")
    if targeted.get("does_not_invent_who_list") is not True:
        errors.append("must not invent a product who-list")
    if targeted.get("unit_of_shortlist") != "research_question":
        errors.append("unit_of_shortlist must be research_question")
    if targeted.get("selected_means") != "allowed_for_targeted_safety_ingest_pass":
        errors.append("selected_means must be targeted safety ingest permission")
    if targeted.get("family_id") != SLICE_FAMILY_V1:
        errors.append(f"family_id must stay {SLICE_FAMILY_V1} as ledger key")
    question = str(targeted.get("research_question") or "").lower()
    if "breath hold" not in question and "who_must_not" not in question:
        errors.append("research_question must name required holds / who_must_not_hold")
    not_in_scope = targeted.get("not_in_scope")
    if not isinstance(not_in_scope, list) or "box_breathing_in_general" not in not_in_scope:
        errors.append("must declare box_breathing_in_general out of scope")
    if not isinstance(not_in_scope, list) or "kernel_rewrite" not in not_in_scope:
        errors.append("must declare kernel_rewrite out of scope")

    kernel = targeted.get("identity_kernel_unchanged")
    if not isinstance(kernel, dict):
        errors.append("identity_kernel_unchanged must be object")
    else:
        if kernel.get("post_exhale_hold") != "required":
            errors.append("must keep post_exhale_hold required")
        if kernel.get("shape") != "four_timed_phases":
            errors.append("must keep four_timed_phases")
    if normalization_v1_1:
        prior = (
            (normalization_v1_1.get("normalized_candidate") or {}).get("identity_kernel")
            if isinstance(normalization_v1_1.get("normalized_candidate"), dict)
            else None
        )
        if prior != kernel:
            errors.append("kernel must match the V1.1 normalized candidate")

    stop = targeted.get("stop_reason")
    if stop not in SAFETY_SHORTLIST_STOP:
        errors.append("stop_reason must be a declared stopping criterion")
    if targeted.get("next_named_pass") != "targeted_safety_ingest_who_must_not_hold":
        errors.append("next_named_pass must be targeted safety ingest")
    not_next = targeted.get("not_next")
    if not isinstance(not_next, list) or "canonical" not in not_next:
        errors.append("not_next must include canonical")
    if not isinstance(not_next, list) or "rewrite_safety_contract_inside_shortlist" not in not_next:
        errors.append("not_next must include rewrite_safety_contract_inside_shortlist")
    finding = str(targeted.get("structural_finding") or "").lower()
    if "who-list" not in finding and "who_must_not" not in finding:
        errors.append("must record a structural finding about the who-list field")

    hypothesis = targeted.get("expression_hypothesis")
    if not isinstance(hypothesis, dict) or hypothesis.get("status") != "not_attested":
        errors.append("expression hypothesis must stay not_attested")

    expected_already = _safety_shortlist_already_expected(family_ingest, targeted_ingest)
    if targeted.get("already_ingested_loci") != expected_already:
        errors.append("already_ingested_loci must match family then targeted ingest sources")

    loci = targeted.get("candidate_loci")
    if not isinstance(loci, list) or not loci:
        errors.append("candidate_loci must be non-empty list")
        return errors

    seen: set[str] = set()
    selected_ids: list[str] = []
    already_ids: list[str] = []
    selected_speech: set[str] = set()
    by_id: dict[str, dict[str, Any]] = {}
    for i, src in enumerate(loci):
        prefix = f"locus[{i}]"
        if not isinstance(src, dict):
            errors.append(f"{prefix}: must be object")
            continue
        for key in SAFETY_SHORTLIST_REQUIRED:
            if key not in src:
                errors.append(f"{prefix}: missing {key}")
        source_id = src.get("source_id")
        if not isinstance(source_id, str) or not source_id.startswith("src."):
            errors.append(f"{prefix}: source_id must start with src.")
        elif source_id in seen:
            errors.append(f"{prefix}: duplicate source_id")
        else:
            seen.add(source_id)
            by_id[source_id] = src
        decision = src.get("selection_decision")
        if decision not in {"selected", "supporting", "rejected", "already_ingested"}:
            errors.append(f"{prefix}: invalid selection_decision")
        elif decision == "selected":
            selected_ids.append(str(source_id))
            selected_speech.add(str(src.get("safety_speech")))
        elif decision == "already_ingested":
            already_ids.append(str(source_id))
        if decision == "rejected":
            reason = src.get("rejection_reason")
            if not isinstance(reason, str) or not reason.strip():
                errors.append(f"{prefix}: rejected must have rejection_reason")
        speech = src.get("safety_speech")
        if speech not in SAFETY_SHORTLIST_SPEECH:
            errors.append(f"{prefix}: invalid safety_speech")
        source_family = src.get("source_family")
        if decision in {"selected", "supporting", "already_ingested"}:
            if source_family not in ALLOWED_SOURCE_FAMILY:
                errors.append(f"{prefix}: source_family must be a provenance class")
        if decision == "selected":
            if speech not in SAFETY_SHORTLIST_SELECTABLE_SPEECH:
                errors.append(f"{prefix}: selected speech must be hold_exclusion or hold_precaution")
            if source_family not in SAFETY_SHORTLIST_SELECTABLE_FAMILIES:
                errors.append(
                    f"{prefix}: wellness/tradition/school cannot be selected for who_must_not_hold"
                )
            if speech == "general_breathwork_precaution":
                errors.append(f"{prefix}: general breathwork precaution must not be selected")
        gates = src.get("gates")
        if not isinstance(gates, dict):
            errors.append(f"{prefix}: gates must be object")
        else:
            if tuple(gates.keys()) != CRITERIA_GATE_IDS:
                errors.append(f"{prefix}: gates must be C1–C9")
            if decision == "selected":
                for gid in SHORTLIST_HARD_GATES:
                    result = (gates.get(gid) or {}).get("result")
                    if result != "pass":
                        errors.append(f"{prefix}: selected requires {gid}=pass")
        extractable = src.get("extractable")
        if not isinstance(extractable, dict):
            errors.append(f"{prefix}: extractable must be object")
        blob = " ".join(
            [
                str(src.get("conflicts_unknowns") or ""),
                str((extractable or {}).get("kernel") or ""),
                str(src.get("research_function") or ""),
            ]
        ).lower()
        if "optional hold" in blob or "hold is optional" in blob:
            errors.append(f"{prefix}: must not declare an optional hold")

    listed = targeted.get("selected_loci")
    if not isinstance(listed, list) or listed != selected_ids:
        errors.append("selected_loci must match loci with selection_decision=selected")
    if already_ids != expected_already:
        errors.append("already_ingested candidate rows must match already_ingested_loci")

    if (
        stop == "preferred_class_hold_evidence_found_for_targeted_safety_ingest"
        and not selected_ids
    ):
        errors.append("stop A requires at least one selected hold_exclusion or hold_precaution")
    if stop == "unresolved_only_general_breathwork_precautions" and selected_ids:
        errors.append("stop B cannot select hold loci")

    kinds = targeted.get("safety_speech_found")
    if not isinstance(kinds, list) or set(kinds) != selected_speech:
        errors.append("safety_speech_found must match selected speech acts")

    healthline = by_id.get("src.healthline.box")
    if healthline and healthline.get("selection_decision") != "rejected":
        errors.append("wellness Healthline must be rejected for who_must_not_hold")
    bts = by_id.get("src.bts.2009.physio_spontaneously_breathing")
    if bts:
        if bts.get("selection_decision") != "supporting":
            errors.append("BTS exertion advice must stay supporting, not selected")
        if bts.get("safety_speech") != "general_breathwork_precaution":
            errors.append("BTS is general_breathwork_precaution, not hold_exclusion for this candidate")
    joshi = by_id.get("src.wjm.joshi.2024.yoga_hypertension")
    if joshi:
        if joshi.get("selection_decision") != "selected":
            errors.append("Joshi 2024 kumbhaka exclusion must be selected")
        if joshi.get("safety_speech") != "hold_exclusion":
            errors.append("Joshi 2024 speech must be hold_exclusion")
    nive = by_id.get("src.nivethitha.2017.bahir_kumbhaka")
    if nive:
        if nive.get("selection_decision") != "selected":
            errors.append("Nivethitha 2017 must be selected as hold_precaution")
        if nive.get("safety_speech") != "hold_precaution":
            errors.append("Nivethitha 2017 speech must be hold_precaution")

    return errors


SAFETY_INGEST_REQUIRED = (
    "evidence_id",
    "candidate_family",
    "source_ref",
    "locus",
    "source_family",
    "paraphrase",
    "speech_type",
    "named_practice",
    "practice_context",
    "hold_phase",
    "dose_or_duration",
    "population",
    "observed_exclusions",
    "observed_precautions",
    "observed_physiology",
    "transfer_limits",
    "source_claim_scope",
    "ingest_status",
)
SAFETY_INGEST_SPEECH = frozenset(
    {"hold_exclusion", "observed_physiological_response"}
)
SAFETY_INGEST_CLAIM_SCOPE = frozenset(
    {
        "kumbhaka_exclusion_statements_in_yoga_hypertension_review",
        "acute_cardiovascular_response_during_bahir_kumbhaka",
    }
)
SAFETY_INGEST_FORBIDDEN_SYNTHESIS = INGEST_FORBIDDEN_SYNTHESIS + (
    "who_must_not_hold =",
    "contraindicated for box",
    "contraindicated for square",
    "box breathing is contraindicated",
    "square breathing is contraindicated",
    "may_release",
)
JOSHI_TRANSFER_LIMITS = (
    "kumbhaka is not four-phase square breathing",
    "unspecified or long retention is not a short timed hold",
)
NIVETHITHA_TRANSFER_LIMITS = (
    "empty-lung retention is physiologically closer to a post-exhale hold but is not the product dose",
    "study response is not a contraindication",
)


def _safety_ingest_blob(row: dict[str, Any]) -> str:
    return " ".join(
        [
            str(row.get("paraphrase") or ""),
            str(row.get("named_practice") or ""),
            str(row.get("practice_context") or ""),
            str(row.get("hold_phase") or ""),
            str(row.get("dose_or_duration") or ""),
            str(row.get("population") or ""),
            str(row.get("source_claim_scope") or ""),
        ]
    ).lower()


def validate_technique_targeted_safety_ingest_v1(
    ingest: dict[str, Any],
    *,
    targeted_safety_shortlist: dict[str, Any] | None = None,
    normalization_v1_1: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if ingest.get("contract_version") != "technique_targeted_safety_ingest_v1":
        errors.append("invalid targeted safety ingest contract_version")
    if ingest.get("writes_technique_canon") is not False:
        errors.append("targeted safety ingest must not write technique canon")
    if ingest.get("technique_id_allowed") is not False:
        errors.append("targeted safety ingest must not allow technique_id")
    if ingest.get("does_not_reopen_kernel") is not True:
        errors.append("must not reopen the kernel")
    if ingest.get("does_not_rewrite_safety_contract") is not True:
        errors.append("must not rewrite the Safety Review V1 contract")
    if ingest.get("does_not_write_who_must_not_hold") is not True:
        errors.append("must not write who_must_not_hold")
    if ingest.get("does_not_write_safety_rules") is not True:
        errors.append("must not write new product safety rules")
    if ingest.get("does_not_transfer_onto_four_phase_candidate") is not True:
        errors.append("must not transfer other-context evidence onto the four-phase candidate")
    if ingest.get("family_id") != SLICE_FAMILY_V1:
        errors.append(f"family_id must stay {SLICE_FAMILY_V1} as ledger key")
    if ingest.get("boundary_held") != (
        "selected_safety_loci_to_source_faithful_observations_not_contraindication_list"
    ):
        errors.append("boundary_held must record selected loci→observations, not a who-list")
    if ingest.get("next_named_pass") != "technique_safety_review_v1_1":
        errors.append("next_named_pass must be Safety Review V1.1")
    not_next = ingest.get("not_next")
    if not isinstance(not_next, list) or "canonical" not in not_next:
        errors.append("not_next must include canonical")
    if not isinstance(not_next, list) or "write_who_must_not_hold" not in not_next:
        errors.append("not_next must include write_who_must_not_hold")
    if not isinstance(not_next, list) or "may_release" not in not_next:
        errors.append("not_next must include may_release")

    kernel = ingest.get("identity_kernel_unchanged")
    if not isinstance(kernel, dict):
        errors.append("identity_kernel_unchanged must be object")
    else:
        if kernel.get("post_exhale_hold") != "required":
            errors.append("must keep post_exhale_hold required")
        if kernel.get("shape") != "four_timed_phases":
            errors.append("must keep four_timed_phases")
    if normalization_v1_1:
        prior = (
            (normalization_v1_1.get("normalized_candidate") or {}).get("identity_kernel")
            if isinstance(normalization_v1_1.get("normalized_candidate"), dict)
            else None
        )
        if prior != kernel:
            errors.append("kernel must match the V1.1 normalized candidate")

    questions = ingest.get("v1_1_questions_not_decided")
    if not isinstance(questions, list) or len(questions) != 2:
        errors.append("v1_1_questions_not_decided must lock two unanswered questions")
    else:
        by_qid = {q.get("id"): q for q in questions if isinstance(q, dict)}
        release = by_qid.get("enough_for_may_release") or {}
        model = by_qid.get("binary_who_must_not_hold_still_correct_model") or {}
        if release.get("status") != "unanswered":
            errors.append("enough_for_may_release must stay unanswered this pass")
        if model.get("status") != "unanswered":
            errors.append("binary who_must_not_hold model question must stay unanswered")
        if model.get("later_structural_model_first_allowed_at") != (
            "technique_safety_review_v1_1"
        ):
            errors.append("exclusion/precaution/stop_rule is first allowed at Safety Review V1.1")

    hypothesis = ingest.get("expression_hypothesis")
    if not isinstance(hypothesis, dict) or hypothesis.get("status") != "not_attested":
        errors.append("expression hypothesis must stay not_attested")

    expected_sources = [
        "src.wjm.joshi.2024.yoga_hypertension",
        "src.nivethitha.2017.bahir_kumbhaka",
    ]
    if targeted_safety_shortlist:
        listed = targeted_safety_shortlist.get("selected_loci")
        if isinstance(listed, list) and all(isinstance(x, str) for x in listed):
            expected_sources = listed

    rows = ingest.get("evidence")
    if not isinstance(rows, list) or len(rows) != 2:
        errors.append("targeted safety ingest must contain exactly two evidence records")
        return errors

    seen_ids: set[str] = set()
    source_ids: list[str] = []
    by_source: dict[str, dict[str, Any]] = {}
    for i, row in enumerate(rows):
        prefix = f"evidence[{i}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix}: must be object")
            continue
        for key in SAFETY_INGEST_REQUIRED:
            if key not in row:
                errors.append(f"{prefix}: missing {key}")
        evidence_id = row.get("evidence_id")
        if not isinstance(evidence_id, str) or not evidence_id.startswith("ev.safety."):
            errors.append(f"{prefix}: evidence_id must start with ev.safety.")
        elif evidence_id in seen_ids:
            errors.append(f"{prefix}: duplicate evidence_id")
        else:
            seen_ids.add(evidence_id)
        if row.get("candidate_family") != SLICE_FAMILY_V1:
            errors.append(f"{prefix}: candidate_family must be the slice family ledger key")
        if row.get("source_family") not in ALLOWED_SOURCE_FAMILY:
            errors.append(f"{prefix}: invalid source_family")
        if row.get("ingest_status") != "ingested":
            errors.append(f"{prefix}: ingest_status must be ingested")
        if row.get("speech_type") not in SAFETY_INGEST_SPEECH:
            errors.append(f"{prefix}: invalid speech_type")
        if row.get("source_claim_scope") not in SAFETY_INGEST_CLAIM_SCOPE:
            errors.append(f"{prefix}: invalid source_claim_scope")
        if row.get("is_not_who_must_not_hold_candidate") is not True:
            errors.append(f"{prefix}: must declare is_not_who_must_not_hold_candidate")
        source_ref = row.get("source_ref")
        if not isinstance(source_ref, dict):
            errors.append(f"{prefix}: source_ref must be object")
            continue
        source_id = source_ref.get("source_id")
        if not isinstance(source_id, str) or not source_id.startswith("src."):
            errors.append(f"{prefix}: source_ref.source_id invalid")
        else:
            source_ids.append(source_id)
            by_source[source_id] = row
        if not isinstance(row.get("paraphrase"), str) or not str(row.get("paraphrase") or "").strip():
            errors.append(f"{prefix}: paraphrase empty")
        if not isinstance(row.get("locus"), str) or not str(row.get("locus") or "").strip():
            errors.append(f"{prefix}: locus empty")
        if not isinstance(row.get("named_practice"), str) or not str(
            row.get("named_practice") or ""
        ).strip():
            errors.append(f"{prefix}: named_practice empty")
        if _as_str_list(row.get("transfer_limits"), allow_empty=False) is None:
            errors.append(f"{prefix}: transfer_limits must be a non-empty string list")
        if _as_str_list(row.get("observed_precautions"), allow_empty=True) is None:
            errors.append(f"{prefix}: observed_precautions must be a list")
        exclusions = row.get("observed_exclusions")
        if not isinstance(exclusions, list):
            errors.append(f"{prefix}: observed_exclusions must be list")
        physiology = row.get("observed_physiology")
        if not isinstance(physiology, list):
            errors.append(f"{prefix}: observed_physiology must be list")
        blob = _safety_ingest_blob(row)
        for phrase in SAFETY_INGEST_FORBIDDEN_SYNTHESIS:
            if phrase in blob:
                errors.append(f"{prefix}: synthesis phrase {phrase!r} is a product rule")
        if "1 min" in blob or "1-minute" in blob or "60 s" in blob:
            errors.append(f"{prefix}: must not import hold duration from other papers")

    if source_ids != expected_sources:
        errors.append("targeted safety ingest source_ids must match selected_loci in order")

    joshi = by_source.get("src.wjm.joshi.2024.yoga_hypertension")
    if joshi:
        if joshi.get("speech_type") != "hold_exclusion":
            errors.append("Joshi speech_type must be hold_exclusion")
        if joshi.get("practice_context") != "kumbhaka":
            errors.append("Joshi practice_context must be kumbhaka")
        named = str(joshi.get("named_practice") or "").lower()
        if "kumbhaka" not in named:
            errors.append("Joshi named_practice must be kumbhaka")
        if "box" in named or "square" in named:
            errors.append("Joshi named_practice must not be box/square")
        if joshi.get("dose_or_duration") != "unspecified_in_this_locus":
            errors.append("Joshi dose_or_duration must stay unspecified in this locus")
        exclusions = joshi.get("observed_exclusions")
        if not isinstance(exclusions, list) or len(exclusions) != 3:
            errors.append("Joshi must record three observed exclusion statements")
        else:
            conditions = [
                str(item.get("condition") or "").lower()
                for item in exclusions
                if isinstance(item, dict)
            ]
            blob = " ".join(conditions)
            for needed in ("hypertension", "heart disease", "illness"):
                if needed not in blob:
                    errors.append(f"Joshi exclusions must include {needed}")
            for item in exclusions:
                if not isinstance(item, dict):
                    continue
                if item.get("practice_context") != "kumbhaka":
                    errors.append("Joshi exclusion practice_context must stay kumbhaka")
                if item.get("is_not_product_who_must_not_hold") is not True:
                    errors.append("Joshi exclusions are not a product who-list")
        limits = _as_str_list(joshi.get("transfer_limits"), allow_empty=False) or []
        for needed in JOSHI_TRANSFER_LIMITS:
            if needed not in limits:
                errors.append(f"Joshi transfer_limits must include {needed!r}")
        if joshi.get("source_claim_scope") != (
            "kumbhaka_exclusion_statements_in_yoga_hypertension_review"
        ):
            errors.append("Joshi source_claim_scope must stay on kumbhaka exclusion statements")

    nive = by_source.get("src.nivethitha.2017.bahir_kumbhaka")
    if nive:
        if nive.get("speech_type") != "observed_physiological_response":
            errors.append("Nivethitha speech_type must be observed_physiological_response")
        if nive.get("practice_context") != "bahir_kumbhaka":
            errors.append("Nivethitha practice_context must be bahir_kumbhaka")
        if nive.get("hold_phase") != "external_empty_lung_retention":
            errors.append("Nivethitha hold_phase must be external empty-lung retention")
        if nive.get("dose_or_duration") != "unspecified_in_this_legally_readable_locus":
            errors.append("Nivethitha dose_or_duration must stay unspecified in this locus")
        exclusions = nive.get("observed_exclusions")
        if exclusions != []:
            errors.append("Nivethitha must not write an exclusion list")
        physiology = nive.get("observed_physiology")
        if not isinstance(physiology, list) or len(physiology) < 3:
            errors.append("Nivethitha must record SBP/DBP/MAP observations")
        else:
            measures = {
                str(item.get("measure") or "")
                for item in physiology
                if isinstance(item, dict)
            }
            if not {"SBP", "DBP", "MAP"} <= measures:
                errors.append("Nivethitha physiology must include SBP, DBP, and MAP")
        limits = _as_str_list(nive.get("transfer_limits"), allow_empty=False) or []
        for needed in NIVETHITHA_TRANSFER_LIMITS:
            if needed not in limits:
                errors.append(f"Nivethitha transfer_limits must include {needed!r}")
        if nive.get("source_claim_scope") != (
            "acute_cardiovascular_response_during_bahir_kumbhaka"
        ):
            errors.append("Nivethitha source_claim_scope must stay on acute physiology")

    return errors


def validate_content_library_v1(
    library: dict[str, Any],
    *,
    vocab: dict[str, Any],
    coverage: dict[str, Any] | None = None,
    techniques: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if library.get("contract_version") != "content_library_v1":
        errors.append("invalid library contract_version")
    items = library.get("items")
    if not isinstance(items, list):
        errors.append("items must be list")
        return errors

    seen_ids: set[str] = set()
    by_id: dict[str, dict[str, Any]] = {}
    for i, item in enumerate(items):
        prefix = f"item[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: must be object")
            continue
        identity = item.get("identity") if isinstance(item.get("identity"), dict) else {}
        item_id = str(identity.get("item_id") or "")
        if item_id:
            if item_id in seen_ids:
                errors.append(f"{prefix}: duplicate item_id {item_id!r}")
            seen_ids.add(item_id)
            by_id[item_id] = item
        errors.extend(validate_content_item_v1(item, vocab=vocab, prefix=prefix or item_id))

    probe_ids = library.get("architecture_probe_item_ids")
    if probe_ids is not None:
        if not isinstance(probe_ids, list) or not all(
            isinstance(x, str) and x.strip() for x in probe_ids
        ):
            errors.append("architecture_probe_item_ids must be string list")
        else:
            if len(probe_ids) != ARCHITECTURE_PROBE_COUNT:
                errors.append(
                    f"architecture_probe_item_ids must list {ARCHITECTURE_PROBE_COUNT} items"
                )
            for iid in probe_ids:
                if iid not in seen_ids:
                    errors.append(f"architecture_probe unknown item_id {iid!r}")

    if library.get("fill_frozen") is True and not (
        isinstance(probe_ids, list) and probe_ids
    ):
        errors.append("fill_frozen library requires architecture_probe_item_ids")
    if techniques is not None:
        errors.extend(validate_technique_canon_v1(techniques))
        technique_rows = [
            row
            for row in techniques.get("techniques") or []
            if isinstance(row, dict) and isinstance(row.get("technique_id"), str)
        ]
        accepted_ids = {
            row["technique_id"]
            for row in technique_rows
            if row.get("status") == "accepted"
        }
        skipped_ids = {
            row["technique_id"]
            for row in technique_rows
            if row.get("status") == "skipped"
        }
        for iid, item in by_id.items():
            identity = item.get("identity") if isinstance(item.get("identity"), dict) else {}
            tid = identity.get("technique_id")
            if not isinstance(tid, str):
                continue
            if tid in skipped_ids:
                errors.append(f"item {iid} must not attach skipped technique_id {tid!r}")
            elif tid not in accepted_ids:
                errors.append(f"item {iid} technique_id {tid!r} not in technique canon")

    if coverage is None:
        return errors

    cells = coverage.get("need_cells")
    if not isinstance(cells, list):
        errors.append("coverage.need_cells must be list")
        return errors

    cells_by_item: dict[str, list[str]] = {}
    for cell in cells:
        if not isinstance(cell, dict):
            continue
        cell_id = str(cell.get("id") or "cell")
        item_ids = cell.get("item_ids") or []
        status = cell.get("status")
        if item_ids and status not in CELL_STATUS_FOR_ITEMS:
            errors.append(f"{cell_id}: has item_ids but status={status!r}")
        if not item_ids and status not in ("empty", None):
            errors.append(f"{cell_id}: empty item_ids but status={status!r}")
        for iid in item_ids:
            cells_by_item.setdefault(str(iid), []).append(cell_id)
            if iid not in by_id:
                errors.append(f"{cell_id}: unknown item_id {iid!r}")
                continue
            item = by_id[iid]
            identity = item["identity"]
            retrieval = item["retrieval"]
            if identity.get("seed_cell") and identity.get("seed_cell") != cell_id:
                errors.append(
                    f"{cell_id}: item {iid} seed_cell={identity.get('seed_cell')!r}"
                )
            primary = cell.get("primary") or {}
            alt = cell.get("alt") or {}
            form_ok = (
                identity.get("content_class") == primary.get("content_class")
                and identity.get("type") == primary.get("type")
            ) or (
                isinstance(alt, dict)
                and identity.get("content_class") == alt.get("content_class")
                and identity.get("type") == alt.get("type")
            )
            if not form_ok:
                errors.append(f"{cell_id}: item {iid} form is not primary/alt")
            if cell.get("purpose") not in (retrieval.get("purpose") or []):
                errors.append(f"{cell_id}: item {iid} missing purpose")
            if cell.get("direction") not in (retrieval.get("direction") or []):
                errors.append(f"{cell_id}: item {iid} missing direction")

    for iid, cell_ids in cells_by_item.items():
        if len(cell_ids) != 1:
            errors.append(f"item {iid} listed on {len(cell_ids)} cells {cell_ids}; seed-pass allows exactly one")

    for iid, item in by_id.items():
        identity = item.get("identity") or {}
        seed_cell = identity.get("seed_cell")
        if identity.get("status") == "draft" and seed_cell and iid not in cells_by_item:
            errors.append(f"item {iid} seed_cell={seed_cell!r} not listed on that cell")

    spine = coverage.get("type_spine") or []
    for row in spine:
        if not isinstance(row, dict):
            continue
        for iid in row.get("item_ids") or []:
            if iid not in by_id:
                errors.append(
                    f"type_spine {row.get('content_class')}.{row.get('type')}: unknown {iid}"
                )

    return errors


def first_empty_p0_cell(coverage: dict[str, Any]) -> dict[str, Any] | None:
    """Deterministic next seed target: first empty cell in ledger order."""
    cells = coverage.get("need_cells")
    if not isinstance(cells, list):
        return None
    for cell in cells:
        if isinstance(cell, dict) and cell.get("status") == "empty":
            return cell
    return None


def first_empty_p0_type(coverage: dict[str, Any]) -> dict[str, Any] | None:
    """After need cells are seeded: first P0 type_spine row with empty item_ids."""
    spine = coverage.get("type_spine")
    if not isinstance(spine, list):
        return None
    for row in spine:
        if (
            isinstance(row, dict)
            and row.get("phase") == "P0"
            and not (row.get("item_ids") or [])
        ):
            return row
    return None


def _retrieval_axis(item: dict[str, Any]) -> tuple[Any, ...]:
    retrieval = item.get("retrieval") if isinstance(item.get("retrieval"), dict) else {}
    return (
        retrieval.get("duration"),
        retrieval.get("duration_days"),
        tuple(retrieval.get("context") or []),
        tuple(retrieval.get("delivery") or []),
    )


def first_p0_type_needing_density(
    coverage: dict[str, Any],
    library: dict[str, Any],
) -> dict[str, Any] | None:
    """First P0 type in spine order with no same-cell duration/context/delivery sibling."""
    return _first_p0_type_missing_sibling(coverage, library, axis="retrieval")


def first_p0_type_needing_context_density(
    coverage: dict[str, Any],
    library: dict[str, Any],
) -> dict[str, Any] | None:
    """First P0 type with no same-cell sibling whose context set differs."""
    return _first_p0_type_missing_sibling(coverage, library, axis="context")


def _context_key(item: dict[str, Any]) -> tuple[str, ...]:
    retrieval = item.get("retrieval") if isinstance(item.get("retrieval"), dict) else {}
    return tuple(retrieval.get("context") or [])


def _first_p0_type_missing_sibling(
    coverage: dict[str, Any],
    library: dict[str, Any],
    *,
    axis: str,
) -> dict[str, Any] | None:
    items = {
        item.get("identity", {}).get("item_id"): item
        for item in library.get("items") or []
        if isinstance(item, dict)
    }
    spine = coverage.get("type_spine")
    if not isinstance(spine, list):
        return None
    for row in spine:
        if not isinstance(row, dict) or row.get("phase") != "P0":
            continue
        iids = [i for i in (row.get("item_ids") or []) if i]
        if not iids:
            continue
        first = items.get(iids[0])
        if not isinstance(first, dict):
            continue
        seed = (first.get("identity") or {}).get("seed_cell")
        key0 = _retrieval_axis(first) if axis == "retrieval" else _context_key(first)
        has_sibling = False
        for iid in iids[1:]:
            other = items.get(iid)
            if not isinstance(other, dict):
                continue
            if (other.get("identity") or {}).get("seed_cell") != seed:
                continue
            key = _retrieval_axis(other) if axis == "retrieval" else _context_key(other)
            if key != key0:
                has_sibling = True
                break
        if not has_sibling:
            return row
    return None


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"expected object in {path}")
    return payload
