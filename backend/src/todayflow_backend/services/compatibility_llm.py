"""LLM-слой для совместимости: живая формулировка поверх детерминированных сигналов.

Принцип: числа и подскоры остаются из шаблона (sign_compatibility_product), текст —
переписывается моделью по промптам с антипаттерном и JSON-выходом.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import date
from time import perf_counter
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.core.config import settings
from todayflow_backend.core.llm_openai_compatible import (
    chat_completion_text,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
    resolve_max_tokens,
)
from todayflow_backend.data.astrology import sign_for_date
from todayflow_backend.services.learning import get_learning_service
from todayflow_backend.services.generation_orchestrator import build_compatibility_orchestration_meta
from todayflow_backend.services.sign_compatibility_product import (
    SignCompatibilityProductSurface,
    SignCompatAnalysisBlock,
    SignCompatRoles,
    SignCompatScenarioGroup,
    normalize_relationship_context,
)
from todayflow_backend.services.compatibility_funnel_artifact import CompatibilityLLMBaseModelFields
from todayflow_backend.services.compatibility_scenario_tone import (
    ScenarioToneSpec,
    augment_system_prompt_with_scenario,
)
from todayflow_backend.core.content_openness_policy import (
    LLM_ANTI_ESOTERIC_EN,
    LLM_ANTI_ESOTERIC_RU,
    LLM_SAFETY_BOUNDARY_EN,
    LLM_SAFETY_BOUNDARY_RU,
    LLM_USER_VOICE_EN,
    LLM_USER_VOICE_RU,
    strip_meta_editorial_phrases,
)
from todayflow_backend.i18n import translate

logger = logging.getLogger(__name__)

_BANNED_SUBSTRINGS_RU = (
    "энерги",
    "вибрац",
    "вселенн",
    "космичес",
    "мистич",
)
_BANNED_SUBSTRINGS_EN = (
    "energy",
    "vibrat",
    "univer",
    "cosmic",
    "mystic",
)


def context_label(ctx: str, *, locale: str) -> str:
    n = normalize_relationship_context(ctx)
    return translate(f"compat.context.{n}", locale=locale)


def context_label_ru(ctx: str) -> str:
    return context_label(ctx, locale="ru")


_HASHTAG_LINE = re.compile(r"^#[A-Za-z][A-Za-z0-9_]*$")
_HASHTAG_TOKEN = re.compile(r"(?:^|\s)(#[A-Za-z][A-Za-z0-9_]*)(?=\s|$)")


def _strip_hashtag_garbage(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    kept = [ln for ln in lines if not _HASHTAG_LINE.match(ln)]
    out = "\n".join(kept) if kept else text
    out = _HASHTAG_TOKEN.sub(" ", out)
    return re.sub(r"\s+", " ", out).strip()


def sanitize_compatibility_copy(text: str, *, locale: str = "ru") -> str:
    if not text or not text.strip():
        return text
    loc = locale.strip().split("-")[0].lower()
    banned = _BANNED_SUBSTRINGS_RU if loc == "ru" else _BANNED_SUBSTRINGS_EN
    repl = "динамика" if loc == "ru" else "dynamic"
    lower = text.lower()
    out = text
    for ban in banned:
        if ban in lower:
            out = re.sub(re.escape(ban) + r"\w*", repl, out, flags=re.IGNORECASE)
            lower = out.lower()
    out = _strip_hashtag_garbage(out)
    out = re.sub(r"\s+", " ", out).strip()
    return strip_meta_editorial_phrases(out)


def _sanitize_obj(obj: Any, *, locale: str) -> Any:
    if isinstance(obj, str):
        return sanitize_compatibility_copy(obj, locale=locale)
    if isinstance(obj, list):
        return [_sanitize_obj(x, locale=locale) for x in obj]
    if isinstance(obj, dict):
        return {k: _sanitize_obj(v, locale=locale) for k, v in obj.items()}
    return obj


def build_pair_dynamics(
    *,
    user1_label: str,
    user2_label: str,
    from_modality: str,
    to_modality: str,
    from_element: str,
    to_element: str,
    locale: str = "ru",
) -> dict[str, Any]:
    fm = (from_modality or "").lower()
    tm = (to_modality or "").lower()
    fe = (from_element or "").lower()
    te = (to_element or "").lower()
    loc = locale.strip().split("-")[0].lower()
    if loc not in ("en", "ru"):
        loc = "en"

    def tendency(mod: str) -> str:
        if mod == "cardinal":
            return translate("compat.dynamics.tendency.cardinal", locale=loc)
        if mod == "fixed":
            return translate("compat.dynamics.tendency.fixed", locale=loc)
        if mod == "mutable":
            return translate("compat.dynamics.tendency.mutable", locale=loc)
        return translate("compat.dynamics.tendency.default", locale=loc)

    leader_guess = "mixed"
    withdrawer_guess = "mixed"
    if fm == "cardinal" and tm in {"fixed", "mutable"}:
        leader_guess, withdrawer_guess = "user_1", "user_2"
    elif tm == "cardinal" and fm in {"fixed", "mutable"}:
        leader_guess, withdrawer_guess = "user_2", "user_1"
    elif fm == "fixed" and tm == "mutable":
        leader_guess, withdrawer_guess = "user_1", "user_2"
    elif tm == "fixed" and fm == "mutable":
        leader_guess, withdrawer_guess = "user_2", "user_1"

    return {
        "user_1_label": user1_label,
        "user_2_label": user2_label,
        "leader_guess": leader_guess,
        "withdrawer_guess": withdrawer_guess,
        "user_1_contact_style": tendency(fm),
        "user_2_contact_style": tendency(tm),
        "element_pair": f"{fe or '?'}_{te or '?'}",
        "emotional_contrast": (
            translate("compat.dynamics.emotional.diff", locale=loc)
            if fe != te
            else translate("compat.dynamics.emotional.same", locale=loc)
        ),
    }


def build_signals(*, subscores: dict[str, int], score: int) -> dict[str, Any]:
    return {
        "attraction_score": subscores.get("attraction", score),
        "stability_index": subscores.get("stability", score),
        "conflict_repair_score": subscores.get("conflicts", score),
        "sexual_dynamic_score": subscores.get("sexuality", score),
        "overall_score": score,
    }


SYSTEM_PROMPT = f"""Ты пишешь разбор совместимости для живого продукта TodayFlow — как умный навигатор отношений.

