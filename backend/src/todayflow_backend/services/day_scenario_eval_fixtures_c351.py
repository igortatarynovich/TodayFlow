"""C3.5.1 — Eval fixtures: good natives, negative cases, mutations (eval-only)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from todayflow_backend.services.day_scenario_native_llm_c1 import NATIVE_LLM_SCHEMA_VERSION
from todayflow_backend.services.day_scenario_editorial_gate_c31 import conflict_anchor_id


def _cid(title: str) -> str:
    return conflict_anchor_id({"title": title})

# ---------------------------------------------------------------------------
# Good baselines
# ---------------------------------------------------------------------------


def _good_scene_ru(sphere: str, *, sid: str | None = None) -> dict[str, Any]:
    return {
        "scene_id": sid or f"scene.{sphere}",
        "sphere": sphere,
        "role_in_story": "primary" if sphere == "relationships" else "support",
        "setup": "В мессенджере спрашивают «всё ли в порядке?» именно когда хочется ответить «нормально».",
        "opportunity": "Написать коротко и честно: «Нужна минута — отвечу по делу».",
        "trap": "Согласиться ради тишины и потом злиться, что вас не поняли.",
        "recommended_action": "Открыть черновик сообщения и отправить после паузы в один абзац.",
        "avoid_action": "Не отвечать автоматическим «всё ок» без смысла.",
        "everyday_example": "Сообщение от партнёра в 21:40: вопрос «ты где?» — момент закрыться или назвать факт.",
        "evidence_refs": ["moon-pisces", "sky-factor"],
        "chorus_refs": ["conflict", "day_card"],
    }


def _good_scene_en(sphere: str, *, sid: str | None = None) -> dict[str, Any]:
    return {
        "scene_id": sid or f"scene.{sphere}",
        "sphere": sphere,
        "role_in_story": "primary" if sphere == "relationships" else "support",
        "setup": "A chat message asks “are you okay?” exactly when you want to answer “fine”.",
        "opportunity": "Reply short and honest: “Need a minute — I’ll answer on the point.”",
        "trap": "Agree for quiet and resent that they never understood you.",
        "recommended_action": "Open a draft message and send one paragraph after a short pause.",
        "avoid_action": "Do not reply with automatic “I’m fine” without meaning.",
        "everyday_example": "Partner message at 21:40: “where are you?” — close up or name one fact.",
        "evidence_refs": ["moon-pisces", "sky-factor"],
        "chorus_refs": ["conflict", "day_card"],
    }


def _day_closure_ru() -> dict[str, str]:
    return {
        "resolution": "К вечеру вы назвали одну точную фразу вместо сглаживания.",
        "remaining_tension": "Остаётся лёгкое желание снова ответить «всё нормально».",
        "evening_state": "Тише, но без ложной гармонии — контакт сохранён через ясность.",
        "conflict_callback": "Конфликт «прояснение против сглаживания» закрыт выбором короткой честности.",
    }


def _day_closure_en() -> dict[str, str]:
    return {
        "resolution": "By evening you named one precise sentence instead of smoothing.",
        "remaining_tension": "A mild urge remains to answer “everything’s fine” again.",
        "evening_state": "Quieter, without false harmony — contact held through clarity.",
        "conflict_callback": "The conflict “clarity versus smoothing” closed by choosing short honesty.",
    }


def good_native_ru() -> dict[str, Any]:
    title = "Прояснение против сглаживания"
    cid = _cid(title)
    return {
        "schema_version": NATIVE_LLM_SCHEMA_VERSION,
        "personalization_depth": "deep_personalized",
        "interpretive_chorus": {
            "astrology": [
                {
                    "named_factor": "Луна в Рыбах",
                    "human_meaning": "Эмоциональный подтекст становится заметнее прямых слов.",
                    "link_to_conflict": "Поэтому хочется сгладить, хотя нужен короткий ясный ответ.",
                    "evidence_refs": ["moon-pisces"],
                    "conflict_id": cid,
                }
            ],
            "day_card": {
                "named_factor": "Карта дня — Отшельник",
                "archetype_role": "Пауза перед ответом.",
                "link_to_conflict": "Архетип того же выбора: сначала понять, потом говорить.",
                "evidence_refs": ["day_card"],
                "conflict_id": cid,
            },
            "day_number": {
                "named_factor": "Число дня — 7",
                "tempo": "сначала понять",
                "style": "без спешки",
                "link_to_conflict": "Число задаёт ритм прохождения конфликта прояснения.",
                "evidence_refs": ["day_number"],
                "conflict_id": cid,
            },
            "natal": [
                {
                    "named_factor": "Луна в 7 доме",
                    "human_meaning": "Привычка сглаживать ради тишины в отношениях.",
                    "link_to_conflict": "Личная привычка тянет к силе A в том же конфликте.",
                    "evidence_refs": ["claim.personal.moon7.smooth"],
                    "conflict_id": cid,
                }
            ],
        },
        "conflict": {
            "title": title,
            "thesis": "Сегодня важнее назвать точно, чем сохранить ложную гармонию.",
            "force_a": "сгладить ради тишины",
            "force_b": "сказать коротко и честно",
            "why_today": "Луна в Рыбах усиливает эмоциональный подтекст.",
            "why_personal": "Привычка сглаживать в отношениях тянет к силе A.",
            "driver_refs": ["moon-pisces"],
            "evidence_refs": ["moon-pisces", "claim.personal.moon7.smooth"],
        },
        "scenes": [
            _good_scene_ru("relationships"),
            {
                **_good_scene_ru("work_decisions"),
                "setup": "Коллега в чате просит «быстро окнуть» письмо, которое вы ещё не дочитали.",
                "opportunity": "Ответить: «Вернусь через 20 минут с точной правкой».",
                "trap": "Поставить «ок» и потом чинить чужие ожидания.",
                "recommended_action": "Одно сообщение с временем возврата.",
                "avoid_action": "Не ставить реакцию без чтения.",
                "everyday_example": "Рабочий чат, 11:15: «ок?» под длинным письмом.",
                "chorus_refs": ["conflict", "astrology"],
            },
        ],
        "prop_material": {
            "color_scene_candidates": ["scene.relationships"],
            "affirmation_tension": {
                "scene_id": "scene.relationships",
                "trap": "сгладить",
                "text": "Я могу сказать коротко и остаться в контакте.",
            },
            "color": {
                "scene_id": "scene.relationships",
                "name": "глубокий синий",
                "note": "Цвет паузы перед ясным ответом.",
            },
        },
        "day_closure": _day_closure_ru(),
    }


def good_native_en() -> dict[str, Any]:
    title = "Clarity versus smoothing"
    cid = _cid(title)
    return {
        "schema_version": NATIVE_LLM_SCHEMA_VERSION,
        "personalization_depth": "deep_personalized",
        "interpretive_chorus": {
            "astrology": [
                {
                    "named_factor": "Moon in Pisces",
                    "human_meaning": "Emotional subtext becomes louder than direct words.",
                    "link_to_conflict": "That is why you want to smooth, though a short clear reply is needed.",
                    "evidence_refs": ["moon-pisces"],
                    "conflict_id": cid,
                }
            ],
            "day_card": {
                "named_factor": "Day card — The Hermit",
                "archetype_role": "Pause before answering.",
                "link_to_conflict": "Archetype of the same choice: understand first, then speak.",
                "evidence_refs": ["day_card"],
                "conflict_id": cid,
            },
            "day_number": {
                "named_factor": "Day number — 7",
                "tempo": "understand first",
                "style": "without rush",
                "link_to_conflict": "The number sets the rhythm through the clarity conflict.",
                "evidence_refs": ["day_number"],
                "conflict_id": cid,
            },
            "natal": [
                {
                    "named_factor": "Moon in the 7th house",
                    "human_meaning": "Habit of smoothing for quiet in relationships.",
                    "link_to_conflict": "Personal habit pulls toward force A in the same conflict.",
                    "evidence_refs": ["claim.personal.moon7.smooth"],
                    "conflict_id": cid,
                }
            ],
        },
        "conflict": {
            "title": title,
            "thesis": "Today it matters more to name precisely than keep false harmony.",
            "force_a": "smooth for quiet",
            "force_b": "say it short and honest",
            "why_today": "Moon in Pisces amplifies emotional subtext.",
            "why_personal": "Habit of smoothing in relationships pulls toward force A.",
            "driver_refs": ["moon-pisces"],
            "evidence_refs": ["moon-pisces", "claim.personal.moon7.smooth"],
        },
        "scenes": [
            _good_scene_en("relationships"),
            {
                **_good_scene_en("work_decisions"),
                "setup": "A colleague in chat asks you to quickly OK an email you have not finished reading.",
                "opportunity": "Reply: “Back in 20 minutes with the exact edit.”",
                "trap": "Hit “ok” and then repair expectations.",
                "recommended_action": "One message with a return time.",
                "avoid_action": "Do not react before reading.",
                "everyday_example": "Work chat, 11:15: “ok?” under a long email.",
                "chorus_refs": ["conflict", "astrology"],
            },
        ],
        "prop_material": {
            "color_scene_candidates": ["scene.relationships"],
            "affirmation_tension": {
                "scene_id": "scene.relationships",
                "trap": "smooth",
                "text": "I can say it short and stay in contact.",
            },
            "color": {
                "scene_id": "scene.relationships",
                "name": "deep blue",
                "note": "Color of the pause before a clear reply.",
            },
        },
        "day_closure": _day_closure_en(),
    }


# ---------------------------------------------------------------------------
# Negative fixtures (complete natives keyed by failure mode)
# ---------------------------------------------------------------------------


def _neg_conflict_no_opposition() -> dict[str, Any]:
    n = good_native_ru()
    n["conflict"]["force_b"] = ""
    n["conflict"]["force_a"] = "просто день"
    return n


def _neg_abstract_scenes() -> dict[str, Any]:
    n = good_native_ru()
    n["scenes"][0] = {
        "scene_id": "scene.relationships",
        "sphere": "relationships",
        "role_in_story": "primary",
        "setup": "В отношениях возможна напряжённость.",
        "opportunity": "Сохраняйте границы.",
        "trap": "Не распыляйтесь.",
        "recommended_action": "Слушайте себя.",
        "avoid_action": "Избегайте конфликтов.",
        "everyday_example": "Баланс важен в сфере отношений.",
        "evidence_refs": ["moon-pisces"],
        "chorus_refs": ["conflict"],
    }
    return n


def _neg_clone_scenes() -> dict[str, Any]:
    n = good_native_ru()
    clone = dict(n["scenes"][0])
    clone["scene_id"] = "scene.communication"
    clone["sphere"] = "communication"
    n["scenes"][1] = clone
    return n


def _neg_parallel_chorus() -> dict[str, Any]:
    n = good_native_ru()
    n["interpretive_chorus"]["astrology"] = [
        {
            "named_factor": "Луна в Рыбах",
            "human_meaning": "Отдельный прогноз про эмоции без связи.",
            "link_to_conflict": "",
            "evidence_refs": ["moon-pisces"],
        }
    ]
    n["interpretive_chorus"]["day_card"] = {
        "named_factor": "Отшельник",
        "archetype_role": "Ещё один независимый прогноз.",
        "link_to_conflict": "",
        "evidence_refs": ["day_card"],
    }
    return n


def _neg_decorative_personalization() -> dict[str, Any]:
    n = good_native_ru()
    n["personalization_depth"] = "general"
    n["scenes"][0]["recommended_action"] = (
        "Как человек с Луной в 7 доме, вы всегда сглаживаете — скажите иначе."
    )
    n["scenes"][0]["personalization"] = {
        "personalization_level": "general",
        "personalization_evidence_refs": ["claim.personal.moon7.smooth"],
    }
    return n


def _neg_recommendation_without_evidence() -> dict[str, Any]:
    n = good_native_ru()
    for s in n["scenes"]:
        s.pop("evidence_refs", None)
        s.pop("chorus_refs", None)
        s.pop("personalization", None)
    return n


def _neg_missing_day_closure() -> dict[str, Any]:
    n = good_native_ru()
    n.pop("day_closure", None)
    return n


def _neg_wellness_closure() -> dict[str, Any]:
    n = good_native_ru()
    n["day_closure"] = {
        "resolution": "Доверьтесь вселенной — вы достаточны.",
        "remaining_tension": "Everything happens for a reason.",
        "evening_state": "Trust the universe; you are enough.",
        "conflict_callback": "The universe has your back today.",
    }
    return n


def _neg_locale_mismatch_en_cyrillic() -> dict[str, Any]:
    """EN cell filled with Cyrillic prose (locale mismatch)."""
    n = good_native_ru()
    n["schema_version"] = NATIVE_LLM_SCHEMA_VERSION
    return n


def _neg_locale_mismatch_ru_latin() -> dict[str, Any]:
    """RU cell filled with Latin prose (locale mismatch)."""
    n = good_native_en()
    n["schema_version"] = NATIVE_LLM_SCHEMA_VERSION
    return n


def _neg_no_birth_time_deep_natal() -> dict[str, Any]:
    n = good_native_ru()
    n["personalization_depth"] = "deep_personalized"
    n["interpretive_chorus"]["natal"] = [
        {
            "named_factor": "Луна в 7 доме",
            "human_meaning": "Глубокая натальная претензия без времени рождения.",
            "link_to_conflict": "Личная привычка тянет к силе A.",
            "evidence_refs": ["claim.personal.moon7.smooth"],
            "conflict_id": _cid(str(n["conflict"]["title"])),
        }
    ]
    return n


NEGATIVE_FIXTURES: dict[str, dict[str, Any]] = {
    "conflict_no_opposition": _neg_conflict_no_opposition(),
    "abstract_scenes": _neg_abstract_scenes(),
    "clone_scenes": _neg_clone_scenes(),
    "parallel_chorus": _neg_parallel_chorus(),
    "decorative_personalization": _neg_decorative_personalization(),
    "recommendation_without_evidence": _neg_recommendation_without_evidence(),
    "missing_day_closure": _neg_missing_day_closure(),
    "wellness_closure": _neg_wellness_closure(),
    "locale_mismatch_en_cyrillic": _neg_locale_mismatch_en_cyrillic(),
    "locale_mismatch_ru_latin": _neg_locale_mismatch_ru_latin(),
    "no_birth_time_deep_natal": _neg_no_birth_time_deep_natal(),
}


# ---------------------------------------------------------------------------
# Mutations (worsen a good native along one axis)
# ---------------------------------------------------------------------------


def _mut_drop_force_b(native: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(native)
    out["conflict"]["force_b"] = ""
    return out


def _mut_universal_advice_example(native: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(native)
    out["scenes"][0]["recommended_action"] = "Don't rush and stay in the moment."
    out["scenes"][0]["opportunity"] = "Listen to yourself."
    out["scenes"][0]["trap"] = "Trust the process without a concrete step."
    out["scenes"][0]["avoid_action"] = "Avoid conflict and find balance."
    out["scenes"][0]["everyday_example"] = "Find balance and be mindful today."
    out["scenes"][0]["setup"] = "Take a pause and trust the process."
    return out


def _mut_drop_link_to_conflict(native: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(native)
    for voice in ("astrology", "day_card", "day_number"):
        node = out["interpretive_chorus"].get(voice)
        rows = node if isinstance(node, list) else [node] if isinstance(node, dict) else []
        for row in rows:
            if isinstance(row, dict):
                row["link_to_conflict"] = ""
                row.pop("conflict_id", None)
    return out


def _mut_clone_scene_into_second(native: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(native)
    clone = dict(out["scenes"][0])
    clone["scene_id"] = "scene.communication"
    clone["sphere"] = "communication"
    out["scenes"][1] = clone
    return out


def _mut_soft_generic_action(native: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(native)
    out["scenes"][0]["recommended_action"] = "Будьте осторожны и сохраняйте баланс."
    return out


def _mut_drop_evidence_refs(native: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(native)
    for s in out["scenes"]:
        s.pop("evidence_refs", None)
        s.pop("chorus_refs", None)
        if "personalization" in s:
            s["personalization"].pop("personalization_evidence_refs", None)
    return out


def _mut_drop_day_closure(native: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(native)
    out.pop("day_closure", None)
    out.pop("closure", None)
    return out


def _mut_mush_closure(native: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(native)
    out["day_closure"] = {
        "resolution": "Trust the universe — you are enough.",
        "remaining_tension": "Everything happens for a reason.",
        "evening_state": "The universe has your back.",
        "conflict_callback": "Доверьтесь вселенной.",
    }
    return out


_MUTATIONS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "drop_force_b": _mut_drop_force_b,
    "universal_advice_example": _mut_universal_advice_example,
    "drop_link_to_conflict": _mut_drop_link_to_conflict,
    "clone_scene_into_second": _mut_clone_scene_into_second,
    "soft_generic_action": _mut_soft_generic_action,
    "drop_evidence_refs": _mut_drop_evidence_refs,
    "drop_day_closure": _mut_drop_day_closure,
    "mush_closure": _mut_mush_closure,
}


def apply_mutation(native: dict[str, Any], mutation_id: str) -> dict[str, Any]:
    fn = _MUTATIONS.get(mutation_id)
    if fn is None:
        raise KeyError(f"unknown mutation_id: {mutation_id!r}")
    return fn(deepcopy(native))


MUTATION_IDS: tuple[str, ...] = tuple(_MUTATIONS.keys())
