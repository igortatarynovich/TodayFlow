"""Phase C3.3a — Personalization evidence contract, depth modes, and analysis.

Builds a bounded personalization_evidence pack (never raw Profile dump).
Modes: general | light_personalized | deep_personalized.

Analyzers emit defects + scores. **Runtime policy is owned by C3.6 gate maturity**
(`day_scenario_gate_maturity_c36`): only hard codes (PROFILE_FACT_LEAK,
EVIDENCE_ORPHAN) may retry/reject in user runtime. Soft personalization codes are
advisory (no downgrade / no unavailable).

Legacy helpers `personalization_requires_retry` / `personalization_decision_after_retries`
remain for tests/eval labeling — native LLM loop must not use them for product policy.

Canon: docs/audits/DAY_SCENARIO_PERSONALIZATION_C33A.md
       docs/audits/DAY_SCENARIO_GATE_MATURITY_C36.md
"""

from __future__ import annotations

import re
from typing import Any, Literal

PersonalizationDepth = Literal["general", "light_personalized", "deep_personalized"]

CONTRACT_VERSION = "day_scenario_personalization_c33a"
PACK_VERSION = "personalization_evidence_v1"

DEPTH_GENERAL: PersonalizationDepth = "general"
DEPTH_LIGHT: PersonalizationDepth = "light_personalized"
DEPTH_DEEP: PersonalizationDepth = "deep_personalized"

# Defect codes
DEFECT_CLAIM_WITHOUT_EVIDENCE = "PERSONALIZATION_CLAIM_WITHOUT_EVIDENCE"
DEFECT_DEPTH_OVERREACH = "PERSONALIZATION_DEPTH_OVERREACH"
DEFECT_DECORATIVE_ONLY = "PERSONALIZATION_DECORATIVE_ONLY"
DEFECT_SCENES_UNCHANGED = "PERSONALIZATION_SCENES_UNCHANGED"
DEFECT_GENERIC_ACTION = "PERSONALIZATION_GENERIC_ACTION"
DEFECT_SPHERE_UNJUSTIFIED = "PERSONALIZATION_SPHERE_UNJUSTIFIED"
DEFECT_CONFLICT_UNCHANGED = "PERSONALIZATION_CONFLICT_UNCHANGED"
DEFECT_NATAL_OVERCLAIM = "PERSONALIZATION_NATAL_OVERCLAIM"
DEFECT_EVIDENCE_ORPHAN = "PERSONALIZATION_EVIDENCE_ORPHAN"
DEFECT_PROFILE_FACT_LEAK = "PERSONALIZATION_PROFILE_FACT_LEAK"
DEFECT_SPHERE_OUTSIDE_PACK = "PERSONALIZATION_SPHERE_OUTSIDE_PACK"
DEFECT_SPHERE_SELECTION_EMPTY = "PERSONALIZATION_SPHERE_SELECTION_EMPTY"

# Legacy severity sets for eval/tests — runtime uses gate maturity C3.6.
CRITICAL_RETRY_DEFECTS = frozenset(
    {
        DEFECT_CLAIM_WITHOUT_EVIDENCE,
        DEFECT_DEPTH_OVERREACH,
        DEFECT_NATAL_OVERCLAIM,
        DEFECT_EVIDENCE_ORPHAN,
        DEFECT_PROFILE_FACT_LEAK,
        DEFECT_SPHERE_OUTSIDE_PACK,
    }
)

# After retry exhausted: downgrade personal layer (keep day story) unless leak/orphan persist
DOWNGRADE_DEFECTS = frozenset(
    {
        DEFECT_CLAIM_WITHOUT_EVIDENCE,
        DEFECT_DEPTH_OVERREACH,
        DEFECT_DECORATIVE_ONLY,
        DEFECT_SCENES_UNCHANGED,
        DEFECT_GENERIC_ACTION,
        DEFECT_SPHERE_UNJUSTIFIED,
        DEFECT_CONFLICT_UNCHANGED,
        DEFECT_NATAL_OVERCLAIM,
        DEFECT_EVIDENCE_ORPHAN,
        DEFECT_SPHERE_OUTSIDE_PACK,
        DEFECT_SPHERE_SELECTION_EMPTY,
    }
)

