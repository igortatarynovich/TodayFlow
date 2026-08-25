"""Native C1 I0 generation split — Global stage then Personal overlay stage.

Meaning is fixed upstream; each LLM stage phrases only its permitted payload.
Personal never mutates Global semantic fields.

SoT: docs/today/NATIVE_C1_I0_GENERATION_SPLIT_V1.md · TODAY_CONTENT_PIPELINE_V1.md I0.
"""

from __future__ import annotations

import copy
import json
import re
from time import perf_counter
from typing import Any, Callable

from todayflow_backend.services.day_scenario_personalization_c33 import (
    DEPTH_DEEP,
    DEPTH_GENERAL,
    DEPTH_LIGHT,
)

PERSONAL_SCHEMA_VERSION = "native_c1_i0_personal_v1"
STAGE_GLOBAL = "global"
STAGE_PERSONAL = "personal"

GLOBAL_STAGE_INSTRUCTION_RU = (
    "I0_GLOBAL_STAGE (LOCKED): этот вызов = только Global layer. "
    "Формулируй внешний день: interpretive_chorus (astrology, day_card, day_number), "
    "conflict, scenes, prop_material. "
    "ЗАПРЕЩЕНО: natal[]; conflict.why_personal; личные personalization traces. "
    "personalization_depth = general. Личный слой — отдельный вызов после фиксации Global."
)

PERSONAL_STAGE_INSTRUCTION_RU = (
    "I0_PERSONAL_STAGE (LOCKED): во входе GLOBAL_LOCKED — зафиксированный Global сценарий. "
    "НЕ менять conflict.title/force_a/force_b/why_today/driver_refs; "
    "astrology/day_card/day_number voices; scene setup/opportunity/trap/recommended_action/avoid_action/"
    "everyday_example/why_sphere/sphere/primary_scene_id/prop_material. "
    "Только personal overlay: natal voices, why_personal, personalization на conflict и scenes. "
    "Не пересчитывай астрологический смысл. Не добавляй второй conflict."
)

# Global-owned fields — personal stage output must not redefine these.
_GLOBAL_CONFLICT_KEYS = frozenset(
    {
        "title",
        "thesis",
        "force_a",
        "force_b",
        "why_today",
        "driver_refs",
        "evidence_refs",
    }
)
_GLOBAL_CHORUS_VOICE_KEYS = frozenset(
    {"named_factor", "human_meaning", "link_to_conflict", "conflict_id", "archetype_role", "tempo", "style"}
)
_GLOBAL_SCENE_KEYS = frozenset(
    {
        "scene_id",
        "sphere",
        "role_in_story",
        "setup",
        "why_sphere",
        "opportunity",
        "trap",
        "recommended_action",
        "avoid_action",
        "everyday_example",
        "evidence_refs",
        "chorus_refs",
    }
)


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _clip(value: Any, n: int = 400) -> str:
    from todayflow_backend.services.prose_clip_v1 import clip_prose

    return clip_prose(value, n)


def generation_stages(pers_pack: dict[str, Any] | None) -> list[str]:
    """Deterministic stage order required by locked I0."""
    if should_run_personal_stage(pers_pack):
        return [STAGE_GLOBAL, STAGE_PERSONAL]
    return [STAGE_GLOBAL]


def should_run_personal_stage(pers_pack: dict[str, Any] | None) -> bool:
    depth = str(_as_dict(pers_pack).get("evidence_depth") or DEPTH_GENERAL)
    return depth in {DEPTH_LIGHT, DEPTH_DEEP}


def augment_global_system(system: str) -> str:
    base = system or ""
    if GLOBAL_STAGE_INSTRUCTION_RU in base:
        return base
    return f"{base.rstrip()}\n\n{GLOBAL_STAGE_INSTRUCTION_RU}\n"


