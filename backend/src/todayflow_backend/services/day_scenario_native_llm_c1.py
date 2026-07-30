"""Phase C1 — Native day_scenario LLM generation.

LLM returns one scenario JSON (chorus · conflict · scenes · prop_material).
Deterministic engine still builds props from scenes.
Legacy expect/trap/do schema is not runtime SoT (kept only for eval/compare).

Canon: docs/DAY_SCENARIO_V1.md · docs/audits/DAY_SCENARIO_NATIVE_LLM_C1.md
"""

from __future__ import annotations

import json
import re
from typing import Any

from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_plain,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
    resolve_max_tokens,
)
from todayflow_backend.services.day_scenario_v1 import (
    DAY_SCENARIO_V1_CONTRACT,
    DAY_SCENARIO_V1_VERSION,
    PRODUCT_SPHERE_IDS,
    build_scenario_foundation_v1,
    build_scenario_props_v1,
    validate_day_scenario_v1,
)

_SPHERE_LABEL_RU: dict[str, str] = {
    "work_decisions": "Работа и решения",
    "relationships": "Отношения",
    "communication": "Общение",
    "money": "Деньги",
    "energy_body": "Энергия и тело",
    "creativity": "Творчество",
    "home": "Дом",
    "rest_travel": "Отдых и поездки",
}

NATIVE_LLM_SCHEMA_VERSION = "day_scenario_native_llm_c1"
NATIVE_PROMPT_VERSION = "day-scenario-native-c4.0"
GENERATION_SOURCE_NATIVE = "native_llm_c1"
GENERATION_SOURCE_DETERMINISTIC = "deterministic_engine_b5"

LEGACY_FORBIDDEN_KEYS = frozenset(
    {
        "expect",
        "trap",
        "do",
        "avoid",
        "direction",
        "advantage",
        "abstain",
        "today_move",
        "primary_action",
        "vibe_closing",
        "vibe_strokes",
        "domains",
        "talisman",
        "practice_recommendation",
        "story",
        "theme",
        "headline_anchor",
        "events_lead",
        "color_note",
        "color",
        "affirmation",
        "affirmations",
        "goals",
        "primary_conflict",
        "day_thesis",
        "symbolic_note",
        "supports_story",
        "evening_closure",
        "development_point",
        "global_period",
    }
)

_PARALLEL_FORECAST_RE = re.compile(
    r"(отдельн\w+\s+прогноз|вторая\s+истори|независим\w+\s+(сюжет|прогноз)|"
    r"свой\s+прогноз|параллельн\w+\s+(сюжет|прогноз))",
    re.I,
)

