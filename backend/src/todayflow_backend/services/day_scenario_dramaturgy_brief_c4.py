"""Phase C4 — Day dramaturgy brief (pre-LLM SoT skeleton).

Canon: docs/DAY_SCENARIO_V1.md — Facts → chorus → conflict → scenes → props → UI.
day_thesis is Act III registry label / projection — not the plot to paraphrase.

This brief is built *before* the native scenario LLM call so the model
dramatizes ranked driver facts into everyday scenes, instead of expanding
a slogan registry label.
"""

from __future__ import annotations

from typing import Any

CONTRACT_VERSION = "day_dramaturgy_brief_c4"
BRIEF_INSTRUCTION_RU = (
    "Драматизируй must_dramatize в бытовые сцены. "
    "conflict.title — живое напряжение дня из фактов, не слоган из act_iii_registry_label. "
    "prop_material только из сцен."
)


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _clip(text: Any, n: int) -> str:
    from todayflow_backend.services.prose_clip_v1 import clip_prose

    s = " ".join(str(text or "").split()).strip()
    return clip_prose(s, n)


def _event_rows(pack: dict[str, Any]) -> list[dict[str, Any]]:
    """Resolve ranked driver ids → fact rows (same idea as scenario foundation)."""
    by_id: dict[str, dict[str, Any]] = {}
    for bucket in ("events", "primary", "supporting", "ambient"):
        for row in _as_list(pack.get(bucket)):
            if not isinstance(row, dict):
                continue
            eid = str(row.get("id") or "").strip()
            if eid and eid not in by_id:
                by_id[eid] = row
    ranked = _as_list(pack.get("ranked_drivers"))
    out: list[dict[str, Any]] = []
    if ranked:
        for did in ranked[:5]:
            key = str(did).strip()
            row = by_id.get(key)
            if row:
                out.append(row)
            else:
                out.append({"id": key, "fact_ru": key})
        return out
    # Fallback: first primary/events rows
    for row in list(by_id.values())[:5]:
        out.append(row)
    return out


