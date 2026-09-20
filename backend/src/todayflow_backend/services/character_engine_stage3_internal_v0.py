"""Character Engine Stage 3 — Internal Engine + tensions (expand Identity Core only).

Canon: docs/audits/CHARACTER_ENGINE_SCHEMA_CONTRACTS_V0.md §1.4 · Architecture Impact Stage 3.
LLM-first; code validates structure/provenance and forbids Identity Core rewrite.
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
    llm_call_context,
    resolve_complex_chat_model,
)
from todayflow_backend.knowledge.il2_composition_v1 import (
    ComposedFrame,
    compose_aspect_pair,
    compose_planet_in_sign,
    load_objects,
)
from todayflow_backend.prompts.registry_v1 import get_prompt

logger = logging.getLogger(__name__)

STAGE3_VERSION = "character_engine_stage3_internal_v0"
STAGE3_PROMPT_ID = "profile.character_engine.stage3.v1"
# PIC: docs/profile/PROFILE_INFORMATION_CONTRACT_V1.md
PIC_K = ("K04", "K05", "K06")  # K06 = N / Explore schema; path M is OMIT-BY-DESIGN
PIC_F = ("F03", "F04", "F07", "F08")
ENGINE_SLOTS = (
    "decision",
    "perception",
    "stress",
    "risk",
    "recovery",
    "growth",
    "burnout",
)
_OCCUPANCY_BODIES = ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn")
_HARMONIC_ASPECTS = {"conjunction": 0, "trine": 1, "sextile": 2}

# Deterministic expansion when LLM down — still rooted in identity thesis.
_ENGINE_BY_IDENTITY: dict[str, dict[str, dict[str, str]]] = {
    "builds_through_autonomy": {
        "decision": {
            "surface_text": (
                "Ты решаешь, когда внутренний контур ясен — чужой темп редко становится достаточным аргументом."
            ),
            "expansion_because": "Автономия как ядро требует собственного «да» до внешнего согласия.",
        },
        "perception": {
            "surface_text": (
                "Ты считываешь поле через дистанцию и структуру: сначала понять устройство, потом открыться."
            ),
            "expansion_because": "Ясность системы важнее чужой эмоциональной повестки.",
        },
        "stress": {
            "surface_text": (
                "Стресс растёт, когда тебя втягивают в чужой ритм без права на свой контур."
            ),
            "expansion_because": "Угроза автономии ощущается как потеря ясности.",
        },
        "risk": {
            "surface_text": (
                "Риск — держать дистанцию так долго, что выбор и близость откладываются."
            ),
            "expansion_because": "Механизм защиты ядра может заморозить движение жизни.",
        },
        "recovery": {
            "surface_text": (
                "Восстановление — вернуть себе тишину и право дойти до вывода самому."
            ),
            "expansion_because": "Автономия восстанавливается через собственный темп, не через суету.",
        },
        "growth": {
            "surface_text": (
                "Рост — входить в контакт, не сдавая систему: граница названа, шаг сделан."
            ),
            "expansion_because": "Ядро зреет, когда автономия служит связи, а не только защите.",
        },
        "burnout": {
            "surface_text": (
                "Выгорание — когда контроль ясности съедает живое движение и близость."
            ),
            "expansion_because": "Гипертрофия автономии истощает то, ради чего система строилась.",
        },
    },
}

_PRIMARY_TENSION_BY_IDENTITY: dict[str, dict[str, str]] = {
    "builds_through_autonomy": {
        "thesis_key": "autonomy_vs_contact",
        "surface_text": (
            "Пока ты держишь дистанцию как способ сохранить ясность, выбор и близость "
            "откладываются — контроль растёт, а жизнь перестаёт двигаться."
        ),
        "expansion_because": (
            "Это проявление builds_through_autonomy: защита контура становится отсрочкой жизни."
        ),
    },
    "builds_through_analysis": {
        "thesis_key": "analysis_vs_action",
        "surface_text": (
            "Пока ты продолжаешь анализировать вместо выбора, ощущение контроля растёт, "
            "а движение останавливается."
        ),
        "expansion_because": "Ядро анализа превращает полноту картины в отсрочку шага.",
    },
    "builds_through_air_mind": {
        "thesis_key": "ideas_vs_direction",
        "surface_text": (
            "Пока ты собираешь идеи и связи вместо направления, понимание растёт, "
            "а решение не наступает."
        ),
        "expansion_because": "Воздушный ум ветвится, пока одна линия не победит.",
    },
    "builds_through_earth_stability": {
        "thesis_key": "stability_vs_start",
        "surface_text": (
            "Пока ты ждёшь идеальной прочности основания, жизнь остаётся на паузе — "
            "устойчивость превращается в отсрочку."
        ),
        "expansion_because": "Опора как ядро рискует требовать идеальных условий до шага.",
    },
    "builds_through_water_care": {
        "thesis_key": "care_vs_boundary",
        "surface_text": (
            "Пока ты растворяешь границы ради чужой боли, собственные контуры стираются — "
            "забота становится потерей себя."
        ),
        "expansion_because": "Забота как ядро без границы съедает носителя.",
    },
    "builds_through_emotional_depth": {
        "thesis_key": "feeling_vs_step",
        "surface_text": (
            "Пока ты проживаешь всё слишком глубоко до любого шага, чувства заполняют поле, "
            "а действие откладывается."
        ),
        "expansion_because": "Глубина как ядро может блокировать внешний шаг.",
    },
    "builds_through_earth_anchor": {
        "thesis_key": "anchor_vs_new",
        "surface_text": (
            "Пока ты цепляешься за привычный порядок как за единственную опору, "
            "новое не входит — якорь становится клеткой."
        ),
        "expansion_because": "Якорь как ядро рискует запретить обновление.",
    },
    "builds_through_freedom_vs_stability": {
        "thesis_key": "freedom_vs_stability_hold",
        "surface_text": (
            "Пока свобода и опора тянут в разные стороны без выбора, ты тратишь силу "
            "на удержание напряжения вместо движения."
        ),
        "expansion_because": "Ось ядра без выбора этапа становится тупиком.",
    },
    "builds_through_fire_drive": {
        "thesis_key": "impulse_vs_direction",
        "surface_text": (
            "Пока импульс важнее направления, скорость растёт, а выбранный путь не собирается."
        ),
        "expansion_because": "Огонь ядра без вектора рассеивает силу.",
    },
    "builds_through_air_presence": {
        "thesis_key": "light_contact_vs_depth",
        "surface_text": (
            "Пока ты входишь в мир через лёгкий контакт и разговор, глубина связи "
            "остаётся недоступной."
        ),
        "expansion_because": "Лёгкое присутствие как ядро может избегать выбранной близости.",
    },
    "builds_through_fire_presence": {
        "thesis_key": "heat_vs_space",
        "surface_text": (
            "Пока первый контакт строится на напоре, вокруг появляется реакция, "
            "а не устойчивое пространство."
        ),
        "expansion_because": "Прямой вход как ядро может не оставлять места для ответа.",
    },
    "builds_through_earth_presence": {
        "thesis_key": "form_vs_alive",
        "surface_text": (
            "Пока ты показываешь только надёжную форму, живое движение остаётся спрятанным."
        ),
        "expansion_because": "Плотная форма как ядро может скрывать желание.",
    },
    "builds_through_water_presence": {
        "thesis_key": "softness_vs_desire",
        "surface_text": (
            "Пока ты встречаешь мир через чуткую оболочку, собственные желания "
            "остаются неназванными."
        ),
        "expansion_because": "Чуткий вход как ядро может не называть свой вектор.",
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _index_facts(raw_facts: list[Any]) -> dict[str, dict[str, Any]]:
    by_type: dict[str, dict[str, Any]] = {}
    for row in raw_facts:
        if not isinstance(row, dict):
            continue
        ft = str(row.get("fact_type") or "").strip()
        if ft and ft not in by_type:
            by_type[ft] = row
    return by_type


def _first_lemma(frame: ComposedFrame, job_name: str) -> str:
    payload = frame.jobs.get(job_name)
    if payload is None:
        return ""
    for lemma in payload.lemmas:
        token = str(lemma).strip()
        if token:
            return token
    return ""


def _how_line(frame: ComposedFrame) -> str:
    payload = frame.jobs.get("how")
    if payload is None:
        return ""
    bits = [str(lemma).strip() for lemma in payload.lemmas if str(lemma).strip()]
    return " ".join(bits)


def _manner_axis_for(
    *,
    catalog: dict[str, Any],
    bodies: dict[str, dict[str, str]],
    field: str,
    expected: str,
    supporting_id: str,
) -> dict[str, Any] | None:
    ordered = [body for body in _OCCUPANCY_BODIES if body in bodies]
    preferred = [body for body in ordered if body != "sun"] or ordered
    for body in preferred:
        meta = bodies.get(body) or {}
        if str(meta.get(field) or "") != expected:
            continue
        sign = str(meta.get("sign") or "").strip().lower()
        if not sign:
            continue
        frame = compose_planet_in_sign(
            catalog, f"astro.object.{body}", f"astro.sign.{sign}"
        )
        if frame.status != "composed":
            continue
        line = _how_line(frame)
        if not line:
            continue
        return {
            "slot": "decision",
            "surface_text": line,
            "source": "stage0_element_balance",
            "thesis_key": f"element_balance:{expected}",
            "body": body,
            "sign": sign,
            "supporting_fact_ids": [supporting_id] if supporting_id else [],
        }
    return None


def _harmonic_axis(
    *,
    catalog: dict[str, Any],
    facts_by_type: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    ranked: list[tuple[int, float, str, dict[str, Any], tuple[str, str, str]]] = []
    for fact_type, row in facts_by_type.items():
        if not str(fact_type).startswith("aspect_pair:"):
            continue
        value = row.get("value") if isinstance(row.get("value"), dict) else {}
        body_a = str(value.get("body_a") or "").strip().lower()
        body_b = str(value.get("body_b") or "").strip().lower()
        aspect = str(value.get("aspect") or "").strip().lower()
        if not body_a or not body_b or aspect not in _HARMONIC_ASPECTS:
            continue
        try:
            orb = float(value.get("orb"))
        except (TypeError, ValueError):
            orb = 99.0
        if body_a > body_b:
            body_a, body_b = body_b, body_a
        thesis = f"aspect_pair:{body_a}:{body_b}:{aspect}"
        ranked.append(
            (_HARMONIC_ASPECTS[aspect], orb, thesis, row, (body_a, body_b, aspect))
        )
    ranked.sort(key=lambda item: (item[0], item[1], item[2]))
    for _rank, _orb, thesis, row, (body_a, body_b, aspect) in ranked:
        frame = compose_aspect_pair(
            catalog,
            f"astro.object.{body_a}",
            f"astro.object.{body_b}",
            f"astro.aspect.{aspect}",
        )
        if frame.status != "composed":
            continue
        what_a = _first_lemma(frame, "what_a")
        what_b = _first_lemma(frame, "what_b")
        relation = _first_lemma(frame, "relation")
        if not what_a or not what_b or not relation:
            continue
        supporting = [str(row["fact_id"])] if row.get("fact_id") else []
        return {
            "slot": "decision",
            "surface_text": f"{what_a} / {what_b} — {relation}.",
            "source": "stage0_harmonic_aspect",
            "thesis_key": thesis,
            "supporting_fact_ids": supporting,
        }
    return None


def select_internal_engine_path_axis_v0(
    *,
    facts_pack: dict[str, Any] | None = None,
    raw_facts: list[Any] | None = None,
) -> dict[str, Any] | None:
    """PIC-K04: one Internal Engine axis from F08 / harmonic F07. Not seven widgets. Hard F07 is K05."""
    facts = raw_facts
    if facts is None and isinstance(facts_pack, dict):
        facts = facts_pack.get("raw_facts")
    if not isinstance(facts, list):
        return None
    facts_by_type = _index_facts(facts)
    balance = facts_by_type.get("element_balance")
    catalog = load_objects()
    if isinstance(balance, dict):
        value = balance.get("value") if isinstance(balance.get("value"), dict) else {}
        bodies = value.get("bodies") if isinstance(value.get("bodies"), dict) else {}
        supporting_id = str(balance.get("fact_id") or "")
        dominant_element = str(value.get("dominant_element") or "").strip() or None
        typed_bodies = {str(k): v for k, v in bodies.items() if isinstance(v, dict)}
        if dominant_element:
            axis = _manner_axis_for(
                catalog=catalog,
                bodies=typed_bodies,
                field="element",
                expected=dominant_element,
                supporting_id=supporting_id,
            )
            if axis:
                return axis
        dominant_modality = str(value.get("dominant_modality") or "").strip() or None
        if dominant_modality:
            axis = _manner_axis_for(
                catalog=catalog,
                bodies=typed_bodies,
                field="modality",
                expected=dominant_modality,
                supporting_id=supporting_id,
            )
            if axis:
                return axis
    return _harmonic_axis(catalog=catalog, facts_by_type=facts_by_type)


def _lemma_tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9-]+", str(text or "").lower()) if token}


def honest_cost_from_axis_v0(
    *,
    axis: dict[str, Any] | None,
    insight: str,
    help_line: str,
) -> dict[str, Any] | None:
    """PIC-K09: one honest cost of grounded K04+K05. Omit if missing, dupe, or no excess atom."""
    insight_line = str(insight or "").strip()
    help_text = str(help_line or "").strip()
    if not isinstance(axis, dict) or not insight_line or not help_text:
        return None
    if str(axis.get("source") or "") != "stage0_element_balance":
        return None
    sign = str(axis.get("sign") or "").strip().lower()
    if not sign:
        return None
    catalog = load_objects()
    obj = catalog.get(f"astro.sign.{sign}")
    canon = obj.get("canon") if isinstance(obj, dict) else None
    excess = canon.get("excess") if isinstance(canon, dict) else None
    if not isinstance(excess, list):
        return None
    bits = [str(lemma).strip() for lemma in excess if str(lemma).strip()]
    cost = " ".join(bits)
    if not cost:
        return None
    if _lemma_tokens(cost) & (_lemma_tokens(insight_line) | _lemma_tokens(help_text)):
        return None
    return {
        "surface_text": cost,
        "source": "sign_excess_of_k04_axis",
        "sign": sign,
        "body": str(axis.get("body") or ""),
    }


def _with_path_axis(out: dict[str, Any], facts_pack: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(out, dict):
        return out
    attached = dict(out)
    attached["path_axis"] = select_internal_engine_path_axis_v0(facts_pack=facts_pack)
    return attached


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


def _generic_engine(identity_thesis: str) -> dict[str, dict[str, str]]:
    pack = _ENGINE_BY_IDENTITY.get(identity_thesis)
    if pack:
        return pack
    # Person-facing defaults — never ship mechanism / English slot ids / thesis keys.
    surfaces = {
        "decision": "Ты решаешь яснее, когда опираешься на уже понятое ядро — без чужого темпа как единственного аргумента.",
        "perception": "Ты считываешь людей через то, что уже видно в тебе: тон, дистанция и смысл раньше чужой повестки.",
        "stress": "Стресс растёт, когда тебя тянут в чужой ритм без права на свой ясный контур.",
        "risk": "Риск — кружить в идеях и связях так долго, что выбор и шаг откладываются.",
        "recovery": "Восстановление — вернуть себе ясный ритм и право дойти до вывода самому.",
        "growth": "Рост — сделать один ясный шаг из того, что уже понятно, не собирая бесконечный круг вариантов.",
        "burnout": "Выгорание — когда бесконечный сбор смысла съедает живое движение и близость.",
    }
    return {
        slot: {
            "surface_text": surfaces[slot],
            "expansion_because": "Расширение того же ядра, не новая линия про себя.",
        }
        for slot in ENGINE_SLOTS
    }


def build_deterministic_stage3_raw_v0(
    *,
    identity_core: dict[str, Any],
    evidence: dict[str, Any],
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
    engine_src = _generic_engine(thesis)
    internal: dict[str, Any] = {}
    for slot in ENGINE_SLOTS:
        row = engine_src.get(slot) or {}
        internal[slot] = {
            "surface_text": row.get("surface_text") or f"Проявление ядра в зоне {slot}.",
            "expansion_because": row.get("expansion_because")
            or f"Это проявление {thesis}, потому что слот раскрывает тот же механизм.",
            "supporting_claim_ids": list(support),
        }
    tension = _PRIMARY_TENSION_BY_IDENTITY.get(thesis) or {
        "thesis_key": f"tension_of_{thesis}",
        "surface_text": (
            "Пока ядро характера не переводится в выбор, сила уходит в удержание формы вместо движения."
        ),
        "expansion_because": f"Это проявление {thesis}: механизм без шага становится ловушкой.",
    }
    return {
        "status": "grounded",
        "identity_thesis_echo": thesis,
        "internal_engine": internal,
        "primary_tension": {
            **tension,
            "supporting_claim_ids": list(support),
        },
        "secondary_tensions": [],
        "selection_rationale": "deterministic_fallback_llm_unavailable",
    }


def build_stage3_context_pack(
    *,
    facts_pack: dict[str, Any],
    evidence: dict[str, Any],
    identity: dict[str, Any],
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
    return {
        "prompt_id": STAGE3_PROMPT_ID,
        "identity_core": {
            "thesis_key": core.get("thesis_key"),
            "surface_text": core.get("surface_text"),
            "primary_claim_id": core.get("primary_claim_id"),
            "supporting_claim_ids": list(core.get("supporting_claim_ids") or []),
            "claim_id": core.get("claim_id"),
        },
        "claims": claims,
        "allowed_claim_ids": [c["claim_id"] for c in claims],
        "capability": facts_pack.get("capability") if isinstance(facts_pack.get("capability"), dict) else {},
        "forbidden": [
            "rewrite_identity_core",
            "second_independent_core",
            "career_love_money_roots",
            "profile_contract_v1",
        ],
    }


def validate_stage3_internal_contract(
    raw: dict[str, Any],
    *,
    identity: dict[str, Any],
    evidence: dict[str, Any],
    prompt_version: str,
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []

    def _fail(code: str, **extra: Any) -> dict[str, Any]:
        errors.append({"code": code, **extra})
        return {
            "artifact_version": STAGE3_VERSION,
            "status": "insufficient_internal_engine",
            "internal_engine": None,
            "primary_tension": None,
            "secondary_tensions": [],
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
    if status not in {"grounded", "insufficient_internal_engine"}:
        return _fail("invalid_status", got=status)

    echo = str(raw.get("identity_thesis_echo") or "").strip()
    if echo and echo != identity_thesis:
        return _fail("identity_thesis_rewrite_forbidden", got=echo, expected=identity_thesis)

    if status == "insufficient_internal_engine":
        return {
            "artifact_version": STAGE3_VERSION,
            "status": "insufficient_internal_engine",
            "internal_engine": None,
            "primary_tension": None,
            "secondary_tensions": [],
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

    engine_raw = raw.get("internal_engine")
    if not isinstance(engine_raw, dict):
        return _fail("internal_engine_required")

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

    internal: dict[str, Any] = {}
    for slot in ENGINE_SLOTS:
        row = engine_raw.get(slot)
        if not isinstance(row, dict):
            return _fail("engine_slot_missing", slot=slot)
        surface = str(row.get("surface_text") or "").strip()
        because = str(row.get("expansion_because") or "").strip()
        if not surface or not because:
            return _fail("engine_slot_incomplete", slot=slot)
        refs = _check_claim_list(row.get("supporting_claim_ids"))
        if refs is None:
            return _fail("engine_slot_unknown_claim", slot=slot)
        internal[slot] = {
            "slot": slot,
            "surface_text": surface,
            "expansion_because": because,
            "supporting_claim_ids": refs,
            "rooted_in_identity_thesis": identity_thesis,
        }

    pt_raw = raw.get("primary_tension")
    if not isinstance(pt_raw, dict):
        return _fail("primary_tension_required")
    pt_surface = str(pt_raw.get("surface_text") or "").strip()
    pt_because = str(pt_raw.get("expansion_because") or "").strip()
    pt_thesis = str(pt_raw.get("thesis_key") or "").strip() or f"tension_of_{identity_thesis}"
    if not pt_surface or not pt_because:
        return _fail("primary_tension_incomplete")
    pt_refs = _check_claim_list(pt_raw.get("supporting_claim_ids"))
    if pt_refs is None:
        return _fail("primary_tension_unknown_claim")
    primary_tension = {
        "thesis_key": pt_thesis,
        "surface_text": pt_surface,
        "expansion_because": pt_because,
        "supporting_claim_ids": pt_refs,
        "rooted_in_identity_thesis": identity_thesis,
    }

    secondary: list[dict[str, Any]] = []
    sec_raw = raw.get("secondary_tensions")
    if sec_raw is None:
        sec_raw = []
    if not isinstance(sec_raw, list):
        return _fail("secondary_tensions_invalid")
    for item in sec_raw[:3]:
        if not isinstance(item, dict):
            return _fail("secondary_tension_invalid")
        s_surface = str(item.get("surface_text") or "").strip()
        s_because = str(item.get("expansion_because") or "").strip()
        if not s_surface:
            continue
        s_refs = _check_claim_list(item.get("supporting_claim_ids"))
        if s_refs is None:
            return _fail("secondary_tension_unknown_claim")
        secondary.append(
            {
                "thesis_key": str(item.get("thesis_key") or "").strip() or "secondary",
                "surface_text": s_surface,
                "expansion_because": s_because
                or f"Это проявление {identity_thesis}, потому что вторичное напряжение того же ядра.",
                "supporting_claim_ids": s_refs,
                "rooted_in_identity_thesis": identity_thesis,
            }
        )

    return {
        "artifact_version": STAGE3_VERSION,
        "status": "grounded",
        "identity_thesis": identity_thesis,
        "identity_core_ref": {
            "claim_id": core.get("claim_id"),
            "thesis_key": identity_thesis,
            "primary_claim_id": core.get("primary_claim_id"),
        },
        "internal_engine": internal,
        "primary_tension": primary_tension,
        "secondary_tensions": secondary,
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
        },
        "generated_at": _now_iso(),
    }


def build_character_engine_internal_engine_v0(
    *,
    facts_pack: dict[str, Any],
    evidence: dict[str, Any],
    identity: dict[str, Any],
    locale: str = "ru",
    llm_raw: dict[str, Any] | None = None,
    deterministic_only: bool = False,
) -> dict[str, Any]:
    """Run Stage 3 Internal Engine. Pass llm_raw in tests."""
    context = build_stage3_context_pack(
        facts_pack=facts_pack, evidence=evidence, identity=identity
    )

    def _finish(out: dict[str, Any]) -> dict[str, Any]:
        return _with_path_axis(out, facts_pack)

    if llm_raw is not None:
        return _finish(
            validate_stage3_internal_contract(
                llm_raw,
                identity=identity,
                evidence=evidence,
                prompt_version="test_inject",
            )
        )

    if str(identity.get("status") or "") != "grounded":
        return _finish(
            validate_stage3_internal_contract(
            {
                "status": "insufficient_internal_engine",
                "identity_thesis_echo": "",
                "internal_engine": None,
                "primary_tension": None,
                "secondary_tensions": [],
                "selection_rationale": "identity_core_not_grounded",
            },
            identity=identity if identity.get("status") else {"status": "insufficient_identity_core"},
            evidence=evidence,
            prompt_version="n/a",
            )
        )

    core = identity.get("identity_core") if isinstance(identity.get("identity_core"), dict) else {}

    def _deterministic(*, reason: str, prompt_ver: str) -> dict[str, Any]:
        raw = build_deterministic_stage3_raw_v0(identity_core=core, evidence=evidence)
        if raw is None:
            return _finish(
                validate_stage3_internal_contract(
                    {
                        "status": "insufficient_internal_engine",
                        "selection_rationale": reason,
                    },
                    identity=identity,
                    evidence=evidence,
                    prompt_version=prompt_ver,
                )
            )
        logger.warning("character_engine_stage3: deterministic Internal Engine (%s)", reason)
        out = validate_stage3_internal_contract(
            raw, identity=identity, evidence=evidence, prompt_version=prompt_ver
        )
        if isinstance(out.get("validation"), dict):
            out["validation"] = {
                **out["validation"],
                "deterministic_fallback": True,
                "fallback_reason": reason,
            }
        return _finish(out)

    if deterministic_only or not is_llm_chat_configured():
        reason = "deterministic_only_read_path" if deterministic_only else "llm_not_configured"
        return _deterministic(reason=reason, prompt_ver="n/a")

    system, prompt_version = get_prompt(STAGE3_PROMPT_ID, locale=locale)
    from todayflow_backend.services.llm_practitioner_persona_v1 import with_practitioner_persona

    system = with_practitioner_persona(system, locale=locale)
    client = get_openai_compatible_client(operation="background", model=resolve_complex_chat_model())
    model = resolve_complex_chat_model()
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(context, ensure_ascii=False)},
    ]
    with llm_call_context(feature="ce.stage3", ensure_operation=True, operation="ce.stage3"):
        raw_text = chat_completion_text(
            client,
            model=model,
            messages=messages,
            temperature=0.35,
            max_tokens=1400,
            json_object=True,
        )
        if not raw_text:
            with llm_call_context(attempt=1, retry_reason="empty_content"):
                raw_text = chat_completion_text(
                    client,
                    model=model,
                    messages=messages,
                    temperature=0.2,
                    max_tokens=1400,
                    json_object=True,
                )
    parsed = _parse_json_object(raw_text or "")
    if not parsed:
        return _deterministic(reason="llm_json_invalid", prompt_ver=prompt_version)
    # Force echo if model omitted but core known — still validated against rewrite.
    if not parsed.get("identity_thesis_echo"):
        parsed["identity_thesis_echo"] = core.get("thesis_key")
    return _finish(
        validate_stage3_internal_contract(
            parsed,
            identity=identity,
            evidence=evidence,
            prompt_version=prompt_version,
        )
    )
