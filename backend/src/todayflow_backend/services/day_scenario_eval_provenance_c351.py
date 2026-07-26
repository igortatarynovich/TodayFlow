"""C3.5.1 — Provenance chain + day-closure contract scoring (eval-only)."""

from __future__ import annotations

import re
from typing import Any

from todayflow_backend.services.day_scenario_personalization_c33 import (
    DEPTH_DEEP,
    DEPTH_GENERAL,
    DEPTH_LIGHT,
    _PERSONAL_CLAIM_RE,
    _as_dict,
    _as_list,
    _clip,
    pack_allowed_refs,
)

DEFECT_PROVENANCE_REF_MISSING = "PROVENANCE_REF_MISSING"
DEFECT_PROVENANCE_REF_ORPHAN = "PROVENANCE_REF_ORPHAN"
DEFECT_PROVENANCE_WRONG_PROFILE = "PROVENANCE_WRONG_PROFILE"
DEFECT_PROVENANCE_ACTION_NOT_DERIVED = "PROVENANCE_ACTION_NOT_DERIVED"
DEFECT_PROVENANCE_PROP_NOT_DERIVED = "PROVENANCE_PROP_NOT_DERIVED"

DEFECT_CLOSURE_MISSING = "CLOSURE_MISSING"
DEFECT_CLOSURE_NO_CONFLICT_CALLBACK = "CLOSURE_NO_CONFLICT_CALLBACK"
DEFECT_CLOSURE_WELLNESS_MUSH = "CLOSURE_WELLNESS_MUSH"
DEFECT_CLOSURE_NEW_FORECAST = "CLOSURE_NEW_FORECAST"
DEFECT_CLOSURE_AFFIRMATION_ECHO = "CLOSURE_AFFIRMATION_ECHO"

_MUSH_RE = re.compile(
    r"("
    r"доверьтесь\s+вселенной|вы\s+достаточны|"
    r"everything\s+happens\s+for\s+a\s+reason|"
    r"trust\s+the\s+universe|you\s+are\s+enough|"
    r"the\s+universe\s+has\s+your\s+back"
    r")",
    re.I,
)

_NEW_FORECAST_RE = re.compile(
    r"("
    r"завтра\s+обязательно|next\s+week\s+you\s+will|"
    r"скоро\s+получите|you\s+will\s+meet\s+someone\s+new|"
    r"гарантированно\s+изменится"
    r")",
    re.I,
)

CLOSURE_FIELDS = ("resolution", "remaining_tension", "evening_state", "conflict_callback")


def _defect(code: str, *, field: str, message: str, severity: str = "critical") -> dict[str, str]:
    return {"code": code, "field": field, "message": message, "severity": severity}