def build_day_dramaturgy_brief_c4(
    *,
    interpretation: dict[str, Any] | None = None,
    ritual_context: dict[str, Any] | None = None,
    personalization_pack: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Deterministic pre-LLM skeleton: what to dramatize today."""
    interp = _as_dict(interpretation)
    ritual = _as_dict(ritual_context)
    pack = _as_dict(interp.get("day_events_pack"))
    thesis = _as_dict(interp.get("day_thesis"))
    pers = _as_dict(personalization_pack)
    selection = _as_dict(pers.get("sphere_selection"))

    rows = _event_rows(pack)
    must: list[dict[str, Any]] = []
    for row in rows[:3]:
        eid = str(row.get("id") or "").strip()
        fact = _clip(row.get("fact_ru") or row.get("title_ru") or eid, 220)
        if not eid and not fact:
            continue
        must.append(
            {
                "id": eid or f"driver.{len(must)}",
                "kind": str(row.get("kind") or "").strip() or None,
                "fact_ru": fact,
                "strength": row.get("strength"),
            }
        )

    supporting: list[dict[str, Any]] = []
    for row in rows[3:5]:
        eid = str(row.get("id") or "").strip()
        fact = _clip(row.get("fact_ru") or row.get("title_ru") or eid, 160)
        if eid or fact:
            supporting.append({"id": eid, "fact_ru": fact})

    ranked_spheres = [
        {
            "sphere": str(r.get("sphere") or "").strip(),
            "score": r.get("score"),
            "reasons": list(r.get("reasons") or [])[:3],
        }
        for r in _as_list(selection.get("ranked_spheres"))
        if isinstance(r, dict) and str(r.get("sphere") or "").strip()
    ][:4]

    primary_spheres = [
        str(s).strip()
        for s in _as_list(selection.get("primary_candidates") or selection.get("allowed_spheres"))
        if str(s).strip()
    ][:3]

    scene_slots: list[dict[str, Any]] = []
    for i, sphere in enumerate(primary_spheres[:3] or ["communication", "work_decisions"]):
        hook = must[i] if i < len(must) else (must[0] if must else None)
        scene_slots.append(
            {
                "role_in_story": "primary" if i == 0 else ("caution" if i == 2 else "support"),
                "sphere": sphere,
                "dramatize_from_driver_id": (hook or {}).get("id"),
                "hook_fact_ru": (hook or {}).get("fact_ru"),
            }
        )

    primary_conflict = None
    if must:
        main = must[0]
        main_theme = _clip(
            thesis.get("label_ru") or thesis.get("label") or main.get("fact_ru") or main.get("id") or "",
            120,
        )
        primary_conflict = {
            "contract_version": "primary_conflict_v1",
            "title": main_theme,
            "main_fact": _clip(main.get("fact_ru") or main.get("id") or "", 220),
            "main_driver_id": main.get("id"),
            "supporting_themes": [
                _clip(m.get("fact_ru") or "", 160)
                for m in must[1:3]
                if m.get("fact_ru")
            ],
            "allowed_spheres": [slot.get("sphere") for slot in scene_slots if slot.get("sphere")],
            "selected_before_llm": True,
        }

    card = _clip(ritual.get("tarot_name_ru") or ritual.get("tarot_name") or "", 80) or None
    number = ritual.get("numerology_value")
    if number is not None:
        try:
            number = int(number)
        except (TypeError, ValueError):
            number = None

    label = _clip(thesis.get("label_ru") or thesis.get("label") or "", 96)

    return {
        "contract_version": CONTRACT_VERSION,
        "instruction_ru": BRIEF_INSTRUCTION_RU,
        "must_dramatize": must,
        "supporting_facts": supporting,
        "scene_slots": scene_slots,
        "primary_conflict": primary_conflict,
        "sphere_candidates": {
            "primary": primary_spheres,
            "ranked": ranked_spheres,
            "allowed": [
                str(s).strip()
                for s in _as_list(selection.get("allowed_spheres"))
                if str(s).strip()
            ][:8],
        },
        "chorus_seeds": {
            "day_card": card,
            "day_number": number,
            "head_topic": _clip(ritual.get("head_topic") or "", 48) or None,
        },
        "act_iii_registry_label": {
            "label_ru": label or None,
            "family": thesis.get("family"),
            "variant": thesis.get("variant"),
            "mode": thesis.get("mode"),
            "role": "registry_seed_only_not_plot",
            "do_not": (
                "Не копируй и не слегка перефразируй label_ru как conflict.title. "
                "Ярлык — проекция Акта III после истории, не сюжет."
            ),
        },
        "personalization_depth": str(pers.get("evidence_depth") or "general"),
        "pipeline": "facts→brief→conflict→scenes→props→UI",
    }


def slim_interpretation_for_native_llm(
    interpretation: dict[str, Any] | None,
    *,
    brief: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Drop bulky nests already summarized in dramaturgy_brief."""
    interp = dict(_as_dict(interpretation))
    interp.pop("day_personal", None)
    # Keep a thin events pack: ranked ids + must_dramatize facts only
    must = _as_list(_as_dict(brief).get("must_dramatize"))
    supporting = _as_list(_as_dict(brief).get("supporting_facts"))
    thin_events = []
    for row in must + supporting:
        if isinstance(row, dict) and row.get("id"):
            thin_events.append(
                {
                    "id": row.get("id"),
                    "kind": row.get("kind"),
                    "fact_ru": row.get("fact_ru"),
                    "strength": row.get("strength"),
                }
            )
    if thin_events:
        interp["day_events_pack"] = {
            "contract_version": "day_events_pack_v1_slim_c4",
            "ranked_drivers": [e["id"] for e in thin_events if e.get("id")],
            "events": thin_events,
        }
    # Thesis demoted — full object lives only under brief.act_iii_registry_label
    if "day_thesis" in interp:
        thesis = _as_dict(interp.get("day_thesis"))
        interp["day_thesis"] = {
            "role": "see_dramaturgy_brief.act_iii_registry_label",
            "family": thesis.get("family"),
            "variant": thesis.get("variant"),
        }
    return interp


def format_native_user_message_c4(
    *,
    brief: dict[str, Any],
    context: dict[str, Any],
    max_chars: int = 16000,
    meaning_block: str | None = None,
) -> tuple[str, str]:
    """Build user message with brief protected from truncation.

    Returns (user_full, user_sent).
    """
    brief_s = json_dumps(brief)
    context_s = json_dumps(context)
    meaning = (str(meaning_block).rstrip() + "\n") if meaning_block else ""
    header = (
        f"{meaning}"
        "=== DRAMATURGY_BRIEF (SoT: что драматизировать сегодня) ===\n"
        f"{brief_s}\n"
        "=== CONTEXT ===\n"
    )
    full = header + context_s
    room = max(0, int(max_chars) - len(header))
    if len(context_s) <= room:
        return full, full
    sent = header + context_s[:room]
    return full, sent


def json_dumps(value: Any) -> str:
    import json

    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