_NATIVE_SYS_RU = """Ты — драматург TodayFlow. Твоя задача — построить ОДИН сценарий дня, а не заполнить карточки прогноза.

Порядок (жёстко): факты дня → DRAMATURGY_BRIEF → conflict → scenes → prop_material.
Во входе первым идёт DRAMATURGY_BRIEF (SoT «что драматизировать»). CONTEXT — уточнения.
Нельзя выдумывать астрономические или натальные факты вне evidence / must_dramatize.

ДРАМАТУРГИЧЕСКИЙ БРИФ (C4):
- must_dramatize = конкретные факты неба/циклов, из которых строится история;
- scene_slots = предпочтительные сферы и крючки; используй их как каркас сцен;
- act_iii_registry_label = ярлык реестра (Акт III), НЕ сюжет: conflict.title пиши как бытовое
  напряжение из must_dramatize (кто / где / что сталкивается), а не как слоган label_ru;
- prop_material только из готовых сцен (цвет, цель, аффирмация, юмор — производные истории).

Верни ТОЛЬКО JSON со schema_version = "day_scenario_native_llm_c1".

Структура:
{
  "schema_version": "day_scenario_native_llm_c1",
  "personalization_depth": "general|light_personalized|deep_personalized",
  "personalization": {
    "depth": "general|light_personalized|deep_personalized",
    "pack_confidence": 0.0
  },
  "interpretive_chorus": {
    "astrology": [{"named_factor": "...", "human_meaning": "...", "link_to_conflict": "...", "conflict_id": "conflict.<slug>", "evidence_refs": ["id"]}],
    "day_card": {"named_factor": "...", "archetype_role": "...", "link_to_conflict": "...", "conflict_id": "conflict.<slug>", "evidence_refs": []},
    "day_number": {"named_factor": "...", "tempo": "...", "style": "...", "link_to_conflict": "...", "conflict_id": "conflict.<slug>", "evidence_refs": []},
    "natal": [{"named_factor": "...", "human_meaning": "...", "link_to_conflict": "...", "conflict_id": "conflict.<slug>", "evidence_refs": ["id"]}]
  },
  "conflict": {
    "title": "...",
    "thesis": "...",
    "force_a": "...",
    "force_b": "...",
    "why_today": "...",
    "why_personal": "...",
    "driver_refs": ["id"],
    "evidence_refs": ["id"],
    "personalization": {
      "personalization_level": "general|light_personalized|deep_personalized",
      "personalization_reason": "...",
      "personalization_evidence_refs": ["id"],
      "general_fallback_available": true,
      "habitual_force": "a|b",
      "required_movement": "a|b"
    }
  },
  "scenes": [
    {
      "scene_id": "scene.relationships",
      "sphere": "relationships|work_decisions|communication|money|energy_body|creativity|home|rest_travel",
      "role_in_story": "primary|support|caution",
      "setup": "...",
      "opportunity": "...",
      "trap": "...",
      "recommended_action": "...",
      "avoid_action": "...",
      "everyday_example": "...",
      "evidence_refs": ["id"],
      "chorus_refs": ["astrology", "day_card", "day_number", "natal", "conflict"],
      "personalization": {
        "personalization_level": "general|light_personalized|deep_personalized",
        "personalization_reason": "почему эта сфера и эта реакция",
        "personalization_evidence_refs": ["id"],
        "general_fallback_available": true,
        "response_pattern": "привычный паттерн",
        "compensating_for": "какой baseline компенсирует действие",
        "trap_pattern": "тип ловушки",
        "sphere_reason": "почему сфера"
      }
    }
  ],
  "prop_material": {
    "color_scene_candidates": ["scene_id"],
    "avoid_color_trigger": "какая ловушка сцены усиливается чужим цветом",
    "goal_candidates": [{"scene_id": "...", "text": "..."}],
    "affirmation_tension": {"scene_id": "...", "trap": "...", "text": "..."},
    "humor_setup": {"scene_id": "...", "text": "..."}
  },
  "generation_notes": "только внутренние заметки; не для UI"
}

Правила (жёстко):
- одна история, один conflict;
- 2–4 scenes; каждая связана с conflict (setup/opportunity/trap про тот же сюжет);
- астрология объясняет внешнюю среду; карта — архетип; число — ритм; натал — личную реакцию;
- ни один голос хора не создаёт отдельный прогноз или вторую историю;
- формулировки вроде «Луна в Рыбах» желательны, если сразу переводятся в человеческое проявление и связаны с conflict;
- без справочного списка аспектов; без wellness/формул Formula Bank;

BYTOVAЯ КОНКРЕТИКА СЦЕН (C3.1) — обязательно:
Каждая сцена = узнаваемый момент, не абстрактная сфера.
В каждой сцене явно:
1) конкретный бытовой момент (кто / где / что сказано или сделано);
2) внутренний импульс;
3) внешняя ситуация;
4) выбор между двумя стратегиями (opportunity vs trap / force_a vs force_b);
5) наблюдаемое последствие;
6) действие, которое реально выполнить сегодня (recommended_action).
everyday_example обязателен и конкретен (сообщение, вопрос, письмо, пауза перед ответом, счёт, созвон…).

ЗАПРЕТ ПОВТОРОВ ОСИ КОНФЛИКТА В СЦЕНАХ:
Конфликт (force_a / force_b / title) уже назван в conflict — один раз.
В scenes НЕ копируй «тот же выбор — «force_a» или «force_b»» и шаблоны
«Шанс выбрать «force_b» именно здесь» / «Ловушка — скатиться в «force_a»…» в каждую сферу.
Перефразируй ось своими словами под быт сферы; opportunity/trap — разные по смыслу и лексике.
Если во входе есть person.first_name / display_name — обращайся по имени (ты + имя), не «вы».

Плохо: «В отношениях возможна напряжённость. Сохраняйте границы.»
Хорошо: «Человек может спросить, всё ли в порядке, именно когда хочется закрыться и ответить «нормально». Ловушка — согласиться ради тишины, а затем злиться, что вас не поняли.»

Запрещены универсальные конструкции без сцены:
«не торопитесь», «сохраняйте баланс», «слушайте себя», «избегайте конфликтов», «сделайте паузу» —
если они не встроены в конкретный момент и действие.

Хор — одна причинная линия (C3.2), не четыре мини-прогноза:
1) астрология = внешняя среда (небо → атмосфера дня для ЭТОГО conflict);
2) карта дня = архетип реакции (как проживать conflict);
3) число дня = темп / способ прохождения conflict;
4) натал = личная уязвимость или ресурс (только при evidence).
Каждый голос ОБЯЗАН иметь один и тот же conflict_id (slug от conflict.title, вида conflict.<slug>)
и link_to_conflict, явно связанный с conflict.
Запрещены: смысловые повторы между голосами; одинаковые абзацы с заменой терминов;
параллельные прогнозы («в работе… / в отношениях…» как отдельные истории).
Без натальных evidence не выдумывай глубокую персонализацию (natal=[]).

ПЕРСОНАЛИЗАЦИЯ (C3.3a/C3.3b) — контракт глубины:
Во входе есть personalization_evidence (ограниченный pack) и sphere_selection.ranked_spheres.
Не читай сырой Profile.
Соблюдай evidence_depth из pack:
- general: без «вы обычно / вам свойственно / ваша привычка»; natal=[]; why_personal пустой или без личных утверждений.
- light_personalized: можно why_personal, тон рекомендации, одну сферу, вероятную реакцию; без точных домов/асцендента/натальных активаций.
- deep_personalized: можно opposing forces, ranking сфер, trap, compensating action, intensity, natal voice;
  обязательно personalization traces с evidence_refs; habitual_force vs required_movement;
  минимум два структурных изменения, не только why_personal + natal абзац.
Сферы: предпочитай sphere_selection.allowed_spheres / primary_candidates.
Сфера вне списка — только с sphere_reason + personalization_evidence_refs.
Действие должно компенсировать baseline из pack.tendencies (не универсальный take a pause).
Не повторяй технические id, координаты, Human Design type labels в публичном тексте.

- ЗАПРЕЩЕНЫ legacy keys: expect, trap, do, avoid, domains, talisman, story, theme,
  color_note, affirmation, goals, day_thesis, primary_conflict, events_lead и т.п.
- не выбирай финальный цвет дня — только prop_material кандидаты;
- evidence_refs только из ids, данных во входе.
"""


NATIVE_SYS_RU = _NATIVE_SYS_RU


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _clip(value: Any, n: int = 400) -> str:
    text = str(value or "").strip()
    if len(text) <= n:
        return text
    return text[: n - 1].rstrip() + "…"


def _normalize_personalization_trace(raw: Any) -> dict[str, Any]:
    d = _as_dict(raw)
    level = _clip(d.get("personalization_level") or d.get("level") or "general", 32)
    if level not in {"general", "light_personalized", "deep_personalized"}:
        level = "general"
    return {
        "personalization_level": level,
        "personalization_reason": _clip(
            d.get("personalization_reason") or d.get("reason") or d.get("sphere_reason"), 240
        ),
        "personalization_evidence_refs": [
            str(x).strip() for x in _as_list(d.get("personalization_evidence_refs")) if str(x).strip()
        ][:6],
        "general_fallback_available": bool(d.get("general_fallback_available", True)),
        "habitual_force": _clip(d.get("habitual_force"), 16),
        "required_movement": _clip(d.get("required_movement"), 16),
        "response_pattern": _clip(d.get("response_pattern"), 120),
        "compensating_for": _clip(d.get("compensating_for"), 120),
        "trap_pattern": _clip(d.get("trap_pattern"), 80),
        "sphere_reason": _clip(d.get("sphere_reason"), 160),
    }


def _slug_scene_id(raw: Any, sphere: str, idx: int) -> str:
    text = str(raw or "").strip()
    if text.startswith("scene.") and len(text) < 64:
        return re.sub(r"[^a-zA-Z0-9_.\-]", "", text) or f"scene.{sphere}"
    if sphere in PRODUCT_SPHERE_IDS:
        return f"scene.{sphere}"
    return f"scene.{idx}"