# Persist after retry → reject entire scenario (unavailable)
REJECT_STORY_DEFECTS = frozenset({DEFECT_PROFILE_FACT_LEAK})

TENDENCY_CATALOG: dict[str, tuple[str, re.Pattern[str]]] = {
    "smooth_conflict": (
        "tendency to smooth conflict",
        re.compile(r"сглаж|избег\w+\s+конфликт|ради\s+тишины|не\s+сказ|дипломат", re.I),
    ),
    "over_control": (
        "tendency to over-control",
        re.compile(r"контрол|управлять\s+за\s+друг|держать\s+всё|не\s+отпуска", re.I),
    ),
    "rejection_sensitivity": (
        "sensitivity to rejection",
        re.compile(r"отвержен|отказ|не\s+поняли|ран[иь]м\w+\s+от|чувствительн\w+\s+к\s+оценк", re.I),
    ),
    "direct_action": (
        "preference for direct action",
        re.compile(r"прям\w+\s+действ|резк\w+|требу\w+\s+ясност|без\s+обход", re.I),
    ),
    "need_processing_time": (
        "need for processing time",
        re.compile(r"время\s+на\s+обдум|сначала\s+понять|пауза|анализ|перевар", re.I),
    ),
    "responsibility_overload": (
        "responsibility overload",
        re.compile(r"ответственност|всё\s+на\s+себ|решить\s+за\s+друг|перегруз", re.I),
    ),
    "high_social_responsiveness": (
        "high social responsiveness",
        re.compile(r"социальн|отклик\w+\s+на\s+друг|чувств\w+\s+настроен|эмпат", re.I),
    ),
}

_PERSONAL_CLAIM_RE = re.compile(
    r"("
    r"вы\s+обычно|"
    r"вам\s+обычно|"
    r"вам\s+свойственн|"
    r"вы\s+свойственн|"
    r"обычно\s+свойственн|"
    r"ваша\s+привычка|"
    r"именно\s+вы\s+склонн|"
    r"вам\s+привычно|"
    r"вы\s+склонны|"
    r"ваш\s+паттерн|"
    r"в\s+вашем\s+натале"
    r")",
    re.I,
)

_PRECISE_NATAL_RE = re.compile(
    r"("
    r"\d+\s*дом|"
    r"асцендент|"
    r"MC\b|IC\b|"
    r"натальн\w+\s+марс|"
    r"в\s+вашей\s+карте|"
    r"прогресси|"
    r"соляр\s+возвращени|"
    r"управитель\s+\d+"
    r")",
    re.I,
)

_PROFILE_LEAK_RE = re.compile(
    r"("
    r"human\s*design|"
    r"тип\s+манифестор|тип\s+генератор|тип\s+проектор|тип\s+рефлектор|"
    r"ба-цзы|bazi|"
    r"координат|"
    r"широта|долгота|"
    r"\d{1,3}\.\d{3,},\s*-?\d{1,3}\.\d{3,}|"  # lat,lon
    r"время\s+рождения\s+\d{1,2}:\d{2}|"
    r"evidence_ref|"
    r"claim\.personal\."
    r")",
    re.I,
)

_GENERIC_ACTION_RE = re.compile(
    r"("
    r"не\s+торопитесь|"
    r"сделайте\s+паузу|"
    r"слушайте\s+себя|"
    r"сохраняйте\s+баланс|"
    r"избегайте\s+конфликтов|"
    r"take\s+a\s+pause|"
    r"trust\s+the\s+process"
    r")",
    re.I,
)


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _clip(value: Any, n: int = 240) -> str:
    from todayflow_backend.services.prose_clip_v1 import clip_prose

    text = re.sub(r"\s+", " ", str(value or "").strip())
    return clip_prose(text, n)


