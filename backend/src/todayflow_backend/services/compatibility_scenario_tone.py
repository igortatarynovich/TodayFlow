"""Scenario format registry — tone, voice, and LLM directives per compatibility exploration."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

ToneFamily = Literal["romantic", "dramatic", "playful", "office", "domestic", "calm", "vacation"]
ToneMode = Literal["serious", "playful"]


class ScenarioToneSpec(BaseModel):
    format_id: str
    tone_family: ToneFamily
    tone_mode: ToneMode
    title_ru: str
    title_en: str
    focus_ru: str
    focus_en: str
    voice_directive_ru: str
    voice_directive_en: str


def _loc(locale: str | None) -> str:
    base = (locale or "ru").strip().split("-")[0].lower()
    return "ru" if base == "ru" else "en"


def _t(ru: str, en: str, locale: str) -> str:
    return ru if locale == "ru" else en


def _spec(
    format_id: str,
    tone_family: ToneFamily,
    tone_mode: ToneMode,
    title_ru: str,
    title_en: str,
    focus_ru: str,
    focus_en: str,
    voice_ru: str,
    voice_en: str,
) -> ScenarioToneSpec:
    return ScenarioToneSpec(
        format_id=format_id,
        tone_family=tone_family,
        tone_mode=tone_mode,
        title_ru=title_ru,
        title_en=title_en,
        focus_ru=focus_ru,
        focus_en=focus_en,
        voice_directive_ru=voice_ru,
        voice_directive_en=voice_en,
    )


SCENARIO_TONE_REGISTRY: dict[str, ScenarioToneSpec] = {
    "love": _spec(
        "love",
        "romantic",
        "serious",
        "Любовь",
        "Love",
        "Эмоциональная близость, притяжение, романтика.",
        "Emotional closeness, attraction, romance.",
        "Тон: тёплый, романтичный, эмпатичный. Конкретные сцены пары, не абстракции.",
        "Tone: warm, romantic, empathetic. Concrete pair scenes, not abstractions.",
    ),
    "living_together": _spec(
        "living_together",
        "domestic",
        "playful",
        "Living Together",
        "Living Together",
        "Быт, границы, йогурт, термostat, посуда.",
        "Domestic life, boundaries, routines, shared home.",
        "Тон: бытовой, ироничный, узнаваемый. Можно лёгкий юмор про мелочи. Без морализаторства.",
        "Tone: domestic, ironic, relatable. Light humor on small things OK. No moralizing.",
    ),
    "office": _spec(
        "office",
        "office",
        "serious",
        "Office Compatibility",
        "Office Compatibility",
        "Рабочие роли, дедлайны, Reply All, встречи.",
        "Work roles, deadlines, meetings, professional friction.",
        "Тон: деловой, с офисным юмором где уместно. Конкретика про роли и темп, не HR-канцелярит.",
        "Tone: professional, office humor where fit. Roles and pace, not HR boilerplate.",
    ),
    "sex": _spec(
        "sex",
        "romantic",
        "serious",
        "Sexual Dynamics",
        "Sexual Dynamics",
        "Желание, инициатива, телесность, напряжение.",
        "Desire, initiative, body, tension.",
        "Тон: взрослый, прямой, телесный. Пиши про секс, желание, инициативу, ритм, границы и согласие — конкретные сцены и реакции. В tips — практика: позы/ритм под пару, фразы для старта или паузы, что делать при отказе или разном желании.",
        "Tone: adult, direct, embodied. Write about sex, desire, initiative, rhythm, boundaries, and consent — concrete behavior and scenes. In tips — practical guidance: positions/rhythm for the pair, phrases to start or pause, what to do if declined or libidos differ.",
    ),
    "apocalypse": _spec(
        "apocalypse",
        "dramatic",
        "serious",
        "Apocalypse",
        "Apocalypse",
        "Кризис, стресс, ответственность под давлением.",
        "Crisis, stress, responsibility under pressure.",
        "Тон: драматичный, собранный. Не фатализм и не «конец света» — реальные кризисы жизни.",
        "Tone: dramatic, grounded. Not doomsday — real-life crises.",
    ),
    "vacation": _spec(
        "vacation",
        "vacation",
        "playful",
        "Vacation Together",
        "Vacation Together",
        "Отдых, чемоданы, опоздания, маршрут.",
        "Travel, packing, lateness, itinerary.",
        "Тон: лёгкий, яркий, с юмором про поездки. Живые детали, не гид по странам.",
        "Tone: light, vivid, travel humor OK. Live details, not a travel guide.",
    ),
    "money_together": _spec(
        "money_together",
        "calm",
        "serious",
        "Money Together",
        "Money Together",
        "Бюджет, траты, риск, безопасность.",
        "Budget, spending, risk, safety.",
        "Тон: спокойный, прямой. Про деньги как про чувства безопасности, без осуждения.",
        "Tone: calm, direct. Money as safety feelings, no judgment.",
    ),
    "parenting": _spec(
        "parenting",
        "calm",
        "serious",
        "Parenting",
        "Parenting",
        "Дети, границы, усталость, единый фронт.",
        "Children, boundaries, fatigue, united front.",
        "Тон: поддерживающий, реалистичный. Без идеальных родителей.",
        "Tone: supportive, realistic. No perfect-parent fantasy.",
    ),
    "conflict_style": _spec(
        "conflict_style",
        "calm",
        "serious",
        "Conflict Style",
        "Conflict Style",
        "Ссоры, молчание, примирение, повторяющиеся циклы.",
        "Fights, silence, reconciliation, repeating cycles.",
        "Тон: спокойный, про понимание. Без обвинений «кто виноват».",
        "Tone: calm, understanding-focused. No blame games.",
    ),
    "partner_in_crime": _spec(
        "partner_in_crime",
        "playful",
        "playful",
        "Partner in Crime",
        "Partner in Crime",
        "Авантюры, риск, «ну а что если», кто потом исправляет.",
        "Adventures, risk, «what if», who fixes the mess.",
        "Тон: игровой, дерзкий, почти кино-buddy. Юмор и азарт, но выводы полезные.",
        "Tone: playful, bold, buddy-movie energy. Humor and thrill, still useful insights.",
    ),
    "after_wine": _spec(
        "after_wine",
        "playful",
        "playful",
        "После бокала вина",
        "After a Glass of Wine",
        "Что меняется после алкоголя: честность, флирт, споры, смешные решения.",
        "What shifts after drinks: honesty, flirt, fights, silly decisions.",
        "Тон: весёлый, слегка хихикающий, «мы все через это проходили». Без морали про алкоголь.",
        "Tone: fun, slightly giggly, «we've all been there». No alcohol moralizing.",
    ),
    "home_renovation": _spec(
        "home_renovation",
        "domestic",
        "playful",
        "Ремонт квартиры",
        "Apartment Renovation",
        "Ремонт, выбор плитки, сроки, нервы, кто сдаётся первым.",
        "Renovation, tile choices, deadlines, nerves, who gives up first.",
        "Тон: ироничный бытовой хаос. Узнаваемые мелочи ремонта. Можно преувеличивать для смеха.",
        "Tone: ironic domestic chaos. Relatable renovation details. Mild exaggeration for humor OK.",
    ),
    "best_friends": _spec(
        "best_friends",
        "playful",
        "playful",
        "Лучшие друзья",
        "Best Friends",
        "Дружба без романтики: опора, подколы, границы, ревность к другим.",
        "Friendship without romance: support, teasing, boundaries, jealousy.",
        "Тон: лёгкий, тёплый, про дружбу — не сводить всё к «может вы пара». Юмор дружеский.",
        "Tone: light, warm, friendship-first — don't force romance. Friendly humor.",
    ),
    "rule_breaker": _spec(
        "rule_breaker",
        "playful",
        "playful",
        "Кто нарушит правила",
        "Who Breaks the Rules First",
        "Кто первым нарушит договорённость, срок или «мы так решили».",
        "Who breaks the agreement, deadline, or «we decided» first.",
        "Тон: шутливый детектив, «ставки приняты». Игровой, но с реальным insight про дисциплину.",
        "Tone: playful detective, «bets are on». Game-like but real insight on discipline.",
    ),
    "business": _spec(
        "business",
        "office",
        "serious",
        "Business Partners",
        "Business Partners",
        "Бизнес-решения, риск, деньги, ответственность.",
        "Business decisions, risk, money, accountability.",
        "Тон: деловой, про партнёрство. Без стартап-клише.",
        "Tone: businesslike, partnership-focused. No startup clichés.",
    ),
    "love_languages": _spec(
        "love_languages",
        "romantic",
        "serious",
        "Love Languages",
        "Love Languages",
        "Как каждый чувствует «меня выбирают».",
        "How each feels «chosen».",
        "Тон: тёплый, конкретный про жесты, не про тесты из интернета.",
        "Tone: warm, concrete gestures, not internet quiz speak.",
    ),
    "emotional": _spec(
        "emotional",
        "romantic",
        "serious",
        "Emotional Compatibility",
        "Emotional Compatibility",
        "Уязвимость, безопасность, дистанция.",
        "Vulnerability, safety, distance.",
        "Тон: мягкий, бережный. Без психотерапевтического жаргона.",
        "Tone: soft, careful. No therapy jargon.",
    ),
    "work": _spec(
        "work",
        "office",
        "serious",
        "Работа",
        "Work",
        "Роли и темп в совместной работе.",
        "Roles and pace when working together.",
        "Тон: деловой, про совместные задачи.",
        "Tone: professional, shared tasks.",
    ),
    "friendship": _spec(
        "friendship",
        "calm",
        "playful",
        "Дружба",
        "Friendship",
        "Доверие, лёгкость, границы без романтики.",
        "Trust, ease, boundaries without romance.",
        "Тон: лёгкий, про дружбу. Не романтизировать без оснований.",
        "Tone: light, friendship-focused. Don't romanticize without cause.",
    ),
}

DEFAULT_SCENARIO = SCENARIO_TONE_REGISTRY["love"]

_TOPIC_TO_FORMAT: dict[str, str] = {
    "love": "love",
    "living": "living_together",
    "living_together": "living_together",
    "work": "work",
    "sex": "sex",
    "money": "money_together",
    "parenting": "parenting",
    "travel": "vacation",
    "conflicts": "conflict_style",
    "communication": "conflict_style",
    "friendship": "friendship",
    "emotional": "emotional",
    "growth": "love",
}

_READING_TO_FORMAT: dict[str, str] = {
    "reconcile": "conflict_style",
    "passion": "sex",
    "opposites": "love",
}


def resolve_scenario_format(
    *,
    topic_id: str | None = None,
    reading_id: str | None = None,
    series_id: str | None = None,
    format_id: str | None = None,
) -> ScenarioToneSpec:
    if format_id and format_id in SCENARIO_TONE_REGISTRY:
        return SCENARIO_TONE_REGISTRY[format_id]
    if series_id and series_id in SCENARIO_TONE_REGISTRY:
        return SCENARIO_TONE_REGISTRY[series_id]
    if topic_id:
        fid = _TOPIC_TO_FORMAT.get(topic_id) or topic_id
        if fid in SCENARIO_TONE_REGISTRY:
            return SCENARIO_TONE_REGISTRY[fid]
    if reading_id:
        fid = _READING_TO_FORMAT.get(reading_id)
        if fid and fid in SCENARIO_TONE_REGISTRY:
            return SCENARIO_TONE_REGISTRY[fid]
    return DEFAULT_SCENARIO


def scenario_context_for_llm(spec: ScenarioToneSpec, *, locale: str | None) -> dict[str, Any]:
    loc = _loc(locale)
    return {
        "format_id": spec.format_id,
        "tone_family": spec.tone_family,
        "tone_mode": spec.tone_mode,
        "scenario_title": _t(spec.title_ru, spec.title_en, loc),
        "scenario_focus": _t(spec.focus_ru, spec.focus_en, loc),
        "voice_directive": _t(spec.voice_directive_ru, spec.voice_directive_en, loc),
    }


def augment_system_prompt_with_scenario(base_prompt: str, spec: ScenarioToneSpec | None, *, locale: str | None) -> str:
    if spec is None:
        return base_prompt
    loc = _loc(locale)
    block = (
        f"\n\n--- SCENARIO / FORMAT ---\n"
        f"format_id: {spec.format_id}\n"
        f"tone_mode: {spec.tone_mode}\n"
        f"tone_family: {spec.tone_family}\n"
        f"scenario_title: {_t(spec.title_ru, spec.title_en, loc)}\n"
        f"scenario_focus: {_t(spec.focus_ru, spec.focus_en, loc)}\n"
        f"VOICE (mandatory): {_t(spec.voice_directive_ru, spec.voice_directive_en, loc)}\n"
        f"Keep numeric signals unchanged in meaning; rewrite all copy in this scenario voice.\n"
        f"Write substance for the user only — open, direct, useful.\n"
        f"If tone_mode is playful: humor and vivid details OK — still give actionable insight, not jokes only.\n"
    )
    out = base_prompt + block
    if spec.tone_mode == "playful":
        from todayflow_backend.services.compatibility_playful_surface import playful_system_prompt_append

        out += playful_system_prompt_append(spec, locale=loc)
    return out


def apply_scenario_tone_to_template_tagline(tagline: str, spec: ScenarioToneSpec, *, locale: str | None) -> str:
    """Light template-mode hint when LLM is off."""
    loc = _loc(locale)
    if spec.tone_mode != "playful":
        return tagline
    prefix = _t("С лёгкой иронией: ", "With a light wink: ", loc)
    if tagline.lower().startswith(prefix.lower().strip()):
        return tagline
    return f"{prefix}{tagline}"