{LLM_SAFETY_BOUNDARY_RU}

{LLM_ANTI_ESOTERIC_RU}

{LLM_USER_VOICE_RU}

СТРОГО ЗАПРЕЩЕНО в тексте: ИИ, AI, LLM, «генерация», «модель», «промпт», «алгоритм», «хаб».

ЦЕПОЧКА СМЫСЛА (держи слои, не усредняй):
1) притяжение — почему тянет;
2) различие — где стили сталкиваются;
3) конфликт — что повторяется;
4) действие — что делать / чего не делать / как (конкретно, с глаголом).

НУЖНО:
— конкретное поведение, реакции, циклы («кто давит», «кто отходит», «что повторяется»)
— пиши так, чтобы хотелось дочитать: тепло, прямо, без канцелярита и без гороскопных штампов
— блок sexuality — полноценный раздел про секс в паре: желание, инициатива, темп, тело, согласие; называй секс сексом
— для key=sexuality добавь tips — 3–5 практических подсказок
— русский язык, «ты» к user_1
— если есть structured_base_model — не противоречь ему
— scenarios.closer = как сближаться; scenarios.boundary или exit = где тормозить

Ответ СТРОГО один JSON-объект без markdown, со структурой:
{{
  "score_tagline": "string — одна строка-статус про динамику пары",
  "overview_paragraphs": ["2–3 абзаца: притяжение → различие → конфликт/напряжение"],
  "blocks": [
    {{
      "key": "emotions",
      "title": "string",
      "subtitle": "string",
      "takeaway": "1–2 строки",
      "detail": "разбор",
      "risk": "чего не делать",
      "action": "что делать",
      "tips": ["только для sexuality: 3–5 практических подсказок"]
    }},
    ... ровно такие key по порядку: emotions, communication, conflicts, sexuality, long_term
  ],
  "roles": {{
    "you_bullets": ["3 коротких пункта про user_1"],
    "partner_bullets": ["3 коротких пункта про user_2"]
  }},
  "scenarios": [
    {{"id": "closer", "title": "string", "bullets": ["2–3 действия — как делать"]}},
    {{"id": "clarity", "title": "string", "bullets": ["2–3 действия"]}},
    {{"id": "exit", "title": "string", "bullets": ["2–3 действия"]}}
  ]
}}