def _defect(code: str, *, field: str, message: str, severity: str = "critical") -> dict[str, str]:
    return {
        "code": code,
        "field": field,
        "message": message,
        "severity": severity,
        "capture_class": "PERSONALIZATION",
    }


def empty_personalization_pack(*, reason: str = "no_personal_evidence") -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "pack_version": PACK_VERSION,
        "evidence_depth": DEPTH_GENERAL,
        "available_sources": [],
        "behavioral_tendencies": [],
        "sensitive_domains": [],
        "supportive_resources": [],
        "natal_activations": [],
        "confidence": 0.0,
        "evidence_refs": [],
        "allowed_personal_claim_ids": [],
        "notes": reason,
    }


def _collect_personal_claims(interpretation: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for c in _as_list(interpretation.get("derived_claims")):
        if not isinstance(c, dict):
            continue
        cid = str(c.get("id") or "")
        if cid.startswith("claim.personal.") or str(c.get("layer") or "") == "personal":
            out.append(c)
    return out


def _infer_tendencies(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tendencies: list[dict[str, Any]] = []
    seen: set[str] = set()
    for c in claims:
        text = str(c.get("text") or "")
        refs = [str(x) for x in _as_list(c.get("evidence_ids")) if str(x).strip()]
        claim_id = str(c.get("id") or "")
        if claim_id:
            refs = list(dict.fromkeys([*refs, claim_id]))
        for tid, (label, pattern) in TENDENCY_CATALOG.items():
            if tid in seen:
                continue
            if pattern.search(text):
                seen.add(tid)
                tendencies.append(
                    {
                        "id": tid,
                        "label": label,
                        "confidence": 0.55 if refs else 0.35,
                        "source_refs": refs[:6],
                        "from_claim_id": claim_id or None,
                    }
                )
    return tendencies[:6]


def _infer_domains(claims: list[dict[str, Any]], personal: dict[str, Any]) -> list[str]:
    domains: list[str] = []
    blob = " ".join(str(c.get("text") or "") for c in claims)
    mapping = [
        ("relationships", r"отношени|партн|близк"),
        ("work_decisions", r"работ|коллег|решени|карьер"),
        ("communication", r"сообщен|разговор|письм|диалог"),
        ("money", r"деньг|счёт|финанс"),
        ("energy_body", r"энерг|тело|усталост"),
        ("home", r"дом|семь"),
    ]
    for sphere, pat in mapping:
        if re.search(pat, blob, re.I):
            domains.append(sphere)
    # From personal beats domains if present
    for key in ("personal_astrology", "human_design", "bazi"):
        block = _as_dict(personal.get(key))
        for beat in _as_list(block.get("beats")):
            if not isinstance(beat, dict):
                continue
            d = str(beat.get("domain") or beat.get("sphere") or "").strip()
            if d and d not in domains:
                domains.append(d)
    return domains[:6]


def build_personalization_evidence_pack_c33(
    interpretation: dict[str, Any] | None,
    *,
    birth_date_present: bool | None = None,
    birth_time_present: bool | None = None,
) -> dict[str, Any]:
    """Bounded pack for LLM + gate. Never includes raw Profile dump."""
    interp = _as_dict(interpretation)
    personal = _as_dict(interp.get("day_personal"))
    source_inputs = _as_dict(personal.get("source_inputs"))
    claims = _collect_personal_claims(interp)

    available_sources: list[str] = []
    for key, flag in (
        ("personal_astrology", "has_personal_astrology"),
        ("human_design", "has_human_design"),
        ("bazi", "has_bazi"),
        ("vedic_personal", "has_vedic_personal"),
        ("name_numbers", "has_name_numbers"),
    ):
        if source_inputs.get(flag) or _as_dict(personal.get(key)):
            available_sources.append(key)

    astro = _as_dict(personal.get("personal_astrology"))
    chart_meta = _as_dict(astro.get("chart_meta") or astro.get("meta") or astro)
    has_time = birth_time_present
    if has_time is None:
        has_time = bool(chart_meta.get("has_birth_time") or source_inputs.get("has_birth_time"))
    has_date = birth_date_present
    if has_date is None:
        has_date = bool(
            available_sources
            or claims
            or source_inputs.get("has_personal_astrology")
            or personal.get("summary_ru")
        )

    natal_activations: list[dict[str, Any]] = []
    evidence_refs: list[str] = []
    allowed_ids: list[str] = []
    for c in claims:
        cid = str(c.get("id") or "").strip()
        refs = [str(x) for x in _as_list(c.get("evidence_ids")) if str(x).strip()]
        if cid:
            allowed_ids.append(cid)
            evidence_refs.append(cid)
        evidence_refs.extend(refs)
        natal_activations.append(
            {
                "id": cid or f"activation.{len(natal_activations)}",
                "text": _clip(c.get("text"), 200),
                "evidence_refs": refs[:6],
                "confidence": 0.65 if refs else 0.4,
            }
        )

    # Cap activations
    natal_activations = natal_activations[:6]
    evidence_refs = list(dict.fromkeys(evidence_refs))[:24]
    allowed_ids = list(dict.fromkeys(allowed_ids))[:24]

    tendencies = _infer_tendencies(claims)
    for t in tendencies:
        evidence_refs = list(dict.fromkeys([*evidence_refs, *list(t.get("source_refs") or [])]))[:24]

    supportive: list[dict[str, Any]] = []
    for t in tendencies:
        if t["id"] in {"direct_action", "need_processing_time"}:
            supportive.append(
                {
                    "id": f"resource.{t['id']}",
                    "label": t["label"],
                    "evidence_refs": list(t.get("source_refs") or [])[:4],
                }
            )

    # Depth resolution
    deep_ok = bool(
        natal_activations
        and any(_as_list(a.get("evidence_refs")) for a in natal_activations)
        and (has_time or source_inputs.get("has_personal_astrology"))
        and len(tendencies) >= 1
    )
    light_ok = bool(has_date or claims or available_sources) and not deep_ok
    if deep_ok:
        depth: PersonalizationDepth = DEPTH_DEEP
        confidence = 0.72
    elif light_ok:
        depth = DEPTH_LIGHT
        confidence = 0.45
    else:
        depth = DEPTH_GENERAL
        confidence = 0.0

    if depth == DEPTH_GENERAL:
        return empty_personalization_pack(reason="insufficient_personal_evidence")

    return {
        "contract_version": CONTRACT_VERSION,
        "pack_version": PACK_VERSION,
        "evidence_depth": depth,
        "available_sources": available_sources,
        "behavioral_tendencies": tendencies,
        "sensitive_domains": _infer_domains(claims, personal),
        "supportive_resources": supportive[:4],
        "natal_activations": natal_activations if depth == DEPTH_DEEP else natal_activations[:2],
        "confidence": confidence,
        "evidence_refs": evidence_refs,
        "allowed_personal_claim_ids": allowed_ids,
        "chart_hints": {
            "has_birth_date": bool(has_date),
            "has_birth_time": bool(has_time),
            "precise_houses_allowed": depth == DEPTH_DEEP and bool(has_time),
        },
        "notes": "bounded pack — do not invent beyond listed refs",
    }


def pack_allowed_refs(pack: dict[str, Any] | None) -> set[str]:
    p = _as_dict(pack)
    refs = {str(x) for x in _as_list(p.get("evidence_refs")) if str(x).strip()}
    refs.update(str(x) for x in _as_list(p.get("allowed_personal_claim_ids")) if str(x).strip())
    for a in _as_list(p.get("natal_activations")):
        if isinstance(a, dict):
            refs.update(str(x) for x in _as_list(a.get("evidence_refs")) if str(x).strip())
            if a.get("id"):
                refs.add(str(a["id"]))
    for t in _as_list(p.get("behavioral_tendencies")):
        if isinstance(t, dict):
            refs.update(str(x) for x in _as_list(t.get("source_refs")) if str(x).strip())
    return refs


def empty_personalization_trace(*, level: str = DEPTH_GENERAL) -> dict[str, Any]:
    return {
        "personalization_level": level,
        "personalization_reason": "",
        "personalization_evidence_refs": [],
        "general_fallback_available": True,
    }


def _public_blobs(native: dict[str, Any]) -> str:
    conflict = _as_dict(native.get("conflict"))
    parts = [
        conflict.get("thesis"),
        conflict.get("force_a"),
        conflict.get("force_b"),
        conflict.get("why_today"),
        conflict.get("why_personal"),
    ]
    for sc in _as_list(native.get("scenes")):
        if not isinstance(sc, dict):
            continue
        parts.extend(
            [
                sc.get("setup"),
                sc.get("opportunity"),
                sc.get("trap"),
                sc.get("recommended_action"),
                sc.get("avoid_action"),
                sc.get("everyday_example"),
            ]
        )
    chorus = _as_dict(native.get("interpretive_chorus"))
    for row in _as_list(chorus.get("natal")):
        if isinstance(row, dict):
            parts.extend([row.get("named_factor"), row.get("human_meaning"), row.get("link_to_conflict")])
    return " ".join(str(p or "") for p in parts)


def _structural_fingerprint(native: dict[str, Any]) -> dict[str, Any]:
    conflict = _as_dict(native.get("conflict"))
    scenes = [s for s in _as_list(native.get("scenes")) if isinstance(s, dict)]
    return {
        "spheres": sorted(str(s.get("sphere") or "") for s in scenes),
        "forces": (
            _clip(conflict.get("force_a"), 80),
            _clip(conflict.get("force_b"), 80),
        ),
        "traps": [_clip(s.get("trap"), 80) for s in scenes],
        "actions": [_clip(s.get("recommended_action"), 80) for s in scenes],
    }


def count_structural_personalization_dimensions(native: dict[str, Any]) -> int:
    """Count how many structural axes carry non-general personalization traces."""
    dims = 0
    conflict = _as_dict(native.get("conflict"))
    c_trace = _as_dict(conflict.get("personalization") or native.get("conflict_personalization"))
    if (
        str(c_trace.get("personalization_level") or "") in {DEPTH_LIGHT, DEPTH_DEEP}
        and _as_list(c_trace.get("personalization_evidence_refs"))
    ):
        dims += 1
    if c_trace.get("habitual_force") in {"a", "b", "force_a", "force_b"}:
        dims += 1

    scene_personalized = 0
    action_personalized = 0
    for sc in _as_list(native.get("scenes")):
        if not isinstance(sc, dict):
            continue
        tr = _as_dict(sc.get("personalization"))
        level = str(tr.get("personalization_level") or "")
        refs = _as_list(tr.get("personalization_evidence_refs"))
        if level in {DEPTH_LIGHT, DEPTH_DEEP} and refs:
            scene_personalized += 1
            if tr.get("compensating_for") or tr.get("response_pattern"):
                action_personalized += 1
    if scene_personalized:
        dims += 1
    if action_personalized:
        dims += 1

    # Habitual trap difference signal via scene trap personalization reason
    if any(
        _as_dict(s.get("personalization")).get("trap_pattern")
        for s in _as_list(native.get("scenes"))
        if isinstance(s, dict)
    ):
        dims += 1
    return dims


def run_personalization_gate_c33(
    native: dict[str, Any] | None,
    pack: dict[str, Any] | None,
) -> list[dict[str, str]]:
    """Return personalization defects. Empty = pass for this depth."""
    if not isinstance(native, dict):
        return [_defect(DEFECT_CLAIM_WITHOUT_EVIDENCE, field="payload", message="native payload missing")]

    p = _as_dict(pack) or empty_personalization_pack()
    depth = str(p.get("evidence_depth") or DEPTH_GENERAL)
    declared = str(
        native.get("personalization_depth")
        or _as_dict(native.get("personalization")).get("depth")
        or depth
    )
    allowed = pack_allowed_refs(p)
    defects: list[dict[str, str]] = []
    public = _public_blobs(native)
    conflict = _as_dict(native.get("conflict"))
    scenes = [s for s in _as_list(native.get("scenes")) if isinstance(s, dict)]
    chorus = _as_dict(native.get("interpretive_chorus"))
    natal_rows = [r for r in _as_list(chorus.get("natal")) if isinstance(r, dict)]

    # Profile fact leak — always critical
    if _PROFILE_LEAK_RE.search(public):
        defects.append(
            _defect(
                DEFECT_PROFILE_FACT_LEAK,
                field="public_prose",
                message="public text leaks raw profile/system fields",
            )
        )

    # General: forbid personal claims
    if depth == DEPTH_GENERAL or declared == DEPTH_GENERAL:
        if _PERSONAL_CLAIM_RE.search(public):
            defects.append(
                _defect(
                    DEFECT_CLAIM_WITHOUT_EVIDENCE,
                    field="public_prose",
                    message="personal claims ('вы обычно' / 'вам свойственно') without personal evidence",
                )
            )
        if natal_rows:
            defects.append(
                _defect(
                    DEFECT_NATAL_OVERCLAIM,
                    field="chorus.natal",
                    message="natal chorus present at general depth",
                )
            )
        why_p = str(conflict.get("why_personal") or "").strip()
        if why_p and _PERSONAL_CLAIM_RE.search(why_p):
            defects.append(
                _defect(
                    DEFECT_CLAIM_WITHOUT_EVIDENCE,
                    field="conflict.why_personal",
                    message="why_personal personal claim at general depth",
                )
            )
        return _unique(defects)

    # Light: no precise natal overclaim
    if depth == DEPTH_LIGHT:
        if _PRECISE_NATAL_RE.search(public):
            defects.append(
                _defect(
                    DEFECT_DEPTH_OVERREACH,
                    field="public_prose",
                    message="precise natal language at light_personalized depth",
                )
            )
        if natal_rows and any(_PRECISE_NATAL_RE.search(_clip(_as_dict(r).get("human_meaning"), 200)) for r in natal_rows):
            defects.append(
                _defect(
                    DEFECT_NATAL_OVERCLAIM,
                    field="chorus.natal",
                    message="light depth must not claim precise natal activations",
                )
            )

    # Deep: structural personalization required
    if depth == DEPTH_DEEP and declared in {DEPTH_DEEP, "deep", ""}:
        dims = count_structural_personalization_dimensions(native)
        c_trace = _as_dict(conflict.get("personalization") or native.get("conflict_personalization"))
        if not c_trace.get("habitual_force") and not (
            str(c_trace.get("personalization_level") or "") == DEPTH_DEEP
            and _as_list(c_trace.get("personalization_evidence_refs"))
        ):
            defects.append(
                _defect(
                    DEFECT_CONFLICT_UNCHANGED,
                    field="conflict.personalization",
                    message="deep mode requires conflict habitual_force / personalization trace with refs",
                )
            )
        scene_with_trace = sum(
            1
            for s in scenes
            if str(_as_dict(s.get("personalization")).get("personalization_level") or "")
            in {DEPTH_LIGHT, DEPTH_DEEP}
            and _as_list(_as_dict(s.get("personalization")).get("personalization_evidence_refs"))
        )
        if scene_with_trace == 0:
            defects.append(
                _defect(
                    DEFECT_SCENES_UNCHANGED,
                    field="scenes",
                    message="deep mode requires scene-level personalization traces with evidence refs",
                )
            )
        if dims < 2:
            defects.append(
                _defect(
                    DEFECT_DECORATIVE_ONLY,
                    field="personalization",
                    message="deep mode changes only decorative wording — need ≥2 structural dimensions",
                )
            )

    # Evidence orphans on personalization refs
    def _check_refs(refs: list[Any], field: str) -> None:
        for r in refs:
            rid = str(r or "").strip()
            if not rid:
                continue
            if rid.startswith(("astrology", "day_card", "day_number", "conflict", "moon-", "merc-")):
                continue  # day facts, not personal pack
            if allowed and rid not in allowed and rid.startswith("claim.personal"):
                defects.append(
                    _defect(
                        DEFECT_EVIDENCE_ORPHAN,
                        field=field,
                        message=f"personal evidence ref not in pack: {rid}",
                    )
                )

    c_trace = _as_dict(conflict.get("personalization") or native.get("conflict_personalization"))
    _check_refs(_as_list(c_trace.get("personalization_evidence_refs")), "conflict.personalization")
    for i, sc in enumerate(scenes):
        tr = _as_dict(sc.get("personalization"))
        _check_refs(_as_list(tr.get("personalization_evidence_refs")), f"scenes[{i}].personalization")
        if (
            str(tr.get("personalization_level") or "") in {DEPTH_LIGHT, DEPTH_DEEP}
            and not str(tr.get("personalization_reason") or tr.get("sphere_reason") or "").strip()
        ):
            defects.append(
                _defect(
                    DEFECT_SPHERE_UNJUSTIFIED,
                    field=f"scenes[{i}]",
                    message="personalized scene missing reason / sphere justification",
                )
            )
        action = str(sc.get("recommended_action") or "")
        if (
            depth in {DEPTH_LIGHT, DEPTH_DEEP}
            and _as_list(p.get("behavioral_tendencies"))
            and _GENERIC_ACTION_RE.search(action)
            and not _as_dict(sc.get("personalization")).get("compensating_for")
        ):
            defects.append(
                _defect(
                    DEFECT_GENERIC_ACTION,
                    field=f"scenes[{i}].recommended_action",
                    message="generic pause/balance action is not personalization",
                )
            )

    for i, row in enumerate(natal_rows):
        _check_refs(_as_list(row.get("evidence_refs")), f"chorus.natal[{i}]")
        if depth == DEPTH_GENERAL:
            continue
        if depth == DEPTH_LIGHT and row:
            # natal voice at light is overclaim unless empty/generic
            meaning = str(row.get("human_meaning") or "")
            if _PERSONAL_CLAIM_RE.search(meaning) or _PRECISE_NATAL_RE.search(meaning):
                defects.append(
                    _defect(
                        DEFECT_NATAL_OVERCLAIM,
                        field=f"chorus.natal[{i}]",
                        message="natal voice overclaim at light depth",
                    )
                )

    # Declared depth overreach vs pack
    if declared == DEPTH_DEEP and depth != DEPTH_DEEP:
        defects.append(
            _defect(
                DEFECT_DEPTH_OVERREACH,
                field="personalization_depth",
                message=f"declared deep but pack evidence_depth={depth}",
            )
        )
    if declared == DEPTH_LIGHT and depth == DEPTH_GENERAL:
        defects.append(
            _defect(
                DEFECT_DEPTH_OVERREACH,
                field="personalization_depth",
                message="declared light but pack is general",
            )
        )

    return _unique(defects)


def _unique(defects: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for d in defects:
        key = f"{d['code']}:{d['field']}:{d['message'][:48]}"
        if key in seen:
            continue
        seen.add(key)
        out.append(d)
    return out


def personalization_has_critical(defects: list[dict[str, str]]) -> bool:
    return any(d.get("severity") == "critical" for d in defects)


def personalization_requires_retry(defects: list[dict[str, str]]) -> bool:
    return any(d.get("code") in CRITICAL_RETRY_DEFECTS for d in defects)


def personalization_decision_after_retries(defects: list[dict[str, str]]) -> str:
    """accept | downgrade_general | reject_story"""
    if not defects:
        return "accept"
    codes = {str(d.get("code")) for d in defects}
    if codes & REJECT_STORY_DEFECTS:
        return "reject_story"
    if codes & DOWNGRADE_DEFECTS or codes & CRITICAL_RETRY_DEFECTS:
        return "downgrade_general"
    return "accept"


def downgrade_native_to_general_c33(native: dict[str, Any] | None) -> dict[str, Any]:
    """Strip unconfirmed personal layer; keep day conflict/scenes as honest general.

    Not a formula rewrite of meaning — removes personal claims / natal / traces.
    """
    src = dict(native) if isinstance(native, dict) else {}
    conflict = dict(_as_dict(src.get("conflict")))
    why_p = str(conflict.get("why_personal") or "")
    if _PERSONAL_CLAIM_RE.search(why_p) or _PRECISE_NATAL_RE.search(why_p):
        conflict["why_personal"] = ""
    conflict["personalization"] = empty_personalization_trace(level=DEPTH_GENERAL)
    conflict.pop("habitual_force", None)

    scenes_out: list[dict[str, Any]] = []
    for sc in _as_list(src.get("scenes")):
        if not isinstance(sc, dict):
            continue
        row = dict(sc)
        row["personalization"] = empty_personalization_trace(level=DEPTH_GENERAL)
        action = str(row.get("recommended_action") or "")
        # leave action text; only clear personalization metadata
        if _PERSONAL_CLAIM_RE.search(action):
            # soften claim wording by blanking personal claim sentences — keep concrete remainder if any
            row["recommended_action"] = _GENERIC_ACTION_RE.sub("", action).strip() or action
        scenes_out.append(row)

    chorus = dict(_as_dict(src.get("interpretive_chorus")))
    chorus["natal"] = []

    src["conflict"] = conflict
    src["scenes"] = scenes_out
    src["interpretive_chorus"] = chorus
    src["personalization_depth"] = DEPTH_GENERAL
    src["personalization"] = {
        "depth": DEPTH_GENERAL,
        "downgraded_from": str(
            _as_dict(native).get("personalization_depth")
            or _as_dict(_as_dict(native).get("personalization")).get("depth")
            or ""
        )
        or None,
        "downgrade_reason": "personalization_gate",
    }
    return src


def format_personalization_retry_feedback(defects: list[dict[str, str]], *, pack: dict[str, Any] | None = None) -> str:
    depth = str(_as_dict(pack).get("evidence_depth") or DEPTH_GENERAL)
    lines = [
        "Предыдущий JSON отклонён personalization gate (C3.3a). Не подставляй Formula Bank.",
        f"Разрешённая глубина: {depth}.",
        "general — без «вы обычно» / натала; light — тон/why_personal/одна сфера, без точных домов;",
        "deep — меняй ≥2 структурных измерения (forces/spheres/trap/action) с personalization traces + evidence_refs.",
        "Дефекты:",
    ]
    for d in defects[:8]:
        lines.append(f"- [{d.get('code')}] {d.get('field')}: {d.get('message')}")
    return "\n".join(lines)


def score_personalization_c33(defects: list[dict[str, str]]) -> dict[str, Any]:
    score = 1.0
    for d in defects:
        score -= 0.12 if d.get("severity") == "critical" else 0.04
    return {
        "personalization_score": max(0.0, round(score, 3)),
        "defect_count": len(defects),
        "codes": sorted({str(d.get("code")) for d in defects}),
    }