def collect_allowed_evidence_ids(
    *,
    interpretation: dict[str, Any] | None,
    ritual_context: dict[str, Any] | None = None,
    celestial_events: dict[str, Any] | None = None,
) -> set[str]:
    """Known evidence / driver / ritual ids — LLM may only cite these."""
    allowed: set[str] = set()
    interp = _as_dict(interpretation)
    for key in ("evidence", "derived_claims"):
        for row in _as_list(interp.get(key)):
            if isinstance(row, dict) and row.get("id"):
                allowed.add(str(row["id"]))
            if isinstance(row, dict):
                for e in _as_list(row.get("evidence_ids")):
                    allowed.add(str(e))
    pack = interp.get("day_events_pack") if isinstance(interp.get("day_events_pack"), dict) else None
    if pack is None and isinstance(celestial_events, dict):
        pack = celestial_events.get("day_events_pack")
    if isinstance(pack, dict):
        for bucket in ("ranked_drivers", "primary", "supporting", "ambient", "events"):
            for row in _as_list(pack.get(bucket)):
                if isinstance(row, dict) and row.get("id"):
                    allowed.add(str(row["id"]))
    thesis = _as_dict(interp.get("day_thesis"))
    for d in _as_list(thesis.get("driver_ids")):
        allowed.add(str(d))
    ritual = _as_dict(ritual_context)
    if ritual.get("tarot_main_id") is not None:
        allowed.add(f"tarot:{ritual.get('tarot_main_id')}")
        allowed.add("day_card")
    if ritual.get("tarot_name_ru"):
        allowed.add("day_card")
    if ritual.get("numerology_value") is not None:
        allowed.add("day_number")
        allowed.add(f"number:{ritual.get('numerology_value')}")
    # Soft allow common chorus tokens
    allowed.update({"astrology", "natal", "conflict", "day_card", "day_number"})
    return {a for a in allowed if a}


def has_native_generation_marker(story: dict[str, Any] | None) -> bool:
    """True if story carries C1-valid meaning cache (native LLM or post-C1 deterministic)."""
    if not isinstance(story, dict):
        return False
    scen = _as_dict(story.get("day_scenario"))
    src = str(scen.get("generation_source") or "").strip()
    if src in {GENERATION_SOURCE_NATIVE, GENERATION_SOURCE_DETERMINISTIC}:
        return True
    editorial = _as_dict(story.get("editorial"))
    return str(editorial.get("native_scenario_generation") or "") == NATIVE_LLM_SCHEMA_VERSION


def find_legacy_keys(payload: dict[str, Any]) -> list[str]:
    return sorted(k for k in payload.keys() if k in LEGACY_FORBIDDEN_KEYS)


def normalize_native_scenario_llm_c1(raw: dict[str, Any] | None) -> dict[str, Any]:
    """Shape-only normalize — never invent meaning."""
    src = _as_dict(raw)
    chorus_in = _as_dict(src.get("interpretive_chorus"))
    conflict_in = _as_dict(src.get("conflict"))
    scenes_in = _as_list(src.get("scenes"))
    props_in = _as_dict(src.get("prop_material"))

    def _voice_row(row: Any, *, default_conflict_id: str = "") -> dict[str, Any] | None:
        d = _as_dict(row)
        if not d:
            return None
        named = _clip(d.get("named_factor") or d.get("named"), 220)
        if not named:
            return None
        cid = _clip(d.get("conflict_id"), 80) or default_conflict_id
        return {
            "named_factor": named,
            "human_meaning": _clip(d.get("human_meaning") or d.get("meaning"), 280),
            "link_to_conflict": _clip(d.get("link_to_conflict") or d.get("for_conflict"), 240),
            "conflict_id": cid,
            "archetype_role": _clip(d.get("archetype_role") or d.get("role"), 200),
            "tempo": _clip(d.get("tempo"), 80),
            "style": _clip(d.get("style"), 80),
            "evidence_refs": [
                str(x).strip()
                for x in (
                    _as_list(d.get("evidence_refs"))
                    if d.get("evidence_refs") is not None
                    else ([d.get("evidence_ref")] if d.get("evidence_ref") else [])
                )
                if str(x).strip()
            ][:6],
        }

    from todayflow_backend.services.day_scenario_editorial_gate_c31 import conflict_anchor_id

    conflict_title_for_id = {
        "title": _clip(conflict_in.get("title") or conflict_in.get("short_name"), 120),
    }
    default_cid = conflict_anchor_id(conflict_title_for_id)

    astrology = []
    for row in _as_list(chorus_in.get("astrology")):
        v = _voice_row(row, default_conflict_id=default_cid)
        if v:
            astrology.append(v)
    natal = []
    for row in _as_list(chorus_in.get("natal")):
        v = _voice_row(row, default_conflict_id=default_cid)
        if v:
            natal.append(v)
    day_card = _voice_row(chorus_in.get("day_card"), default_conflict_id=default_cid)
    day_number = _voice_row(chorus_in.get("day_number"), default_conflict_id=default_cid)

    scenes_out: list[dict[str, Any]] = []
    seen_spheres: set[str] = set()
    for idx, sc in enumerate(scenes_in):
        if not isinstance(sc, dict):
            continue
        sphere = str(sc.get("sphere") or "").strip()
        if sphere not in PRODUCT_SPHERE_IDS:
            continue
        if sphere in seen_spheres:
            continue
        seen_spheres.add(sphere)
        scene_id = _slug_scene_id(sc.get("scene_id"), sphere, idx)
        scenes_out.append(
            {
                "scene_id": scene_id,
                "sphere": sphere,
                "role_in_story": _clip(sc.get("role_in_story") or ("primary" if idx == 0 else "support"), 32),
                "setup": _clip(sc.get("setup") or sc.get("what_happens"), 320),
                "opportunity": _clip(sc.get("opportunity"), 280),
                "trap": _clip(sc.get("trap"), 280),
                "recommended_action": _clip(sc.get("recommended_action") or sc.get("do"), 240),
                "avoid_action": _clip(sc.get("avoid_action") or sc.get("do_not") or sc.get("avoid"), 240),
                "everyday_example": _clip(sc.get("everyday_example") or sc.get("domestic_example"), 280),
                "evidence_refs": [str(x).strip() for x in _as_list(sc.get("evidence_refs")) if str(x).strip()][:6],
                "chorus_refs": [str(x).strip() for x in _as_list(sc.get("chorus_refs")) if str(x).strip()][:8],
                "personalization": _normalize_personalization_trace(sc.get("personalization")),
            }
        )

    goals = []
    for g in _as_list(props_in.get("goal_candidates")):
        if isinstance(g, dict) and g.get("text"):
            goals.append(
                {
                    "scene_id": _clip(g.get("scene_id"), 64),
                    "text": _clip(g.get("text"), 200),
                }
            )

    affirm = _as_dict(props_in.get("affirmation_tension"))
    humor = _as_dict(props_in.get("humor_setup"))

    pers_in = _as_dict(src.get("personalization"))
    depth = _clip(
        src.get("personalization_depth") or pers_in.get("depth") or "general",
        32,
    )
    if depth not in {"general", "light_personalized", "deep_personalized"}:
        depth = "general"
    conflict_pers = _normalize_personalization_trace(
        conflict_in.get("personalization") or src.get("conflict_personalization")
    )
    if conflict_in.get("habitual_force") and not conflict_pers.get("habitual_force"):
        conflict_pers["habitual_force"] = _clip(conflict_in.get("habitual_force"), 16)
    if conflict_in.get("required_movement") and not conflict_pers.get("required_movement"):
        conflict_pers["required_movement"] = _clip(conflict_in.get("required_movement"), 16)

    return {
        "schema_version": NATIVE_LLM_SCHEMA_VERSION,
        "personalization_depth": depth,
        "personalization": {
            "depth": depth,
            "pack_confidence": pers_in.get("pack_confidence"),
            "downgraded_from": pers_in.get("downgraded_from"),
            "downgrade_reason": pers_in.get("downgrade_reason"),
        },
        "interpretive_chorus": {
            "astrology": astrology[:4],
            "day_card": day_card,
            "day_number": day_number,
            "natal": natal[:3],
        },
        "conflict": {
            "title": _clip(conflict_in.get("title") or conflict_in.get("short_name"), 160),
            "thesis": _clip(conflict_in.get("thesis"), 280),
            "force_a": _clip(conflict_in.get("force_a") or _as_dict(conflict_in.get("opposing_forces")).get("a"), 120),
            "force_b": _clip(conflict_in.get("force_b") or _as_dict(conflict_in.get("opposing_forces")).get("b"), 120),
            "why_today": _clip(conflict_in.get("why_today") or conflict_in.get("why_arose"), 320),
            "why_personal": _clip(conflict_in.get("why_personal"), 280),
            "driver_refs": [str(x).strip() for x in _as_list(conflict_in.get("driver_refs") or conflict_in.get("driver_ids")) if str(x).strip()][:5],
            "evidence_refs": [str(x).strip() for x in _as_list(conflict_in.get("evidence_refs")) if str(x).strip()][:8],
            "personalization": conflict_pers,
        },
        "scenes": scenes_out[:4],
        "prop_material": {
            "color_scene_candidates": [
                str(x).strip() for x in _as_list(props_in.get("color_scene_candidates")) if str(x).strip()
            ][:4],
            "avoid_color_trigger": _clip(props_in.get("avoid_color_trigger"), 200),
            "goal_candidates": goals[:4],
            "affirmation_tension": {
                "scene_id": _clip(affirm.get("scene_id"), 64),
                "trap": _clip(affirm.get("trap"), 160),
                "text": _clip(affirm.get("text"), 200),
            }
            if affirm.get("text") or affirm.get("scene_id")
            else None,
            "humor_setup": {
                "scene_id": _clip(humor.get("scene_id"), 64),
                "text": _clip(humor.get("text"), 200),
            }
            if humor.get("text")
            else None,
        },
        "generation_notes": _clip(src.get("generation_notes"), 400),
    }


