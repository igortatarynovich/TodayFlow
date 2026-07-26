"""Character Engine Stage 4 — scenes · potential · blind spots (expand only).

Canon: docs/audits/CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0.md §2.1 · §9 · Architecture Impact Stage 4.
LLM-first; code validates structure/provenance and forbids Identity Core rewrite /
career-love-money encyclopedia roots.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any

from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_text,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
)
from todayflow_backend.prompts.registry_v1 import get_prompt
from todayflow_backend.services.character_engine_ids_v0 import make_scene_id

logger = logging.getLogger(__name__)

STAGE4_VERSION = "character_engine_stage4_life_v0"
STAGE4_PROMPT_ID = "profile.character_engine.stage4.v1"

SCENE_KINDS = frozenset(
    {
        "responsibility",
        "intimacy",
        "risk",
        "success",
        "uncertainty",
        "competition",
        "recovery_context",
        "learning_pressure",
    }
)

# Deterministic life_bundle when LLM down — still rooted in identity thesis.
_LIFE_BY_IDENTITY: dict[str, dict[str, Any]] = {
    "builds_through_autonomy": {
        "scenes": [
            {
                "scene_kind": "intimacy",
                "surface_text": (
                    "В близости ты держишь свой контур: тепло возможно, когда тебя не "
                    "просят раствориться ради чужого темпа."
                ),
                "expansion_because": "Автономия как ядро задаёт форму интимности через дистанцию и ясность.",
                "rooted_in": "primary_tension",
            },
            {
                "scene_kind": "responsibility",
                "surface_text": (
                    "В зоне ответственности ты берёшь задачу, когда видишь свою систему — "
                    "чужой хаос без права на контур быстро выматывает."
                ),
                "expansion_because": "Ядро автономии проявляется как условие входа в долг/обязательство.",
                "rooted_in": "decision",
            },
            {
                "scene_kind": "risk",
                "surface_text": (
                    "Риск для тебя — отдать контроль ясности раньше, чем внутренний вывод готов."
                ),
                "expansion_because": "Угроза автономии ощущается как риск потери ясной линии.",
                "rooted_in": "risk",
            },
            {
                "scene_kind": "recovery_context",
                "surface_text": (
                    "Восстановление — вернуть тишину и право дойти до вывода самому, без чужой повестки."
                ),
                "expansion_because": "Recovery engine раскрывает то же ядро через возврат контура.",
                "rooted_in": "recovery",
            },
        ],
        "potential": {
            "surface_text": (
                "Потенциал — входить в контакт и обязательство, не сдавая систему: "
                "граница названа, шаг сделан."
            ),
            "expansion_because": "Growth slot Stage 3 + ядро автономии сходятся в зрелую связь.",
        },
        "blind_spots": [
            {
                "surface_text": (
                    "Легко не заметить, как защита ясности уже стала отсрочкой выбора и близости."
                ),
                "expansion_because": "Primary tension автономии vs контакта прячется в «ещё чуть ясности».",
            }
        ],
    },
}

# Person-facing labels for thesis keys (must never leak machine ids into surface_text).
_THESIS_SURFACE_LABEL: dict[str, str] = {
    "builds_through_autonomy": "автономию",
    "builds_through_analysis": "анализ",
    "builds_through_air_mind": "исследование идей",
    "builds_through_earth_stability": "опору",
    "builds_through_water_care": "заботу",
    "builds_through_emotional_depth": "глубину",
    "builds_through_earth_anchor": "якорь",
    "builds_through_freedom_vs_stability": "свободу и опору",
    "builds_through_fire_drive": "импульс",
    "builds_through_air_presence": "лёгкий контакт",
    "builds_through_fire_presence": "прямой вход",
    "builds_through_earth_presence": "плотную форму",
    "builds_through_water_presence": "чуткий вход",
}


def _thesis_surface_label(identity_thesis: str) -> str:
    key = str(identity_thesis or "").strip()
    if not key:
        return "своё ядро"
    return _THESIS_SURFACE_LABEL.get(key) or "своё ядро"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_json_object(raw: str) -> dict[str, Any] | None:
    text = (raw or "").strip()
    if not text:
        return None
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None


def _generic_life(identity_thesis: str) -> dict[str, Any]:
    pack = _LIFE_BY_IDENTITY.get(identity_thesis)
    if pack:
        return pack
    label = _thesis_surface_label(identity_thesis)
    return {
        "scenes": [
            {
                "scene_kind": "uncertainty",
                "surface_text": (
                    f"В неопределённости {label} проявляется как способ "
                    "держать поле, пока выбор ещё не назван."
                ),
                "expansion_because": f"Это расширение {identity_thesis}, а не новая identity-линия.",
                "rooted_in": "primary_tension",
            },
            {
                "scene_kind": "responsibility",
                "surface_text": (
                    f"В зоне ответственности тот же механизм — {label} — задаёт, "
                    "когда ты реально берёшь задачу на себя."
                ),
                "expansion_because": f"Ситуация раскрывает {identity_thesis} без career-корня.",
                "rooted_in": "decision",
            },
            {
                "scene_kind": "intimacy",
                "surface_text": (
                    f"В близости {label} задаёт, сколько пространства нужно, "
                    "чтобы оставаться собой рядом с другим."
                ),
                "expansion_because": f"Интимность как ситуация, не love-энциклопедия — проявление {identity_thesis}.",
                "rooted_in": "primary_tension",
            },
        ],
        "potential": {
            "surface_text": (
                f"Потенциал — переводить {label} в явный шаг, а не только в понимание."
            ),
            "expansion_because": f"Growth направления из того же ядра {identity_thesis}.",
        },
        "blind_spots": [
            {
                "surface_text": (
                    f"Легко не увидеть, где сила ({label}) уже стала отсрочкой жизни."
                ),
                "expansion_because": f"Слепое пятно — гипертрофия того же механизма {identity_thesis}.",
            }
        ],
    }


def build_deterministic_stage4_raw_v0(
    *,
    identity_core: dict[str, Any],
    evidence: dict[str, Any],
    stage3: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    thesis = str(identity_core.get("thesis_key") or "").strip()
    if not thesis:
        return None
    primary_claim = str(identity_core.get("primary_claim_id") or "").strip()
    claim_ids = [
        str(c.get("claim_id"))
        for c in (evidence.get("claims") or [])
        if isinstance(c, dict) and c.get("claim_id")
    ]
    support = [primary_claim] if primary_claim in claim_ids else claim_ids[:1]
    life = _generic_life(thesis)
    # Prefer Stage 3 tension surface inside intimacy if present.
    if isinstance(stage3, dict) and stage3.get("status") == "grounded":
        pt = stage3.get("primary_tension") if isinstance(stage3.get("primary_tension"), dict) else {}
        pt_text = str(pt.get("surface_text") or "").strip()
        if pt_text:
            scenes = list(life.get("scenes") or [])
            for i, sc in enumerate(scenes):
                if isinstance(sc, dict) and sc.get("scene_kind") == "intimacy":
                    scenes[i] = {
                        **sc,
                        "surface_text": (
                            "В близости это напряжение звучит так: " + pt_text
                        ),
                        "rooted_in": "primary_tension",
                    }
                    break
            life = {**life, "scenes": scenes}

    def _with_claims(row: dict[str, Any]) -> dict[str, Any]:
        return {**row, "supporting_claim_ids": list(support)}

    return {
        "status": "grounded",
        "identity_thesis_echo": thesis,
        "scenes": [_with_claims(dict(s)) for s in (life.get("scenes") or []) if isinstance(s, dict)],
        "potential": _with_claims(dict(life.get("potential") or {})),
        "blind_spots": [
            _with_claims(dict(b)) for b in (life.get("blind_spots") or []) if isinstance(b, dict)
        ],
        "selection_rationale": "deterministic_fallback_llm_unavailable",
    }


def build_stage4_context_pack(
    *,
    facts_pack: dict[str, Any],
    evidence: dict[str, Any],
    identity: dict[str, Any],
    stage3: dict[str, Any],
) -> dict[str, Any]:
    core = identity.get("identity_core") if isinstance(identity.get("identity_core"), dict) else {}
    claims = [
        {
            "claim_id": c.get("claim_id"),
            "thesis_key": c.get("thesis_key"),
            "supporting_fact_ids": list(c.get("supporting_fact_ids") or []),
            "evidence_status": c.get("evidence_status"),
        }
        for c in (evidence.get("claims") or [])
        if isinstance(c, dict) and c.get("claim_id")
    ]
    engine = stage3.get("internal_engine") if isinstance(stage3.get("internal_engine"), dict) else {}
    engine_brief = {
        slot: {
            "surface_text": (row or {}).get("surface_text") if isinstance(row, dict) else None,
        }
        for slot, row in engine.items()
    }
    pt = stage3.get("primary_tension") if isinstance(stage3.get("primary_tension"), dict) else {}
    return {
        "prompt_id": STAGE4_PROMPT_ID,
        "identity_core": {
            "thesis_key": core.get("thesis_key"),
            "surface_text": core.get("surface_text"),
            "primary_claim_id": core.get("primary_claim_id"),
            "supporting_claim_ids": list(core.get("supporting_claim_ids") or []),
            "claim_id": core.get("claim_id"),
        },
        "internal_engine": engine_brief,
        "primary_tension": {
            "thesis_key": pt.get("thesis_key"),
            "surface_text": pt.get("surface_text"),
            "supporting_claim_ids": list(pt.get("supporting_claim_ids") or []),
        },
        "claims": claims,
        "allowed_claim_ids": [c["claim_id"] for c in claims],
        "allowed_scene_kinds": sorted(SCENE_KINDS),
        "capability": facts_pack.get("capability") if isinstance(facts_pack.get("capability"), dict) else {},
        "forbidden": [
            "rewrite_identity_core",
            "second_independent_core",
            "career_love_money_roots",
            "profile_contract_v1",
            "encyclopedia_essays",
        ],
    }


def validate_stage4_life_contract(
    raw: dict[str, Any],
    *,
    identity: dict[str, Any],
    evidence: dict[str, Any],
    stage3: dict[str, Any],
    prompt_version: str,
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []

    def _fail(code: str, **extra: Any) -> dict[str, Any]:
        errors.append({"code": code, **extra})
        return {
            "artifact_version": STAGE4_VERSION,
            "status": "insufficient_life_bundle",
            "scenes": [],
            "potential": None,
            "blind_spots": [],
            "validation": {
                "ok": False,
                "no_core_rewrite": False,
                "refs_resolve": False,
                "required_fields_ok": False,
            },
            "diagnostics": {"contract_errors": errors, "prompt_version": prompt_version},
            "generated_at": _now_iso(),
        }

    if str(identity.get("status") or "") != "grounded":
        return _fail("identity_core_not_grounded")
    if str(stage3.get("status") or "") != "grounded":
        return _fail("stage3_not_grounded")
    core = identity.get("identity_core") if isinstance(identity.get("identity_core"), dict) else None
    if not core:
        return _fail("identity_core_missing")
    identity_thesis = str(core.get("thesis_key") or "").strip()
    if not identity_thesis:
        return _fail("identity_thesis_missing")

    claim_ids = {
        str(c.get("claim_id"))
        for c in (evidence.get("claims") or [])
        if isinstance(c, dict) and c.get("claim_id")
    }

    status = str(raw.get("status") or "").strip()
    if status not in {"grounded", "insufficient_life_bundle"}:
        return _fail("invalid_status", got=status)

    echo = str(raw.get("identity_thesis_echo") or "").strip()
    if echo and echo != identity_thesis:
        return _fail("identity_thesis_rewrite_forbidden", got=echo, expected=identity_thesis)

    if status == "insufficient_life_bundle":
        return {
            "artifact_version": STAGE4_VERSION,
            "status": "insufficient_life_bundle",
            "scenes": [],
            "potential": None,
            "blind_spots": [],
            "identity_thesis": identity_thesis,
            "validation": {
                "ok": True,
                "no_core_rewrite": True,
                "refs_resolve": True,
                "required_fields_ok": True,
            },
            "diagnostics": {
                "contract_errors": [],
                "prompt_version": prompt_version,
                "selection_rationale": raw.get("selection_rationale"),
            },
            "generated_at": _now_iso(),
        }

    def _check_claim_list(vals: Any) -> list[str] | None:
        if vals is None:
            return []
        if not isinstance(vals, list):
            return None
        out: list[str] = []
        for item in vals:
            cid = str(item or "").strip()
            if not cid:
                continue
            if cid not in claim_ids:
                return None
            out.append(cid)
        return sorted(set(out))

    scenes_raw = raw.get("scenes")
    if not isinstance(scenes_raw, list) or not scenes_raw:
        return _fail("scenes_required")

    tension_key = ""
    pt = stage3.get("primary_tension") if isinstance(stage3.get("primary_tension"), dict) else {}
    tension_key = str(pt.get("thesis_key") or identity_thesis).strip()

    scenes: list[dict[str, Any]] = []
    seen_kinds: set[str] = set()
    for item in scenes_raw[:8]:
        if not isinstance(item, dict):
            return _fail("scene_invalid")
        kind = str(item.get("scene_kind") or "").strip()
        if kind not in SCENE_KINDS:
            return _fail("scene_kind_invalid", got=kind)
        surface = str(item.get("surface_text") or "").strip()
        because = str(item.get("expansion_because") or "").strip()
        if not surface or not because:
            return _fail("scene_incomplete", scene_kind=kind)
        refs = _check_claim_list(item.get("supporting_claim_ids"))
        if refs is None:
            return _fail("scene_unknown_claim", scene_kind=kind)
        rooted = str(item.get("rooted_in") or "primary_tension").strip() or "primary_tension"
        scene_id = make_scene_id(
            scene_kind=kind,
            tension_or_mechanism_ref=f"{identity_thesis}:{tension_key}:{rooted}",
        )
        # Allow duplicate kinds only if distinct rooted_in — prefer unique kinds.
        key = f"{kind}:{rooted}"
        if key in seen_kinds:
            continue
        seen_kinds.add(key)
        scenes.append(
            {
                "scene_id": scene_id,
                "scene_kind": kind,
                "surface_text": surface,
                "expansion_because": because,
                "supporting_claim_ids": refs,
                "rooted_in": rooted,
                "rooted_in_identity_thesis": identity_thesis,
            }
        )
    if not scenes:
        return _fail("scenes_empty_after_normalize")

    pot_raw = raw.get("potential")
    if not isinstance(pot_raw, dict):
        return _fail("potential_required")
    pot_surface = str(pot_raw.get("surface_text") or "").strip()
    pot_because = str(pot_raw.get("expansion_because") or "").strip()
    if not pot_surface or not pot_because:
        return _fail("potential_incomplete")
    pot_refs = _check_claim_list(pot_raw.get("supporting_claim_ids"))
    if pot_refs is None:
        return _fail("potential_unknown_claim")
    potential = {
        "surface_text": pot_surface,
        "expansion_because": pot_because,
        "supporting_claim_ids": pot_refs,
        "rooted_in_identity_thesis": identity_thesis,
    }

    blind_spots: list[dict[str, Any]] = []
    bs_raw = raw.get("blind_spots")
    if bs_raw is None:
        bs_raw = []
    if not isinstance(bs_raw, list):
        return _fail("blind_spots_invalid")
    for item in bs_raw[:4]:
        if not isinstance(item, dict):
            return _fail("blind_spot_invalid")
        surface = str(item.get("surface_text") or "").strip()
        because = str(item.get("expansion_because") or "").strip()
        if not surface:
            continue
        refs = _check_claim_list(item.get("supporting_claim_ids"))
        if refs is None:
            return _fail("blind_spot_unknown_claim")
        blind_spots.append(
            {
                "surface_text": surface,
                "expansion_because": because
                or f"Это проявление {identity_thesis}, потому что слепое пятно того же механизма.",
                "supporting_claim_ids": refs,
                "rooted_in_identity_thesis": identity_thesis,
            }
        )

    return {
        "artifact_version": STAGE4_VERSION,
        "status": "grounded",
        "identity_thesis": identity_thesis,
        "identity_core_ref": {
            "claim_id": core.get("claim_id"),
            "thesis_key": identity_thesis,
            "primary_claim_id": core.get("primary_claim_id"),
        },
        "scenes": scenes,
        "potential": potential,
        "blind_spots": blind_spots,
        "validation": {
            "ok": True,
            "no_core_rewrite": True,
            "refs_resolve": True,
            "required_fields_ok": True,
            "expand_only": True,
        },
        "diagnostics": {
            "contract_errors": [],
            "prompt_version": prompt_version,
            "selection_rationale": raw.get("selection_rationale"),
            "scene_kinds": [s["scene_kind"] for s in scenes],
        },
        "generated_at": _now_iso(),
    }


def build_character_engine_life_bundle_v0(
    *,
    facts_pack: dict[str, Any],
    evidence: dict[str, Any],
    identity: dict[str, Any],
    stage3: dict[str, Any],
    locale: str = "ru",
    llm_raw: dict[str, Any] | None = None,
    deterministic_only: bool = False,
) -> dict[str, Any]:
    """Run Stage 4 life_bundle. Pass llm_raw in tests."""
    if llm_raw is not None:
        return validate_stage4_life_contract(
            llm_raw,
            identity=identity,
            evidence=evidence,
            stage3=stage3,
            prompt_version="test_inject",
        )

    if str(identity.get("status") or "") != "grounded" or str(stage3.get("status") or "") != "grounded":
        return validate_stage4_life_contract(
            {
                "status": "insufficient_life_bundle",
                "identity_thesis_echo": "",
                "scenes": [],
                "potential": None,
                "blind_spots": [],
                "selection_rationale": "prerequisites_not_grounded",
            },
            identity=identity if identity.get("status") else {"status": "insufficient_identity_core"},
            evidence=evidence,
            stage3=stage3 if stage3.get("status") else {"status": "insufficient_internal_engine"},
            prompt_version="n/a",
        )

    core = identity.get("identity_core") if isinstance(identity.get("identity_core"), dict) else {}
    context = build_stage4_context_pack(
        facts_pack=facts_pack, evidence=evidence, identity=identity, stage3=stage3
    )

    def _deterministic(*, reason: str, prompt_ver: str) -> dict[str, Any]:
        raw = build_deterministic_stage4_raw_v0(
            identity_core=core, evidence=evidence, stage3=stage3
        )
        if raw is None:
            return validate_stage4_life_contract(
                {"status": "insufficient_life_bundle", "selection_rationale": reason},
                identity=identity,
                evidence=evidence,
                stage3=stage3,
                prompt_version=prompt_ver,
            )
        logger.warning("character_engine_stage4: deterministic life_bundle (%s)", reason)
        out = validate_stage4_life_contract(
            raw, identity=identity, evidence=evidence, stage3=stage3, prompt_version=prompt_ver
        )
        if isinstance(out.get("validation"), dict):
            out["validation"] = {
                **out["validation"],
                "deterministic_fallback": True,
                "fallback_reason": reason,
            }
        return out

    if deterministic_only or not is_llm_chat_configured():
        reason = "deterministic_only_read_path" if deterministic_only else "llm_not_configured"
        return _deterministic(reason=reason, prompt_ver="n/a")

    system, prompt_version = get_prompt(STAGE4_PROMPT_ID, locale=locale)
    client = get_openai_compatible_client(operation="background")
    model = resolve_default_chat_model()
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(context, ensure_ascii=False)},
    ]
    raw_text = chat_completion_text(
        client,
        model=model,
        messages=messages,
        temperature=0.35,
        max_tokens=1600,
        json_object=True,
    )
    if not raw_text:
        raw_text = chat_completion_text(
            client,
            model=model,
            messages=messages,
            temperature=0.2,
            max_tokens=1600,
            json_object=True,
        )
    parsed = _parse_json_object(raw_text or "")
    if not parsed:
        return _deterministic(reason="llm_json_invalid", prompt_ver=prompt_version)
    if not parsed.get("identity_thesis_echo"):
        parsed["identity_thesis_echo"] = core.get("thesis_key")
    return validate_stage4_life_contract(
        parsed,
        identity=identity,
        evidence=evidence,
        stage3=stage3,
        prompt_version=prompt_version,
    )