def _scene_index(native: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for s in _as_list(native.get("scenes")):
        if isinstance(s, dict) and s.get("scene_id"):
            out[str(s["scene_id"])] = s
    return out


def _conflict_tokens(native: dict[str, Any]) -> set[str]:
    c = _as_dict(native.get("conflict"))
    blob = " ".join(str(c.get(k) or "") for k in ("title", "thesis", "force_a", "force_b"))
    return {t.lower() for t in re.findall(r"[\wа-яё]+", blob, flags=re.I) if len(t) > 3}


def run_provenance_gate_c351(
    native: dict[str, Any],
    pack: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    """recommendation → scene → conflict → evidence chain."""
    defects: list[dict[str, str]] = []
    pack = pack or {}
    allowed = pack_allowed_refs(pack) if pack else set()
    depth = str(pack.get("evidence_depth") or native.get("personalization_depth") or DEPTH_GENERAL)
    scenes = _scene_index(native)
    conflict = _as_dict(native.get("conflict"))
    conflict_ok = bool(_clip(conflict.get("title"), 80) and _clip(conflict.get("force_a"), 40))

    for i, s in enumerate(_as_list(native.get("scenes"))):
        if not isinstance(s, dict):
            continue
        field = f"scenes[{i}]"
        action = _clip(s.get("recommended_action"), 200)
        sid = str(s.get("scene_id") or s.get("origin_scene_id") or "").strip()
        if action and not sid:
            defects.append(
                _defect(
                    DEFECT_PROVENANCE_REF_MISSING,
                    field=field,
                    message="recommended_action without scene_id",
                )
            )
        if action and sid and sid not in scenes and sid != str(s.get("scene_id") or ""):
            defects.append(
                _defect(
                    DEFECT_PROVENANCE_ACTION_NOT_DERIVED,
                    field=field,
                    message=f"origin_scene_id {sid!r} not found",
                )
            )
        if action and not conflict_ok:
            defects.append(
                _defect(
                    DEFECT_PROVENANCE_ACTION_NOT_DERIVED,
                    field=field,
                    message="action present but conflict incomplete",
                )
            )

        evidence_refs = [str(x) for x in _as_list(s.get("evidence_refs")) if str(x).strip()]
        pers = _as_dict(s.get("personalization"))
        pers_refs = [str(x) for x in _as_list(pers.get("personalization_evidence_refs")) if str(x).strip()]
        level = str(pers.get("personalization_level") or native.get("personalization_depth") or "")

        if action and not evidence_refs and not pers_refs:
            defects.append(
                _defect(
                    DEFECT_PROVENANCE_REF_MISSING,
                    field=field,
                    message="action without evidence_refs / personalization_evidence_refs",
                )
            )

        for ref in evidence_refs + pers_refs:
            if allowed and ref.startswith("claim.personal") and ref not in allowed:
                defects.append(
                    _defect(
                        DEFECT_PROVENANCE_REF_ORPHAN,
                        field=field,
                        message=f"orphan personal ref {ref}",
                    )
                )

        if depth == DEPTH_GENERAL or level in {DEPTH_GENERAL, ""}:
            if pers_refs or _PERSONAL_CLAIM_RE.search(action or ""):
                defects.append(
                    _defect(
                        DEFECT_PROVENANCE_WRONG_PROFILE,
                        field=field,
                        message="general depth uses personal refs/claims",
                    )
                )
        if level in {DEPTH_DEEP, DEPTH_LIGHT} and action and not pers_refs and _PERSONAL_CLAIM_RE.search(action):
            defects.append(
                _defect(
                    DEFECT_PROVENANCE_WRONG_PROFILE,
                    field=field,
                    message="personal-sounding action without personal evidence refs",
                )
            )

    props = _as_dict(native.get("prop_material") or native.get("props"))
    for key in ("affirmation_tension", "affirmation", "color", "avoid_color"):
        node = _as_dict(props.get(key))
        if not node:
            continue
        osid = str(node.get("scene_id") or node.get("origin_scene_id") or "").strip()
        text = _clip(node.get("text") or node.get("name") or node.get("note"), 200)
        if text and not osid:
            defects.append(
                _defect(
                    DEFECT_PROVENANCE_PROP_NOT_DERIVED,
                    field=f"props.{key}",
                    message="prop text without scene_id",
                )
            )
        elif osid and osid not in scenes:
            defects.append(
                _defect(
                    DEFECT_PROVENANCE_PROP_NOT_DERIVED,
                    field=f"props.{key}",
                    message=f"prop scene_id {osid!r} missing",
                )
            )
    for cand in _as_list(props.get("color_scene_candidates")):
        if str(cand) not in scenes:
            defects.append(
                _defect(
                    DEFECT_PROVENANCE_PROP_NOT_DERIVED,
                    field="props.color_scene_candidates",
                    message=f"color candidate {cand!r} not a scene",
                )
            )
    return defects


def score_provenance_c351(
    native: dict[str, Any],
    pack: dict[str, Any] | None = None,
) -> dict[str, Any]:
    defects = run_provenance_gate_c351(native, pack)
    critical = [d for d in defects if d.get("severity") != "soft"]
    # Contract: scene_ids + conflict present; editorial: no orphans / wrong profile
    scenes = [s for s in _as_list(native.get("scenes")) if isinstance(s, dict)]
    contract_checks = {
        "scenes_have_ids": all(str(s.get("scene_id") or "").strip() for s in scenes) if scenes else False,
        "conflict_present": bool(_clip(_as_dict(native.get("conflict")).get("title"), 40)),
        "actions_present": any(str(s.get("recommended_action") or "").strip() for s in scenes),
    }
    contract_score = sum(1 for v in contract_checks.values() if v) / max(1, len(contract_checks))
    editorial_score = max(0.0, 1.0 - 0.18 * len(critical))
    combined = round(0.45 * contract_score + 0.55 * editorial_score, 3)
    return {
        "score": combined,
        "contract_score": round(contract_score, 3),
        "editorial_score": round(editorial_score, 3),
        "checks": contract_checks,
        "defect_codes": sorted({str(d.get("code")) for d in defects}),
        "defects": defects,
    }


def extract_day_closure(native: dict[str, Any]) -> dict[str, str]:
    """Accept nested day_closure or legacy prop affirmation as partial signal only."""
    raw = _as_dict(native.get("day_closure") or native.get("closure"))
    out = {k: _clip(raw.get(k), 240) for k in CLOSURE_FIELDS}
    return out


def run_closure_gate_c351(native: dict[str, Any]) -> list[dict[str, str]]:
    defects: list[dict[str, str]] = []
    closure = extract_day_closure(native)
    missing = [k for k, v in closure.items() if not v]
    if missing:
        defects.append(
            _defect(
                DEFECT_CLOSURE_MISSING,
                field="day_closure",
                message=f"missing closure fields: {', '.join(missing)}",
            )
        )
    # Scenes must NOT count as closure
    if not any(closure.values()) and _as_list(native.get("scenes")):
        defects.append(
            _defect(
                DEFECT_CLOSURE_MISSING,
                field="day_closure",
                message="scenes present but day_closure absent — scenes do not satisfy closure",
            )
        )

    blob = " ".join(closure.values())
    if blob and _MUSH_RE.search(blob):
        defects.append(_defect(DEFECT_CLOSURE_WELLNESS_MUSH, field="day_closure", message="wellness mush"))
    if blob and _NEW_FORECAST_RE.search(blob):
        defects.append(_defect(DEFECT_CLOSURE_NEW_FORECAST, field="day_closure", message="new forecast in closure"))

    callback = closure.get("conflict_callback") or ""
    ctokens = _conflict_tokens(native)
    if closure.get("resolution") and ctokens:
        cb_tokens = {t.lower() for t in re.findall(r"[\wа-яё]+", callback, flags=re.I) if len(t) > 3}
        if not (ctokens & cb_tokens) and not callback:
            defects.append(
                _defect(
                    DEFECT_CLOSURE_NO_CONFLICT_CALLBACK,
                    field="day_closure.conflict_callback",
                    message="closure does not call back to conflict",
                )
            )
        elif callback and not (ctokens & cb_tokens):
            defects.append(
                _defect(
                    DEFECT_CLOSURE_NO_CONFLICT_CALLBACK,
                    field="day_closure.conflict_callback",
                    message="conflict_callback unrelated to conflict tokens",
                )
            )

    props = _as_dict(native.get("prop_material") or native.get("props"))
    aff = _clip(_as_dict(props.get("affirmation_tension") or props.get("affirmation")).get("text"), 200)
    if aff and closure.get("resolution"):
        # near-echo of affirmation as "resolution"
        a_set = {t.lower() for t in re.findall(r"[\wа-яё]+", aff, flags=re.I) if len(t) > 3}
        r_set = {t.lower() for t in re.findall(r"[\wа-яё]+", closure["resolution"], flags=re.I) if len(t) > 3}
        if a_set and r_set and len(a_set & r_set) / max(1, len(a_set | r_set)) >= 0.75:
            defects.append(
                _defect(
                    DEFECT_CLOSURE_AFFIRMATION_ECHO,
                    field="day_closure.resolution",
                    message="resolution merely echoes affirmation",
                    severity="soft",
                )
            )
    return defects


def score_day_closure_c351(native: dict[str, Any]) -> dict[str, Any]:
    defects = run_closure_gate_c351(native)
    closure = extract_day_closure(native)
    contract_checks = {f"has_{k}": bool(closure.get(k)) for k in CLOSURE_FIELDS}
    # Explicitly: scenes do not help contract_score
    contract_checks["not_relying_on_scenes_alone"] = bool(any(closure.values()))
    contract_score = sum(1 for v in contract_checks.values() if v) / max(1, len(contract_checks))
    critical = [d for d in defects if d.get("severity") != "soft"]
    editorial_score = max(0.0, 1.0 - 0.2 * len(critical))
    if not any(closure.values()):
        editorial_score = min(editorial_score, 0.15)
        contract_score = min(contract_score, 0.2)
    combined = round(0.5 * contract_score + 0.5 * editorial_score, 3)
    return {
        "score": combined,
        "contract_score": round(contract_score, 3),
        "editorial_score": round(editorial_score, 3),
        "checks": contract_checks,
        "closure": closure,
        "defect_codes": sorted({str(d.get("code")) for d in defects}),
        "defects": defects,
    }