def augment_personal_system(system: str) -> str:
    base = system or ""
    if PERSONAL_STAGE_INSTRUCTION_RU in base:
        return base
    return f"{base.rstrip()}\n\n{PERSONAL_STAGE_INSTRUCTION_RU}\n"


def global_locked_snapshot(global_norm: dict[str, Any]) -> dict[str, Any]:
    """Structured payload personal stage may read — not rewrite."""
    chorus = _as_dict(global_norm.get("interpretive_chorus"))
    scenes = []
    for sc in _as_list(global_norm.get("scenes")):
        if not isinstance(sc, dict):
            continue
        scenes.append({k: sc.get(k) for k in _GLOBAL_SCENE_KEYS if sc.get(k) is not None})
    return {
        "schema_version": "native_c1_i0_global_locked_v1",
        "personalization_depth": DEPTH_GENERAL,
        "interpretive_chorus": {
            "astrology": list(chorus.get("astrology") or []),
            "day_card": chorus.get("day_card"),
            "day_number": chorus.get("day_number"),
            "natal": [],
        },
        "conflict": {
            k: _as_dict(global_norm.get("conflict")).get(k)
            for k in _GLOBAL_CONFLICT_KEYS
        },
        "primary_scene_id": global_norm.get("primary_scene_id"),
        "scenes": scenes,
        "prop_material": global_norm.get("prop_material"),
        "visual_mode": global_norm.get("visual_mode"),
    }