def validate_native_scenario_llm_c1(
    payload: dict[str, Any] | None,
    *,
    allowed_evidence_ids: set[str] | None = None,
) -> list[str]:
    """Structural + architectural validation. Empty list = accept."""
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["payload_not_dict"]
    legacy = find_legacy_keys(payload)
    if legacy:
        errors.append(f"legacy_keys:{','.join(legacy)}")
    if str(payload.get("schema_version") or "") != NATIVE_LLM_SCHEMA_VERSION:
        errors.append("bad_schema_version")

    conflict = _as_dict(payload.get("conflict"))
    if not conflict.get("title"):
        errors.append("conflict_missing_title")
    if not conflict.get("force_a") or not conflict.get("force_b"):
        errors.append("conflict_missing_forces")
    # Exactly one conflict object — reject if scenes try to declare rival titles
    scenes = _as_list(payload.get("scenes"))
    if len(scenes) < 2:
        errors.append("scenes_too_few")
    if len(scenes) > 4:
        errors.append("scenes_too_many")

    chorus = _as_dict(payload.get("interpretive_chorus"))
    card = _as_dict(chorus.get("day_card"))
    number = _as_dict(chorus.get("day_number"))
    title = str(conflict.get("title") or "")
    for label, voice in (("day_card", card), ("day_number", number)):
        if not voice:
            continue
        blob = " ".join(
            str(voice.get(k) or "")
            for k in ("named_factor", "human_meaning", "link_to_conflict", "archetype_role", "tempo", "style")
        )
        if _PARALLEL_FORECAST_RE.search(blob):
            errors.append(f"parallel_forecast:{label}")
        if not str(voice.get("link_to_conflict") or "").strip():
            errors.append(f"{label}_missing_conflict_link")

    scene_ids: set[str] = set()
    for sc in scenes:
        if not isinstance(sc, dict):
            errors.append("scene_not_dict")
            continue
        sid = str(sc.get("scene_id") or "")
        sphere = str(sc.get("sphere") or "")
        if sphere not in PRODUCT_SPHERE_IDS:
            errors.append(f"scene_bad_sphere:{sphere}")
        if not sid:
            errors.append("scene_missing_id")
        elif sid in scene_ids:
            errors.append(f"scene_duplicate_id:{sid}")
        else:
            scene_ids.add(sid)
        setup = str(sc.get("setup") or "")
        if not setup:
            errors.append(f"scene_missing_setup:{sid}")
        # Conflict link: setup/opportunity/trap must mention conflict title fragment or explicit chorus conflict
        linked = False
        if title and title[:12].lower() in (setup + str(sc.get("opportunity") or "") + str(sc.get("trap") or "")).lower():
            linked = True
        if "conflict" in [str(x).lower() for x in _as_list(sc.get("chorus_refs"))]:
            linked = True
        if str(sc.get("serves_conflict") or "").strip():
            linked = True
        if not linked and title:
            # Soft: require chorus_refs include conflict
            if "conflict" not in _as_list(sc.get("chorus_refs")):
                errors.append(f"scene_missing_conflict_link:{sid or sphere}")

    # Evidence refs — only when we know the allow-list
    if allowed_evidence_ids:
        allowed = set(allowed_evidence_ids)

        def _check_refs(refs: list[Any], where: str) -> None:
            for r in refs:
                rid = str(r).strip()
                if not rid:
                    continue
                if rid not in allowed:
                    errors.append(f"unknown_evidence:{where}:{rid}")

        _check_refs(_as_list(conflict.get("driver_refs")), "conflict.driver")
        _check_refs(_as_list(conflict.get("evidence_refs")), "conflict")
        for i, sc in enumerate(scenes):
            if isinstance(sc, dict):
                _check_refs(_as_list(sc.get("evidence_refs")), f"scene[{i}]")
        for voice_name in ("astrology", "natal"):
            for i, row in enumerate(_as_list(chorus.get(voice_name))):
                if isinstance(row, dict):
                    _check_refs(_as_list(row.get("evidence_refs")), f"chorus.{voice_name}[{i}]")
        for label, voice in (("day_card", card), ("day_number", number)):
            if voice:
                _check_refs(_as_list(voice.get("evidence_refs")), f"chorus.{label}")

    # Orphan prop_material
    prop = _as_dict(payload.get("prop_material"))
    for cand in _as_list(prop.get("color_scene_candidates")):
        if str(cand).strip() and str(cand).strip() not in scene_ids:
            errors.append(f"orphan_prop_color_scene:{cand}")
    for g in _as_list(prop.get("goal_candidates")):
        if isinstance(g, dict):
            gs = str(g.get("scene_id") or "").strip()
            if gs and gs not in scene_ids:
                errors.append(f"orphan_prop_goal_scene:{gs}")
    affirm = _as_dict(prop.get("affirmation_tension"))
    if affirm.get("scene_id") and str(affirm["scene_id"]) not in scene_ids:
        errors.append("orphan_prop_affirm_scene")
    humor = _as_dict(prop.get("humor_setup"))
    if humor.get("scene_id") and str(humor["scene_id"]) not in scene_ids:
        errors.append("orphan_prop_humor_scene")

    return errors


