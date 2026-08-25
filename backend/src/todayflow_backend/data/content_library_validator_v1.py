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
ARCHITECTURE_PROBE_COUNT = 11
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
    "source_family",
    "source_refs",
    "tradition",
    "evidence_level",
    "efficacy_claim_level",
    "canonical_mechanism",
    "canonical_steps",
    "safety_notes",
    "allowed_claims",
    "prohibited_claims",
    "review_status",
    "semantic_version",
)
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
        for key in TECHNIQUE_REQUIRED:
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
        if row.get("source_family") not in ALLOWED_SOURCE_FAMILY:
            errors.append(f"{prefix}: invalid source_family")
        if row.get("evidence_level") not in ALLOWED_EVIDENCE_LEVEL:
            errors.append(f"{prefix}: invalid evidence_level")
        if row.get("efficacy_claim_level") not in ALLOWED_EFFICACY_CLAIM_LEVEL:
            errors.append(f"{prefix}: invalid efficacy_claim_level")
        if row.get("review_status") not in ALLOWED_TECHNIQUE_REVIEW_STATUS:
            errors.append(f"{prefix}: invalid review_status")
        for list_key in (
            "source_refs",
            "tradition",
            "canonical_steps",
            "safety_notes",
            "allowed_claims",
            "prohibited_claims",
        ):
            value = row.get(list_key)
            if list_key == "source_refs":
                if not isinstance(value, list):
                    errors.append(f"{prefix}: {list_key} must be list")
                elif not all(isinstance(x, dict) for x in value):
                    errors.append(f"{prefix}: source_refs must be object list")
            elif _as_str_list(value, allow_empty=True) is None:
                errors.append(f"{prefix}: {list_key} must be string list")
        mechanism = row.get("canonical_mechanism")
        if not isinstance(mechanism, str) or not mechanism.strip():
            errors.append(f"{prefix}: canonical_mechanism must be non-empty string")
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
        errors.append("shortlist_opened must be false")
    if landscape.get("writes_technique_canon") is not False:
        errors.append("writes_technique_canon must be false")
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
        if row.get("shortlist_status") != "not_opened":
            errors.append(f"{prefix}: shortlist_status must be not_opened")
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
        technique_ids = {
            row["technique_id"]
            for row in techniques.get("techniques") or []
            if isinstance(row, dict) and isinstance(row.get("technique_id"), str)
        }
        for iid, item in by_id.items():
            identity = item.get("identity") if isinstance(item.get("identity"), dict) else {}
            tid = identity.get("technique_id")
            if isinstance(tid, str) and tid not in technique_ids:
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