def format_personal_user_message(
    global_locked: dict[str, Any],
    *,
    personalization_evidence: dict[str, Any],
    max_chars: int = 12000,
) -> str:
    payload = {
        "GLOBAL_LOCKED": global_locked,
        "personalization_evidence": personalization_evidence,
        "instruction": (
            "Верни ТОЛЬКО JSON schema_version=native_c1_i0_personal_v1 с полями: "
            "personalization_depth, personalization, interpretive_chorus.natal, "
            "conflict.why_personal, conflict.personalization, scenes[{scene_id,personalization}]."
        ),
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    return text[:max_chars]


def enforce_global_only(norm: dict[str, Any]) -> dict[str, Any]:
    """Strip personal fields — Global stage must not carry personal semantics."""
    from todayflow_backend.services.day_scenario_native_llm_c1 import _normalize_personalization_trace

    out = copy.deepcopy(norm)
    chorus = dict(_as_dict(out.get("interpretive_chorus")))
    chorus["natal"] = []
    out["interpretive_chorus"] = chorus
    conflict = dict(_as_dict(out.get("conflict")))
    conflict["why_personal"] = ""
    conflict["personalization"] = _normalize_personalization_trace(
        {"personalization_level": DEPTH_GENERAL}
    )
    out["conflict"] = conflict
    out["personalization_depth"] = DEPTH_GENERAL
    out["personalization"] = {
        "depth": DEPTH_GENERAL,
        **_as_dict(out.get("personalization")),
    }
    scenes_out: list[dict[str, Any]] = []
    for sc in _as_list(out.get("scenes")):
        if not isinstance(sc, dict):
            continue
        row = dict(sc)
        row["personalization"] = _normalize_personalization_trace(
            {"personalization_level": DEPTH_GENERAL}
        )
        scenes_out.append(row)
    out["scenes"] = scenes_out
    return out


def detect_global_mutation(
    global_norm: dict[str, Any],
    candidate: dict[str, Any],
) -> list[str]:
    """Return drift paths if candidate redefines Global-owned semantics."""
    errors: list[str] = []
    locked = global_locked_snapshot(global_norm)
    cand_chorus = _as_dict(candidate.get("interpretive_chorus"))
    lock_chorus = _as_dict(locked.get("interpretive_chorus"))

    for voice_name in ("astrology", "day_card", "day_number"):
        if voice_name == "astrology":
            cand_rows = _as_list(cand_chorus.get(voice_name))
            lock_rows = _as_list(lock_chorus.get(voice_name))
            if cand_rows and len(cand_rows) != len(lock_rows):
                errors.append(f"global_mutation:chorus.{voice_name}.count")
            for i, c_row in enumerate(cand_rows):
                if not isinstance(c_row, dict):
                    continue
                l_row = lock_rows[i] if i < len(lock_rows) and isinstance(lock_rows[i], dict) else {}
                for key in _GLOBAL_CHORUS_VOICE_KEYS:
                    cand_val = str(c_row.get(key) or "").strip()
                    if not cand_val:
                        continue
                    if cand_val != str(l_row.get(key) or "").strip():
                        errors.append(f"global_mutation:chorus.{voice_name}[{i}].{key}")
        else:
            c_voice = _as_dict(cand_chorus.get(voice_name))
            if not c_voice:
                continue
            l_voice = _as_dict(lock_chorus.get(voice_name))
            for key in _GLOBAL_CHORUS_VOICE_KEYS:
                cand_val = str(c_voice.get(key) or "").strip()
                if not cand_val:
                    continue
                if cand_val != str(l_voice.get(key) or "").strip():
                    errors.append(f"global_mutation:chorus.{voice_name}.{key}")

    cand_conflict = _as_dict(candidate.get("conflict"))
    lock_conflict = _as_dict(locked.get("conflict"))
    for key in _GLOBAL_CONFLICT_KEYS:
        cand_val = str(cand_conflict.get(key) or "").strip()
        if not cand_val:
            continue
        if cand_val != str(lock_conflict.get(key) or "").strip():
            errors.append(f"global_mutation:conflict.{key}")

    cand_pid = str(candidate.get("primary_scene_id") or "").strip()
    if cand_pid and cand_pid != str(locked.get("primary_scene_id") or "").strip():
        errors.append("global_mutation:primary_scene_id")

    cand_scenes = {
        str(s.get("scene_id")): s for s in _as_list(candidate.get("scenes")) if isinstance(s, dict)
    }
    lock_scenes = {str(s.get("scene_id")): s for s in _as_list(locked.get("scenes")) if isinstance(s, dict)}
    if cand_scenes:
        has_full_scene_body = any(
            any(str(_as_dict(c_sc).get(k) or "").strip() for k in ("setup", "opportunity", "trap"))
            for c_sc in cand_scenes.values()
        )
        if has_full_scene_body and set(cand_scenes.keys()) != set(lock_scenes.keys()):
            errors.append("global_mutation:scenes.set")
    for sid, l_sc in lock_scenes.items():
        c_sc = _as_dict(cand_scenes.get(sid))
        if not c_sc:
            continue
        for key in _GLOBAL_SCENE_KEYS:
            cand_val = str(c_sc.get(key) or "").strip()
            if not cand_val:
                continue
            if cand_val != str(l_sc.get(key) or "").strip():
                errors.append(f"global_mutation:scene[{sid}].{key}")

    return errors


def merge_personal_overlay(global_norm: dict[str, Any], personal_raw: dict[str, Any]) -> dict[str, Any]:
    """Apply personal overlay only — Global fields stay from global_norm."""
    from todayflow_backend.services.day_scenario_native_llm_c1 import _normalize_personalization_trace

    out = copy.deepcopy(global_norm)
    pers = _as_dict(personal_raw)
    depth = _clip(pers.get("personalization_depth") or _as_dict(pers.get("personalization")).get("depth"), 32)
    if depth not in {DEPTH_GENERAL, DEPTH_LIGHT, DEPTH_DEEP}:
        depth = str(_as_dict(global_norm.get("personalization")).get("depth") or DEPTH_GENERAL)

    out["personalization_depth"] = depth
    pers_meta = dict(_as_dict(pers.get("personalization")))
    out["personalization"] = {
        **_as_dict(out.get("personalization")),
        "depth": depth,
        "pack_confidence": pers_meta.get("pack_confidence"),
        "downgraded_from": pers_meta.get("downgraded_from"),
        "downgrade_reason": pers_meta.get("downgrade_reason"),
    }

    chorus = dict(_as_dict(out.get("interpretive_chorus")))
    pers_chorus = _as_dict(pers.get("interpretive_chorus"))
    natal_out: list[dict[str, Any]] = []
    for row in _as_list(pers_chorus.get("natal")):
        if not isinstance(row, dict):
            continue
        named = _clip(row.get("named_factor"), 220)
        if not named:
            continue
        natal_out.append(
            {
                "named_factor": named,
                "human_meaning": _clip(row.get("human_meaning"), 450),
                "link_to_conflict": _clip(row.get("link_to_conflict"), 420),
                "conflict_id": _clip(row.get("conflict_id"), 80),
                "evidence_refs": [
                    str(x).strip() for x in _as_list(row.get("evidence_refs")) if str(x).strip()
                ][:6],
            }
        )
    chorus["natal"] = natal_out[:3]
    out["interpretive_chorus"] = chorus

    conflict = dict(_as_dict(out.get("conflict")))
    pers_conflict = _as_dict(pers.get("conflict"))
    conflict["why_personal"] = _clip(pers_conflict.get("why_personal"), 280)
    if pers_conflict.get("personalization"):
        conflict["personalization"] = _normalize_personalization_trace(pers_conflict.get("personalization"))
    out["conflict"] = conflict

    pers_scenes = {
        str(s.get("scene_id")): s
        for s in _as_list(pers.get("scenes"))
        if isinstance(s, dict) and s.get("scene_id")
    }
    scenes_merged: list[dict[str, Any]] = []
    for sc in _as_list(out.get("scenes")):
        if not isinstance(sc, dict):
            continue
        row = dict(sc)
        sid = str(row.get("scene_id") or "")
        p_sc = _as_dict(pers_scenes.get(sid))
        if p_sc.get("personalization"):
            row["personalization"] = _normalize_personalization_trace(p_sc.get("personalization"))
        scenes_merged.append(row)
    out["scenes"] = scenes_merged
    return out


def normalize_personal_overlay(raw: dict[str, Any] | None) -> dict[str, Any]:
    from todayflow_backend.services.day_scenario_native_llm_c1 import _normalize_personalization_trace

    src = _as_dict(raw)
    depth = _clip(src.get("personalization_depth"), 32)
    if depth not in {DEPTH_GENERAL, DEPTH_LIGHT, DEPTH_DEEP}:
        depth = DEPTH_GENERAL
    pers_chorus = _as_dict(src.get("interpretive_chorus"))
    natal: list[dict[str, Any]] = []
    for row in _as_list(pers_chorus.get("natal")):
        if not isinstance(row, dict):
            continue
        named = _clip(row.get("named_factor"), 220)
        if named:
            natal.append(
                {
                    "named_factor": named,
                    "human_meaning": _clip(row.get("human_meaning"), 450),
                    "link_to_conflict": _clip(row.get("link_to_conflict"), 420),
                    "conflict_id": _clip(row.get("conflict_id"), 80),
                    "evidence_refs": [
                        str(x).strip() for x in _as_list(row.get("evidence_refs")) if str(x).strip()
                    ][:6],
                }
            )
    pers_conflict = _as_dict(src.get("conflict"))
    scenes: list[dict[str, Any]] = []
    for sc in _as_list(src.get("scenes")):
        if not isinstance(sc, dict):
            continue
        sid = _clip(sc.get("scene_id"), 64)
        if not sid:
            continue
        scenes.append(
            {
                "scene_id": sid,
                "personalization": _normalize_personalization_trace(sc.get("personalization")),
            }
        )
    return {
        "schema_version": PERSONAL_SCHEMA_VERSION,
        "personalization_depth": depth,
        "personalization": dict(_as_dict(src.get("personalization"))),
        "interpretive_chorus": {"natal": natal[:3]},
        "conflict": {
            "why_personal": _clip(pers_conflict.get("why_personal"), 280),
            "personalization": _normalize_personalization_trace(pers_conflict.get("personalization")),
        },
        "scenes": scenes,
    }


def validate_personal_overlay(payload: dict[str, Any] | None) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["personal_overlay_not_dict"]
    if str(payload.get("schema_version") or "") != PERSONAL_SCHEMA_VERSION:
        errors.append("personal_bad_schema_version")
    return errors


def _parse_json_content(content: str) -> dict[str, Any] | None:
    text = (content or "").strip()
    if not text:
        return None
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{[\s\S]*\}", text)
        if not m:
            return None
        try:
            data = json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
    return data if isinstance(data, dict) else None


def orchestrate_i0_split_generation(
    *,
    global_system: str,
    personal_system: str,
    user_base: str,
    pers_pack: dict[str, Any],
    il4_pack: Any,
    allowed_evidence_ids: set[str],
    max_attempts: int,
    llm_call: Callable[..., tuple[str | None, str | None, str | None]],
    resolve_attempt_model: Callable[[int], str],
    process_global_normalized: Callable[[dict[str, Any]], tuple[dict[str, Any] | None, str | None]],
    meta_out: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]], dict[str, Any]]:
    """
    Run I0 split stages. Returns (normalized_merged, attempt_rows, split_meta).
    split_meta: stages_run, personal_skipped, personal_degraded.
    """
    attempt_rows: list[dict[str, Any]] = []
    stages = generation_stages(pers_pack)
    split_meta: dict[str, Any] = {
        "i0_split": True,
        "stages_run": list(stages),
        "personal_skipped": STAGE_PERSONAL not in stages,
        "personal_degraded": False,
    }

    global_norm: dict[str, Any] | None = None
    retry_feedback = ""
    pending_retry_reason: str | None = None

    for attempt_idx in range(max_attempts):
        user_sent = user_base
        if retry_feedback:
            user_sent = f"{user_base}\n\n---\n{retry_feedback}"[:18000]
        attempt_t0 = perf_counter()
        attempt_model = resolve_attempt_model(attempt_idx)
        content, provider_kind, used_model = llm_call(
            attempt_idx=attempt_idx,
            attempt_model=attempt_model,
            system=global_system,
            user=user_sent,
            allow_model_fallback=attempt_idx == 0,
        )
        attempt_ms = int((perf_counter() - attempt_t0) * 1000)
        if not content:
            failure_class = "timeout" if provider_kind == "timeout" else "empty"
            attempt_rows.append(
                {
                    "attempt_index": attempt_idx,
                    "stage": STAGE_GLOBAL,
                    "attempt_duration_ms": attempt_ms,
                    "failure_class": failure_class,
                    "reject_reason": f"empty_llm_content:{provider_kind or 'unknown'}",
                    "provider_kind": provider_kind,
                }
            )
            if meta_out is not None:
                meta_out["i0_split"] = split_meta
            return None, attempt_rows, split_meta

        parsed = _parse_json_content(content)
        if not parsed:
            attempt_rows.append(
                {
                    "attempt_index": attempt_idx,
                    "stage": STAGE_GLOBAL,
                    "attempt_duration_ms": attempt_ms,
                    "failure_class": "parse",
                    "reject_reason": "json_parse_failed",
                    "raw_chars": len(content),
                }
            )
            retry_feedback = "Исправь JSON schema global stage."
            pending_retry_reason = "parse_failed"
            continue

        normalized, reject = process_global_normalized(parsed)
        if reject or normalized is None:
            attempt_rows.append(
                {
                    "attempt_index": attempt_idx,
                    "stage": STAGE_GLOBAL,
                    "attempt_duration_ms": attempt_ms,
                    "failure_class": "gate",
                    "reject_reason": reject or "global_stage_reject",
                }
            )
            retry_feedback = (reject or "").strip() or "I0 global stage: reject"
            pending_retry_reason = "gate_retry"
            continue

        global_norm = enforce_global_only(normalized)
        attempt_rows.append(
            {
                "attempt_index": attempt_idx,
                "stage": STAGE_GLOBAL,
                "attempt_duration_ms": attempt_ms,
                "status": "accepted_global",
                "model": used_model,
            }
        )
        break
    else:
        if meta_out is not None:
            meta_out["i0_split"] = split_meta
        return None, attempt_rows, split_meta

    if STAGE_PERSONAL not in stages:
        if meta_out is not None:
            meta_out["i0_split"] = split_meta
        return global_norm, attempt_rows, split_meta

    locked = global_locked_snapshot(global_norm)
    personal_user = format_personal_user_message(
        locked,
        personalization_evidence=pers_pack,
    )
    merged: dict[str, Any] | None = None
    personal_retry = ""

    for attempt_idx in range(max_attempts):
        user_sent = personal_user
        if personal_retry:
            user_sent = f"{personal_user}\n\n---\n{personal_retry}"[:18000]
        attempt_t0 = perf_counter()
        attempt_model = resolve_attempt_model(attempt_idx)
        content, provider_kind, used_model = llm_call(
            attempt_idx=attempt_idx,
            attempt_model=attempt_model,
            system=personal_system,
            user=user_sent,
            allow_model_fallback=attempt_idx == 0,
        )
        attempt_ms = int((perf_counter() - attempt_t0) * 1000)
        if not content:
            attempt_rows.append(
                {
                    "attempt_index": attempt_idx,
                    "stage": STAGE_PERSONAL,
                    "attempt_duration_ms": attempt_ms,
                    "failure_class": "timeout" if provider_kind == "timeout" else "empty",
                    "reject_reason": f"personal_empty:{provider_kind or 'unknown'}",
                }
            )
            break

        parsed = _parse_json_content(content)
        if not parsed:
            attempt_rows.append(
                {
                    "attempt_index": attempt_idx,
                    "stage": STAGE_PERSONAL,
                    "attempt_duration_ms": attempt_ms,
                    "failure_class": "parse",
                    "reject_reason": "personal_json_parse_failed",
                }
            )
            personal_retry = "Верни только personal overlay JSON."
            continue

        mutation = detect_global_mutation(global_norm, parsed)
        if mutation:
            attempt_rows.append(
                {
                    "attempt_index": attempt_idx,
                    "stage": STAGE_PERSONAL,
                    "attempt_duration_ms": attempt_ms,
                    "failure_class": "gate",
                    "reject_reason": ";".join(mutation[:6]),
                    "status": "personal_global_mutation",
                }
            )
            personal_retry = "Не меняй GLOBAL_LOCKED поля. Только personal overlay."
            continue

        overlay = normalize_personal_overlay(parsed)
        overlay_errors = validate_personal_overlay(overlay)
        if overlay_errors:
            attempt_rows.append(
                {
                    "attempt_index": attempt_idx,
                    "stage": STAGE_PERSONAL,
                    "attempt_duration_ms": attempt_ms,
                    "failure_class": "gate",
                    "reject_reason": ";".join(overlay_errors),
                }
            )
            personal_retry = "Исправь personal overlay schema."
            continue

        merged = merge_personal_overlay(global_norm, overlay)
        attempt_rows.append(
            {
                "attempt_index": attempt_idx,
                "stage": STAGE_PERSONAL,
                "attempt_duration_ms": attempt_ms,
                "status": "accepted_personal",
                "model": used_model,
            }
        )
        break

    if merged is None:
        split_meta["personal_degraded"] = True
        if meta_out is not None:
            meta_out["i0_split"] = split_meta
        return global_norm, attempt_rows, split_meta

    if meta_out is not None:
        meta_out["i0_split"] = split_meta
    return merged, attempt_rows, split_meta