def native_llm_to_day_scenario_v1(
    native: dict[str, Any],
    *,
    interpretation: dict[str, Any] | None = None,
    ritual_context: dict[str, Any] | None = None,
    celestial_events: dict[str, Any] | None = None,
    day_thesis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Map validated native LLM payload → day_scenario_v1; props deterministic."""
    norm = normalize_native_scenario_llm_c1(native)
    interp = _as_dict(interpretation)
    foundation = build_scenario_foundation_v1(
        interpretation=interp,
        day_events_pack=interp.get("day_events_pack")
        if isinstance(interp.get("day_events_pack"), dict)
        else None,
        ritual_context=ritual_context,
        celestial_events=celestial_events,
    )
    thesis_in = day_thesis if isinstance(day_thesis, dict) else _as_dict(interp.get("day_thesis"))
    conflict_n = _as_dict(norm.get("conflict"))
    title = str(conflict_n.get("title") or thesis_in.get("label_ru") or "Сюжет дня").strip()
    conflict = {
        "contract_version": "day_scenario_conflict_v1",
        "short_name": title,
        "thesis": {
            "family": thesis_in.get("family") or "momentum",
            "variant": thesis_in.get("variant") or "steady_productive_rhythm",
            "mode": thesis_in.get("mode") or "stability",
            "label_ru": title,
            "day_thesis": thesis_in,
            "llm_thesis": conflict_n.get("thesis"),
        },
        "opposing_forces": {
            "a": conflict_n.get("force_a") or "автопилот",
            "b": conflict_n.get("force_b") or "осознанный выбор",
        },
        "why_arose": conflict_n.get("why_today") or "",
        "why_personal": conflict_n.get("why_personal") or "",
        "driver_ids": list(conflict_n.get("driver_refs") or thesis_in.get("driver_ids") or [])[:3],
        "chorus_references": ["astrology", "day_card", "day_number", "natal"],
        "confidence": 0.72,
        "foundation_rule": "Native LLM conflict; facts from foundation; card/number do not invent rival plot.",
        "evidence_refs": list(conflict_n.get("evidence_refs") or []),
        "personalization": _as_dict(conflict_n.get("personalization")),
    }
    from todayflow_backend.services.today_natal_activations_v1 import natal_conflict_driver_ids

    natal_ids = natal_conflict_driver_ids(foundation.get("personal_natal_activations"))
    if natal_ids:
        conflict["driver_ids"] = natal_ids

    chorus_n = _as_dict(norm.get("interpretive_chorus"))
    astrology = []
    for row in _as_list(chorus_n.get("astrology")):
        if not isinstance(row, dict):
            continue
        astrology.append(
            {
                "voice": "astrology",
                "named_factor": row.get("named_factor"),
                "human_meaning": row.get("human_meaning"),
                "link_to_conflict": row.get("link_to_conflict"),
                "conflict_id": row.get("conflict_id"),
                "evidence_ref": (_as_list(row.get("evidence_refs")) or [None])[0],
                "evidence_refs": list(row.get("evidence_refs") or []),
            }
        )
    card_n = _as_dict(chorus_n.get("day_card"))
    card_voice = None
    if card_n.get("named_factor"):
        card_voice = {
            "voice": "day_card",
            "named_factor": card_n.get("named_factor"),
            "archetype_role": card_n.get("archetype_role") or card_n.get("link_to_conflict"),
            "link_to_conflict": card_n.get("link_to_conflict"),
            "conflict_id": card_n.get("conflict_id"),
            "human_meaning": card_n.get("link_to_conflict") or card_n.get("human_meaning"),
            "evidence_refs": list(card_n.get("evidence_refs") or []),
            "is_not_astro_proof": True,
            "must_not_invent_second_plot": True,
        }
    number_n = _as_dict(chorus_n.get("day_number"))
    number_voice = None
    if number_n.get("named_factor"):
        number_voice = {
            "voice": "day_number",
            "named_factor": number_n.get("named_factor"),
            "tempo": number_n.get("tempo"),
            "style": number_n.get("style"),
            "link_to_conflict": number_n.get("link_to_conflict"),
            "conflict_id": number_n.get("conflict_id"),
            "human_meaning": number_n.get("link_to_conflict") or number_n.get("human_meaning"),
            "evidence_refs": list(number_n.get("evidence_refs") or []),
            "must_not_invent_second_plot": True,
        }
    natal = []
    for row in _as_list(chorus_n.get("natal")):
        if not isinstance(row, dict):
            continue
        natal.append(
            {
                "voice": "natal",
                "named_factor": row.get("named_factor"),
                "human_meaning": row.get("human_meaning"),
                "link_to_conflict": row.get("link_to_conflict"),
                "conflict_id": row.get("conflict_id"),
                "evidence_refs": list(row.get("evidence_refs") or []),
            }
        )
    chorus = {
        "contract_version": "day_scenario_chorus_v1",
        "astrology": astrology,
        "day_card": card_voice,
        "day_number": number_voice,
        "natal": natal,
        "dialogue_rule": "Four voices explain one conflict; no parallel forecasts.",
        "parallel_forecast_forbidden": True,
    }

    scenes: list[dict[str, Any]] = []
    for idx, sc in enumerate(_as_list(norm.get("scenes"))):
        if not isinstance(sc, dict):
            continue
        sphere = str(sc.get("sphere") or "")
        scenes.append(
            {
                "scene_id": sc.get("scene_id"),
                "sphere": sphere,
                "sphere_label_ru": _SPHERE_LABEL_RU.get(sphere, sphere),
                "role_in_story": sc.get("role_in_story") or ("primary" if idx == 0 else "support"),
                "what_happens": sc.get("setup"),
                "why": conflict.get("why_arose"),
                "opportunity": sc.get("opportunity"),
                "trap": sc.get("trap"),
                "recommended_action": sc.get("recommended_action"),
                "do_not": sc.get("avoid_action"),
                "domestic_example": sc.get("everyday_example"),
                "evidence_references": list(sc.get("evidence_refs") or []),
                "chorus_references": list(sc.get("chorus_refs") or ["conflict"]),
                "confidence": 0.7,
                "serves_conflict": title,
            }
        )

    props = build_scenario_props_v1(conflict=conflict, scenes=scenes, chorus=chorus)
    # Attach LLM prop_material as diagnostics only (not SoT for final color)
    props["prop_material_llm"] = norm.get("prop_material")

    return {
        "contract_version": DAY_SCENARIO_V1_CONTRACT,
        "version": DAY_SCENARIO_V1_VERSION,
        "runtime_sot": True,
        "ready": bool(scenes) and bool(title),
        "generation_source": GENERATION_SOURCE_NATIVE,
        "native_schema_version": NATIVE_LLM_SCHEMA_VERSION,
        "foundation": foundation,
        "chorus": chorus,
        "conflict": conflict,
        "scenes": scenes,
        "props": props,
        "projections": {
            "status": "day_scenario_project_v1.b5",
            "note": "Native LLM scenario; props deterministic; legacy slots projections only.",
        },
        "generation_notes": norm.get("generation_notes"),
    }


def mark_deterministic_generation_source(scenario: dict[str, Any] | None) -> dict[str, Any]:
    """Tag B5 deterministic engine scenarios for valid cache after C1."""
    scen = dict(scenario) if isinstance(scenario, dict) else {}
    if not scen.get("generation_source"):
        scen["generation_source"] = GENERATION_SOURCE_DETERMINISTIC
    return scen


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


def call_day_scenario_native_llm_c1(
    user_json: dict[str, Any],
    *,
    interpretation: dict[str, Any] | None = None,
    ritual_context: dict[str, Any] | None = None,
    celestial_events: dict[str, Any] | None = None,
    max_attempts: int = 2,
) -> dict[str, Any] | None:
    """Generate native scenario via LLM. Returns day_scenario_v1 or None after hard fails.

    Pipeline per attempt (C3.6 / C3.6.3):
      parse → hard schema validate → quality analysis (editorial + personalization)
      → maturity policy (hard + promoted quality) → map → hard structural validate
      → accept with scores/defects in editorial_meta.

    Default quality remains observe-only. C3.6.3 promotes SCENE_CLONE /
    SCENE_MISSING_EVERYDAY / SCENE_ABSTRACT / ASTRO_JARGON_BARE to blocking
    (retry then unavailable). Still no quality→general downgrade.
    Hard: PROFILE_FACT_LEAK, broken evidence refs, schema/SoT.
    """
    from todayflow_backend.services.day_scenario_editorial_gate_c31 import (
        format_editorial_retry_feedback,
        run_editorial_quality_gate_c31,
        score_editorial_quality_c31,
    )
    from todayflow_backend.services.day_scenario_gate_maturity_c36 import (
        annotate_defects_with_maturity,
        is_hard_native_validate_error,
        is_hard_scenario_validate_error,
        maturity_summary,
        public_defect_view,
        should_reject_story,
        should_retry_defects,
    )
    from todayflow_backend.services.day_scenario_personalization_c33 import (
        DEPTH_DEEP,
        DEPTH_GENERAL,
        DEFECT_PROFILE_FACT_LEAK,
        build_personalization_evidence_pack_c33,
        format_personalization_retry_feedback,
        run_personalization_gate_c33,
        score_personalization_c33,
    )
    from todayflow_backend.services.day_story_capture_session_v0 import get_day_story_capture_session

    if not is_llm_chat_configured():
        return None
    # Refresh/enrichment only — never GET. Use background timeout budget.
    client = get_openai_compatible_client(operation="background")
    if client is None:
        return None

    interp = interpretation or (
        user_json.get("interpretation") if isinstance(user_json.get("interpretation"), dict) else {}
    )
    if not isinstance(interp, dict):
        interp = {}

    allowed = collect_allowed_evidence_ids(
        interpretation=interp,
        ritual_context=ritual_context,
        celestial_events=celestial_events,
    )

    pers_pack = build_personalization_evidence_pack_c33(interp)
    from todayflow_backend.services.day_scenario_sphere_selection_c33b import (
        attach_sphere_selection_to_pack,
        run_sphere_selection_gate_c33b,
    )

    ritual = _as_dict(ritual_context)
    thesis = _as_dict(interp.get("day_thesis"))
    domains_present = []
    for d in _as_list(interp.get("domains_present") or _as_dict(interp.get("domain_presence")).get("present")):
        if isinstance(d, str):
            domains_present.append(d)
        elif isinstance(d, dict) and d.get("id"):
            domains_present.append(str(d["id"]))
    pers_pack = attach_sphere_selection_to_pack(
        pers_pack,
        day_domains=domains_present,
        ritual_head_topic=str(ritual.get("head_topic") or "") or None,
        thesis_family=str(thesis.get("family") or "") or None,
    )
    has_natal_evidence = str(pers_pack.get("evidence_depth") or "") == DEPTH_DEEP

    from todayflow_backend.services.day_scenario_dramaturgy_brief_c4 import (
        build_day_dramaturgy_brief_c4,
        format_native_user_message_c4,
        slim_interpretation_for_native_llm,
    )

    brief = build_day_dramaturgy_brief_c4(
        interpretation=interp,
        ritual_context=ritual,
        personalization_pack=pers_pack,
    )

    # Bounded LLM input: brief first (protected); slim interpretation; no raw day_personal
    llm_payload = dict(user_json) if isinstance(user_json, dict) else {}
    llm_payload["personalization_evidence"] = pers_pack
    llm_payload.pop("day_personal", None)
    llm_payload.pop("day_thesis", None)  # demoted into brief.act_iii_registry_label
    if isinstance(llm_payload.get("interpretation"), dict):
        llm_payload["interpretation"] = slim_interpretation_for_native_llm(
            llm_payload["interpretation"],
            brief=brief,
        )
    else:
        llm_payload["interpretation"] = slim_interpretation_for_native_llm(interp, brief=brief)

    attempts = max(1, min(int(max_attempts or 1), 3))
    user_full, user_base = format_native_user_message_c4(
        brief=brief,
        context=llm_payload,
        max_chars=16000,
    )
    user_sent = user_base
    retry_feedback = ""
    model_name = ""
    try:
        model_name = str(resolve_default_chat_model() or "")
    except Exception:
        model_name = ""

    capture = get_day_story_capture_session()
    from todayflow_backend.services.llm_practitioner_persona_v1 import with_practitioner_persona

    system = with_practitioner_persona(_NATIVE_SYS_RU, locale="ru")
    if capture is not None:
        capture.record_prompt(
            system=system,
            user_full=user_full,
            user_sent=user_sent,
            prompt_version=NATIVE_PROMPT_VERSION,
            model=model_name or None,
        )
        meta = capture.pack.setdefault("generation_metadata", {})
        if isinstance(meta, dict):
            meta["dramaturgy_brief_c4"] = brief
            meta["dramaturgy_brief_protected"] = True
            meta["user_message_format"] = "dramaturgy_brief_c4_v1"

    last_pers_defects: list[dict[str, str]] = []

    for attempt_idx in range(attempts):
        if retry_feedback:
            # Keep brief intact; append feedback after protected base
            user_sent = f"{user_base}\n\n---\n{retry_feedback}"[:18000]
        content = chat_completion_plain(
            client,
            model=resolve_default_chat_model(),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_sent},
            ],
            temperature=0.52,
            max_tokens=resolve_max_tokens(4800),
        )
        if not content:
            if capture is not None:
                capture.record_attempt(
                    attempt_index=attempt_idx,
                    raw_response=None,
                    parsed=None,
                    after_normalize=None,
                    after_gate=None,
                    status="empty_response",
                    reject_reason="empty_llm_content",
                )
            continue
        parsed = _parse_json_content(content)
        if not parsed:
            if capture is not None:
                capture.record_attempt(
                    attempt_index=attempt_idx,
                    raw_response=content,
                    parsed=None,
                    after_normalize=None,
                    after_gate=None,
                    status="parse_fail",
                    reject_reason="json_parse_failed",
                )
            continue
        normalized = normalize_native_scenario_llm_c1(parsed)
        # Align declared depth with pack if model omitted it
        if not normalized.get("personalization_depth"):
            normalized["personalization_depth"] = pers_pack.get("evidence_depth") or DEPTH_GENERAL
            normalized["personalization"] = {
                **_as_dict(normalized.get("personalization")),
                "depth": normalized["personalization_depth"],
                "pack_confidence": pers_pack.get("confidence"),
            }

        errors = validate_native_scenario_llm_c1(normalized, allowed_evidence_ids=allowed)
        legacy_raw = find_legacy_keys(parsed)
        if legacy_raw:
            errors = list(errors) + [f"legacy_keys:{','.join(legacy_raw)}"]
        hard_errors = [e for e in errors if is_hard_native_validate_error(e)]
        soft_native = [e for e in errors if not is_hard_native_validate_error(e)]
        if hard_errors:
            if capture is not None:
                capture.record_attempt(
                    attempt_index=attempt_idx,
                    raw_response=content,
                    parsed=parsed,
                    after_normalize=normalized,
                    after_gate=None,
                    status="native_validation_reject",
                    reject_reason=";".join(hard_errors[:8]),
                )
            retry_feedback = "Исправь schema/validation ошибки: " + "; ".join(hard_errors[:6])
            continue
        # Soft native findings (e.g. parallel_forecast regex) → capture only.
        if soft_native and capture is not None:
            try:
                for e in soft_native[:12]:
                    capture.add_defect(
                        "NATIVE_SOFT_VALIDATE",
                        f"{e}|maturity=experimental|action=score_only",
                        cls="VALIDATION",
                    )
            except Exception:
                pass

        # --- Quality analysis (C3.1–C3.3b): always measure; maturity decides runtime ---
        pers_defects = run_personalization_gate_c33(normalized, pers_pack)
        pers_defects = list(pers_defects) + list(run_sphere_selection_gate_c33b(normalized, pers_pack))
        pers_defects = annotate_defects_with_maturity(pers_defects)
        last_pers_defects = pers_defects
        pers_score = score_personalization_c33(pers_defects)

        # Hard personalization: reject_story (e.g. PROFILE_FACT_LEAK) wins over retry.
        # Leaked prose must never reach the user or a quality-rewrite retry prompt.
        if should_reject_story(pers_defects):
            if capture is not None:
                capture.record_attempt(
                    attempt_index=attempt_idx,
                    raw_response=content,
                    parsed=parsed,
                    after_normalize={
                        **normalized,
                        "personalization_score": pers_score,
                        "personalization_defects": pers_defects,
                        "gate_maturity": maturity_summary(pers_defects),
                    },
                    after_gate=None,
                    status="personalization_reject_story",
                    reject_reason=";".join(str(d.get("code")) for d in pers_defects[:8]),
                )
                try:
                    for d in pers_defects:
                        capture.add_defect(
                            str(d.get("code") or "PERSONALIZATION"),
                            f"{d.get('field')}:{d.get('message')}|maturity={d.get('gate_maturity')}"
                            f"|action={d.get('runtime_action')}",
                            cls="PERSONALIZATION",
                        )
                except Exception:
                    pass
            return None
        if should_retry_defects(pers_defects):
            # Hard orphan/refs only — never include PROFILE_FACT_LEAK in retry feedback.
            retryable = [
                d
                for d in pers_defects
                if str(d.get("runtime_action")) == "retry"
                and str(d.get("code")) != DEFECT_PROFILE_FACT_LEAK
            ]
            if attempt_idx + 1 < attempts and retryable:
                feedback = format_personalization_retry_feedback(retryable, pack=pers_pack)
                if capture is not None:
                    capture.record_attempt(
                        attempt_index=attempt_idx,
                        raw_response=content,
                        parsed=parsed,
                        after_normalize={
                            **normalized,
                            "personalization_score": pers_score,
                            "personalization_defects": pers_defects,
                            "gate_maturity": maturity_summary(pers_defects),
                        },
                        after_gate=None,
                        status="personalization_hard_retry",
                        reject_reason=";".join(str(d.get("code")) for d in retryable[:8]),
                    )
                    try:
                        for d in pers_defects:
                            capture.add_defect(
                                str(d.get("code") or "PERSONALIZATION"),
                                f"{d.get('field')}:{d.get('message')}|maturity={d.get('gate_maturity')}",
                                cls="PERSONALIZATION",
                            )
                    except Exception:
                        pass
                retry_feedback = feedback
                continue
            if capture is not None:
                capture.record_attempt(
                    attempt_index=attempt_idx,
                    raw_response=content,
                    parsed=parsed,
                    after_normalize=normalized,
                    after_gate=None,
                    status="personalization_reject_story",
                    reject_reason=";".join(str(d.get("code")) for d in pers_defects[:8]),
                )
            return None
        # Quality personalization defects (non-blocking maturity): keep first valid story.

        editorial = run_editorial_quality_gate_c31(
            normalized,
            has_natal_evidence=has_natal_evidence if has_natal_evidence else False,
        )
        natal_rows = _as_list(_as_dict(normalized.get("interpretive_chorus")).get("natal"))
        if natal_rows and not has_natal_evidence:
            editorial = run_editorial_quality_gate_c31(normalized, has_natal_evidence=False)
        editorial = annotate_defects_with_maturity(editorial)
        ed_score = score_editorial_quality_c31(editorial)

        # C3.6.3: promoted quality codes may retry / reject via maturity registry.
        if should_reject_story(editorial):
            if capture is not None:
                capture.record_attempt(
                    attempt_index=attempt_idx,
                    raw_response=content,
                    parsed=parsed,
                    after_normalize={
                        **normalized,
                        "editorial_score": ed_score,
                        "editorial_defects": editorial,
                        "gate_maturity": maturity_summary(editorial),
                    },
                    after_gate=None,
                    status="editorial_reject_story",
                    reject_reason=";".join(str(d.get("code")) for d in editorial[:8]),
                )
                try:
                    for d in editorial:
                        capture.add_defect(
                            str(d.get("code") or "EDITORIAL"),
                            f"{d.get('field')}:{d.get('message')}|maturity={d.get('gate_maturity')}"
                            f"|action={d.get('runtime_action')}",
                            cls=str(d.get("capture_class") or "VALIDATION"),
                        )
                except Exception:
                    pass
            return None
        if should_retry_defects(editorial):
            retryable = [d for d in editorial if str(d.get("runtime_action")) == "retry"]
            if attempt_idx + 1 < attempts and retryable:
                feedback = format_editorial_retry_feedback(retryable)
                if capture is not None:
                    capture.record_attempt(
                        attempt_index=attempt_idx,
                        raw_response=content,
                        parsed=parsed,
                        after_normalize={
                            **normalized,
                            "editorial_score": ed_score,
                            "editorial_defects": editorial,
                            "gate_maturity": maturity_summary(editorial),
                        },
                        after_gate=None,
                        status="editorial_quality_retry",
                        reject_reason=";".join(str(d.get("code")) for d in retryable[:8]),
                    )
                    try:
                        for d in editorial:
                            capture.add_defect(
                                str(d.get("code") or "EDITORIAL"),
                                f"{d.get('field')}:{d.get('message')}|maturity={d.get('gate_maturity')}"
                                f"|action={d.get('runtime_action')}",
                                cls=str(d.get("capture_class") or "VALIDATION"),
                            )
                    except Exception:
                        pass
                retry_feedback = feedback
                continue
            if capture is not None:
                capture.record_attempt(
                    attempt_index=attempt_idx,
                    raw_response=content,
                    parsed=parsed,
                    after_normalize={
                        **normalized,
                        "editorial_score": ed_score,
                        "editorial_defects": editorial,
                        "gate_maturity": maturity_summary(editorial),
                    },
                    after_gate=None,
                    status="editorial_reject_story",
                    reject_reason=";".join(str(d.get("code")) for d in editorial[:8]),
                )
            return None

        # Remaining editorial defects: observe only (score + capture).
        if editorial and capture is not None:
            try:
                for d in editorial:
                    if str(d.get("runtime_action") or "score_only") != "score_only":
                        continue
                    capture.add_defect(
                        str(d.get("code") or "EDITORIAL"),
                        f"{d.get('field')}:{d.get('message')}|maturity={d.get('gate_maturity')}"
                        f"|action=score_only",
                        cls=str(d.get("capture_class") or "VALIDATION"),
                    )
            except Exception:
                pass
        if pers_defects and capture is not None:
            try:
                for d in pers_defects:
                    if str(d.get("runtime_action") or "score_only") != "score_only":
                        continue
                    capture.add_defect(
                        str(d.get("code") or "PERSONALIZATION"),
                        f"{d.get('field')}:{d.get('message')}|maturity={d.get('gate_maturity')}"
                        f"|action=score_only",
                        cls="PERSONALIZATION",
                    )
            except Exception:
                pass

        scenario = native_llm_to_day_scenario_v1(
            normalized,
            interpretation=interp,
            ritual_context=ritual_context,
            celestial_events=celestial_events,
            day_thesis=_as_dict(interp.get("day_thesis")),
        )
        scen_errors = validate_day_scenario_v1(scenario)
        hard = [e for e in scen_errors if is_hard_scenario_validate_error(e)]
        if hard:
            if capture is not None:
                capture.record_attempt(
                    attempt_index=attempt_idx,
                    raw_response=content,
                    parsed=parsed,
                    after_normalize=normalized,
                    after_gate=scenario,
                    status="scenario_validate_reject",
                    reject_reason=";".join(hard),
                )
            retry_feedback = "Исправь structural/SoT ошибки: " + "; ".join(hard[:6])
            continue
        if capture is not None:
            capture.record_attempt(
                attempt_index=attempt_idx,
                raw_response=content,
                parsed=parsed,
                after_normalize={
                    **normalized,
                    "editorial_score": ed_score,
                    "editorial_defects": editorial,
                    "personalization_score": pers_score,
                    "personalization_defects": pers_defects,
                    "gate_maturity": {
                        "editorial": maturity_summary(editorial),
                        "personalization": maturity_summary(pers_defects),
                        "policy": "hard_plus_promoted_quality_blocking_c363",
                    },
                },
                after_gate=scenario,
                status="accepted_native_c36",
            )
        scenario["personalization_depth"] = normalized.get("personalization_depth") or DEPTH_GENERAL
        scenario["personalization_evidence"] = {
            "evidence_depth": pers_pack.get("evidence_depth"),
            "confidence": pers_pack.get("confidence"),
            "evidence_refs": list(pers_pack.get("evidence_refs") or [])[:12],
            "tendency_ids": [
                t.get("id")
                for t in _as_list(pers_pack.get("behavioral_tendencies"))
                if isinstance(t, dict)
            ][:6],
            "sphere_selection": _as_dict(pers_pack.get("sphere_selection")),
        }
        # Public editorial_meta keeps pre-C3.6 analyzer shape only.
        # gate_maturity / runtime_action / policy live in capture metadata (not API).
        scenario["editorial_meta"] = {
            "prompt_version": NATIVE_PROMPT_VERSION,
            "model_version": model_name,
            "native_schema_version": NATIVE_LLM_SCHEMA_VERSION,
            "editorial_score": ed_score,
            "editorial_defects": public_defect_view(editorial),
            "personalization_score": pers_score,
            "personalization_defects": public_defect_view(last_pers_defects),
            "personalization_depth": scenario["personalization_depth"],
        }
        return scenario
    return None