Не повторяй дословно входные поля element_relation и rhythm_relation — переводи в поведение."""

SYSTEM_PROMPT_EN = f"""You write pair-compatibility readings for a living product — a sharp relationship navigator.

{LLM_SAFETY_BOUNDARY_EN}

{LLM_ANTI_ESOTERIC_EN}

{LLM_USER_VOICE_EN}

STRICTLY FORBIDDEN in copy: AI, LLM, «generation», «model», «prompt», «algorithm», «hub».

MEANING CHAIN (keep layers, don't flatten):
1) attraction — why they pull;
2) difference — where styles collide;
3) conflict — what repeats;
4) action — what to do / what not to / how (concrete verbs).

REQUIRE:
— concrete behavior, reactions, cycles («who pushes», «who withdraws», «what repeats»)
— write so people finish reading: warm, direct, no corporate mush, no horoscope clichés
— sexuality block: a full section on sex in the pair — desire, arousal, initiative, pace, bodies, consent; call sex sex
— for key=sexuality include tips — 3–5 practical bullets
— English; address user_1 as «you» (second person)
— if the input contains structured_base_model, align overview/blocks/roles with it; do not contradict it
— scenarios.closer = how to get closer; scenarios.boundary or exit = where to brake

Return STRICTLY one JSON object, no markdown, shaped like:
{{
  "score_tagline": "string — one status line about the pair dynamic",
  "overview_paragraphs": ["2–3 paragraphs: pull → difference → conflict/tension"],
  "blocks": [
    {{
      "key": "emotions",
      "title": "string",
      "subtitle": "string",
      "takeaway": "1–2 lines",
      "detail": "analysis",
      "risk": "risk",
      "action": "what to do",
      "tips": ["sexuality only: 3–5 practical tips"]
    }},
    ... exactly these keys in order: emotions, communication, conflicts, sexuality, long_term
  ],
  "roles": {{
    "you_bullets": ["3 short bullets about user_1"],
    "partner_bullets": ["3 short bullets about user_2"]
  }},
  "scenarios": [
    {{"id": "closer", "title": "string", "bullets": ["2–3 actions"]}},
    {{"id": "clarity", "title": "string", "bullets": ["2–3 actions"]}},
    {{"id": "exit", "title": "string", "bullets": ["2–3 actions"]}}
  ]
}}

Do not repeat element_relation and rhythm_relation verbatim — turn them into behavior."""

BASE_MODEL_SYSTEM_PROMPT_RU = """Ты строишь ПЕРВЫЙ внутренний слой совместимости пары (не финальный текст для пользователя — сухо и по делу).

Запреты формулировок: энергия, вибрации, вселенная, космос, мистика.

Нужно различать: здоровое притяжение vs зависимость/проекция; конфликт как цикл; секс как отдельный мотор (инициатива, контроль, закрытие).

Если переданы today_do / today_avoid — твои выводы не должны им противоречить (это дневной ритм пользователя).

Ответ СТРОГО один JSON:
{
  "pull_vs_tension": "1–3 предложения: что тянет и где основное напряжение",
  "attraction_or_dependency": "1–3 предложения: притяжение vs риск зависимости/проверок",
  "conflict_cycle": "1–3 предложения: как заводится и разворачивается конфликт",
  "sexual_dynamic": "1–3 предложения: желание, инициатива, темп и контроль в сексе у пары",
  "aligned_actions_hint": "1–2 предложения: какие действия сейчас совместимы с today_do/today_avoid если они есть"
}"""

BASE_MODEL_SYSTEM_PROMPT_EN = """You build the FIRST internal compatibility layer (not final user-facing copy — concise).

Banned wording: energy, vibration, universe, cosmos, mysticism.

Separate: healthy pull vs dependency/projection; conflict as a cycle; sex as its own engine (initiation, control, shutdown).

If today_do / today_avoid are provided, do not contradict them.

Return STRICTLY one JSON object:
{
  "pull_vs_tension": "1–3 sentences",
  "attraction_or_dependency": "1–3 sentences",
  "conflict_cycle": "1–3 sentences",
  "sexual_dynamic": "1–3 sentences: desire, initiative, pace, and control in the pair's sex life",
  "aligned_actions_hint": "1–2 sentences aligned with today_do/today_avoid when present"
}"""


def base_model_system_prompt_for_locale(locale: str) -> str:
    loc = locale.strip().split("-")[0].lower()
    return BASE_MODEL_SYSTEM_PROMPT_EN if loc == "en" else BASE_MODEL_SYSTEM_PROMPT_RU


def generate_llm_base_model(
    *,
    pair_display: str,
    user1_label: str,
    user2_label: str,
    relationship_context: str,
    pair_dynamics: dict[str, Any],
    signals: dict[str, Any],
    element_relation: str,
    rhythm_relation: str,
    today_do: str | None,
    today_avoid: str | None,
    today_focus: str | None,
    locale: str = "ru",
    scenario_tone: ScenarioToneSpec | None = None,
    scenario_context: dict[str, Any] | None = None,
    compatibility_learning: dict[str, Any] | None = None,
) -> CompatibilityLLMBaseModelFields | None:
    """Цепочка: Base Model (JSON) до основного LLM-текста поверхности."""
    if not is_llm_chat_configured():
        return None
    client = get_openai_compatible_client()
    if client is None:
        return None
    loc = locale.strip().split("-")[0].lower()
    if loc not in ("en", "ru"):
        loc = "en"
    sys_prompt = augment_system_prompt_with_scenario(
        base_model_system_prompt_for_locale(loc), scenario_tone, locale=loc
    )
    payload: dict[str, Any] = {
        "pair_display": pair_display,
        "user_1": user1_label,
        "user_2": user2_label,
        "relationship_stage": normalize_relationship_context(relationship_context),
        "context_label": context_label(relationship_context, locale=loc),
        "pair_dynamics": pair_dynamics,
        "signals": signals,
        "element_relation_hint": element_relation,
        "rhythm_relation_hint": rhythm_relation,
        "today_do": (today_do or "").strip()[:800],
        "today_avoid": (today_avoid or "").strip()[:800],
        "today_focus": (today_focus or "").strip()[:400],
        "content_locale": loc,
    }
    if scenario_context:
        payload["scenario"] = scenario_context
    if compatibility_learning:
        payload["compatibility_learning"] = compatibility_learning
    user_prompt = json.dumps(payload, ensure_ascii=False)
    model_id = resolve_default_chat_model()
    try:
        raw = chat_completion_text(
            client,
            model=model_id,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.35,
            max_tokens=resolve_max_tokens(900),
            json_object=True,
        )
        parsed = _parse_llm_json(raw or "")
        if not isinstance(parsed, dict):
            return None
        parsed = _sanitize_obj(parsed, locale=loc)
        return CompatibilityLLMBaseModelFields(
            pull_vs_tension=sanitize_compatibility_copy(str(parsed.get("pull_vs_tension") or ""), locale=loc)[:520],
            attraction_or_dependency=sanitize_compatibility_copy(
                str(parsed.get("attraction_or_dependency") or ""), locale=loc
            )[:520],
            conflict_cycle=sanitize_compatibility_copy(str(parsed.get("conflict_cycle") or ""), locale=loc)[:520],
            sexual_dynamic=sanitize_compatibility_copy(str(parsed.get("sexual_dynamic") or ""), locale=loc)[:520],
            aligned_actions_hint=sanitize_compatibility_copy(
                str(parsed.get("aligned_actions_hint") or ""), locale=loc
            )[:400],
        )
    except Exception as exc:
        logger.warning("compatibility base model LLM failed: %s", exc, exc_info=True)
        return None



def system_prompt_for_locale(locale: str) -> str:
    loc = locale.strip().split("-")[0].lower()
    return SYSTEM_PROMPT_EN if loc == "en" else SYSTEM_PROMPT


def _parse_llm_json(raw: str) -> dict[str, Any] | None:
    text = (raw or "").strip()
    if not text:
        return None
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if fence:
        text = fence.group(1).strip()
    elif text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def _tips_from_llm(raw: Any, template: list[str], *, locale: str) -> list[str]:
    if not isinstance(raw, list):
        return list(template)
    cleaned = [
        sanitize_compatibility_copy(str(x), locale=locale)
        for x in raw
        if str(x).strip()
    ]
    cleaned = [t for t in cleaned if len(t.split()) >= 4][:5]
    return cleaned if len(cleaned) >= 2 else list(template)


def _blocks_from_llm(
    raw_blocks: Any, template_blocks: list[SignCompatAnalysisBlock], *, locale: str
) -> list[SignCompatAnalysisBlock]:
    by_key = {b.key: b for b in template_blocks}
    if not isinstance(raw_blocks, list):
        return template_blocks
    out: list[SignCompatAnalysisBlock] = []
    for key in ("emotions", "communication", "conflicts", "sexuality", "long_term"):
        tpl = by_key.get(key)
        if not tpl:
            continue
        row = next((x for x in raw_blocks if isinstance(x, dict) and x.get("key") == key), None)
        if not row:
            out.append(tpl)
            continue
        out.append(
            SignCompatAnalysisBlock(
                key=key,
                title=sanitize_compatibility_copy(str(row.get("title") or tpl.title), locale=locale)[:120],
                subtitle=sanitize_compatibility_copy(str(row.get("subtitle") or tpl.subtitle), locale=locale)[:160],
                takeaway=sanitize_compatibility_copy(str(row.get("takeaway") or tpl.takeaway), locale=locale),
                detail=sanitize_compatibility_copy(str(row.get("detail") or tpl.detail), locale=locale),
                risk=sanitize_compatibility_copy(str(row.get("risk") or tpl.risk), locale=locale),
                action=sanitize_compatibility_copy(str(row.get("action") or tpl.action), locale=locale),
                tips=_tips_from_llm(row.get("tips"), tpl.tips, locale=locale),
            )
        )
    return out if len(out) == 5 else template_blocks


def _roles_from_llm(raw: Any, template: SignCompatRoles, *, locale: str) -> SignCompatRoles:
    if not isinstance(raw, dict):
        return template
    yb = raw.get("you_bullets")
    pb = raw.get("partner_bullets")
    if not isinstance(yb, list) or not isinstance(pb, list):
        return template
    y_clean = [sanitize_compatibility_copy(str(x), locale=locale) for x in yb[:5] if str(x).strip()]
    p_clean = [sanitize_compatibility_copy(str(x), locale=locale) for x in pb[:5] if str(x).strip()]
    if len(y_clean) < 2 or len(p_clean) < 2:
        return template
    return SignCompatRoles(you_bullets=y_clean[:3], partner_bullets=p_clean[:3])


def _scenarios_from_llm(raw: Any, template: list[SignCompatScenarioGroup], *, locale: str) -> list[SignCompatScenarioGroup]:
    if not isinstance(raw, list):
        return template
    out: list[SignCompatScenarioGroup] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        sid = str(item.get("id") or "")
        title = sanitize_compatibility_copy(str(item.get("title") or ""), locale=locale)
        bullets_raw = item.get("bullets")
        if sid not in {"closer", "clarity", "exit"} or not title:
            continue
        bl = bullets_raw if isinstance(bullets_raw, list) else []
        bullets = [sanitize_compatibility_copy(str(b), locale=locale) for b in bl if str(b).strip()][:5]
        if len(bullets) < 2:
            continue
        out.append(SignCompatScenarioGroup(id=sid, title=title, bullets=bullets[:3]))
    if len(out) < 3:
        return template
    out.sort(key=lambda x: {"closer": 0, "clarity": 1, "exit": 2}.get(x.id, 9))
    return out


def generate_llm_product_surface(
    db: Session | None,
    *,
    template_surface: SignCompatibilityProductSurface,
    pair_display: str,
    user1_label: str,
    user2_label: str,
    relationship_context: str,
    pair_dynamics: dict[str, Any],
    signals: dict[str, Any],
    element_relation: str,
    rhythm_relation: str,
    block_feedback: dict[str, str] | None,
    user_id: int | None,
    locale: str = "ru",
    base_model_layer: dict[str, Any] | None = None,
    scenario_tone: ScenarioToneSpec | None = None,
    scenario_context: dict[str, Any] | None = None,
    compatibility_learning: dict[str, Any] | None = None,
) -> tuple[SignCompatibilityProductSurface, str, dict[str, Any] | None]:
    """Возвращает (surface, source, raw_llm_or_none). source — llm | template."""

    if not is_llm_chat_configured():
        return template_surface, "template", None
    client = get_openai_compatible_client()
    if client is None:
        return template_surface, "template", None

    loc = locale.strip().split("-")[0].lower()
    if loc not in ("en", "ru"):
        loc = "en"
    sys_prompt = augment_system_prompt_with_scenario(system_prompt_for_locale(loc), scenario_tone, locale=loc)

    fb_lines: list[str] = []
    if block_feedback:
        for k, v in block_feedback.items():
            if v in {"yes", "partial", "no"}:
                fb_lines.append(translate("compat.llm.feedback", locale=loc).format(block=k, val=v))

    payload: dict[str, Any] = {
        "pair_display": pair_display,
        "user_1": user1_label,
        "user_2": user2_label,
        "relationship_stage": normalize_relationship_context(relationship_context),
        "context_label": context_label(relationship_context, locale=loc),
        "pair_dynamics": pair_dynamics,
        "signals": signals,
        "element_relation_hint": element_relation,
        "rhythm_relation_hint": rhythm_relation,
        "feedback_on_blocks": fb_lines,
        "content_locale": loc,
    }
    if scenario_context:
        payload["scenario"] = scenario_context
    if base_model_layer:
        payload["structured_base_model"] = base_model_layer
    if compatibility_learning:
        payload["compatibility_learning"] = compatibility_learning
    user_prompt = json.dumps(payload, ensure_ascii=False)

    is_playful = scenario_tone is not None and scenario_tone.tone_mode == "playful"
    max_tokens = 1200 if is_playful else 2800

    started = perf_counter()
    raw_response = ""
    model_id = resolve_default_chat_model()
    orchestration_meta = build_compatibility_orchestration_meta(
        relationship_context=relationship_context,
        signals=signals,
        pair_dynamics=pair_dynamics,
        scenario_tone=scenario_tone,
    )
    try:
        raw_response = chat_completion_text(
            client,
            model=model_id,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.55,
            max_tokens=resolve_max_tokens(max_tokens),
            json_object=True,
        ) or ""
        parsed = _parse_llm_json(raw_response)
        if not parsed:
            raise ValueError("empty_llm_json")

        parsed = _sanitize_obj(parsed, locale=loc)
        tagline = sanitize_compatibility_copy(
            str(parsed.get("score_tagline") or template_surface.score_tagline), locale=loc
        )
        overview = parsed.get("overview_paragraphs")
        ov_list: list[str] = []
        if isinstance(overview, list):
            ov_list = [
                sanitize_compatibility_copy(str(x), locale=loc) for x in overview if str(x).strip()
            ][:1 if is_playful else 4]
        if is_playful:
            if not ov_list:
                ov_list = [tagline] if tagline else list(template_surface.overview_paragraphs)[:1]
        elif len(ov_list) < 2:
            ov_list = list(template_surface.overview_paragraphs)

        blocks = _blocks_from_llm(parsed.get("blocks"), list(template_surface.blocks), locale=loc)
        roles = _roles_from_llm(parsed.get("roles"), template_surface.roles, locale=loc)
        if is_playful:
            scenarios: list = []
        else:
            scenarios = _scenarios_from_llm(parsed.get("scenarios"), list(template_surface.scenarios), locale=loc)

        surface = SignCompatibilityProductSurface(
            score_tagline=tagline[:220],
            subscores=template_surface.subscores,
            overview_paragraphs=ov_list,
            blocks=blocks,
            roles=roles,
            scenarios=scenarios,
        )

        duration_ms = int((perf_counter() - started) * 1000)
        compat_quality = {
            "contract_version": "semantic_quality_v0",
            "surface": "compatibility_dynamics",
            "passed": bool(surface.score_tagline.strip()) and len(surface.overview_paragraphs) >= 1,
            "checks": {
                "tagline_present": bool(surface.score_tagline.strip()),
                "overview_present": len(surface.overview_paragraphs) >= 1,
            },
        }
        if db is not None:
            try:
                get_learning_service().log_generation(
                    db,
                    module="compatibility",
                    surface="dynamics_llm",
                    user_id=user_id,
                    model=model_id,
                    locale=loc,
                    input_payload={
                        "relationship_context": normalize_relationship_context(relationship_context),
                        "format_id": scenario_tone.format_id if scenario_tone else None,
                        "tone_mode": scenario_tone.tone_mode if scenario_tone else None,
                        "orchestration": {
                            **orchestration_meta,
                            "semantic_quality": compat_quality,
                            "generation_outcome": {"source": "llm", "used_fallback": False},
                        },
                    },
                    system_prompt=sys_prompt[:2000],
                    user_prompt=user_prompt[:8000],
                    raw_response=raw_response[:12000],
                    normalized_response={"score_tagline": surface.score_tagline},
                    status="success",
                    used_fallback=False,
                    duration_ms=duration_ms,
                )
            except Exception as log_exc:
                logger.warning("compatibility llm log failed: %s", log_exc)

        return surface, "llm", parsed
    except Exception as exc:
        if str(exc) == "empty_llm_json":
            logger.info(
                "compatibility LLM returned empty JSON (model=%s); using template fallback",
                model_id,
            )
        else:
            logger.warning("compatibility LLM generation failed: %s", exc, exc_info=True)
        duration_ms = int((perf_counter() - started) * 1000)
        if db is not None:
            try:
                get_learning_service().log_generation(
                    db,
                    module="compatibility",
                    surface="dynamics_llm",
                    user_id=user_id,
                    model=model_id,
                    locale=loc,
                    input_payload={
                        "relationship_context": normalize_relationship_context(relationship_context),
                        "format_id": scenario_tone.format_id if scenario_tone else None,
                        "tone_mode": scenario_tone.tone_mode if scenario_tone else None,
                        "orchestration": {
                            **orchestration_meta,
                            "generation_outcome": {"source": "template", "used_fallback": True},
                        },
                    },
                    system_prompt=sys_prompt[:2000],
                    user_prompt=user_prompt[:8000],
                    raw_response=raw_response[:12000] if raw_response else None,
                    normalized_response=None,
                    status="error",
                    used_fallback=True,
                    error_message=str(exc)[:500],
                    duration_ms=duration_ms,
                )
            except Exception:
                pass
        return template_surface, "template", None


def resolve_sign_meta_for_date(d: date | None) -> dict[str, Any] | None:
    if d is None:
        return None
    return sign_for_date(d)
