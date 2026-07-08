"""Playful compatibility surface contract — short stat-card copy, not love-therapy essays."""

from __future__ import annotations

import re

from todayflow_backend.services.compatibility_scenario_tone import ScenarioToneSpec, _loc, _t
from todayflow_backend.services.sign_compatibility_product import (
    SignCompatAnalysisBlock,
    SignCompatibilityProductSurface,
)

_IRONY_PREFIXES = (
    "с лёгкой иронией:",
    "with a light wink:",
)


def _strip_irony_prefix(text: str) -> str:
    t = (text or "").strip()
    low = t.lower()
    for p in _IRONY_PREFIXES:
        if low.startswith(p):
            return t[len(p) :].strip()
    return t


def _band(score: int) -> str:
    if score >= 72:
        return "high"
    if score >= 52:
        return "mid"
    return "low"


def _playful_verdict_ru(format_id: str, score: int) -> str:
    labels = {
        "partner_in_crime": {
            "high": "Вероятность совместного безумия — высокая. Кто-то потом всё равно всё исправит.",
            "mid": "Авантюра возможна, но один из вас точно спросит «а мы точно это обсуждали?»",
            "low": "Как напарники в приключении — скорее очередь в МФЦ, чем ограбление банка.",
        },
        "after_wine": {
            "high": "После бокала вы опасны — в хорошем и смешном смысле.",
            "mid": "Вечер будет с историями. Желательно — с приятными.",
            "low": "Даже вино не гарантирует, что будет интересно.",
        },
        "home_renovation": {
            "high": "Ремонт вас не разведёт — редкий результат.",
            "mid": "Кто-то сдастся на этапе выбора плитки. Ставки приняты.",
            "low": "Статистика говорит: лучше нанять прораба и не спорить.",
        },
        "best_friends": {
            "high": "Дружба без романтики — и это ваш суперсиловой режим.",
            "mid": "Besties с подколами — ваш формат.",
            "low": "Скорее приятельский чат, чем «лучшие друзья».",
        },
        "rule_breaker": {
            "high": "Кто нарушит правила первым — вопрос времени, не принципа.",
            "mid": "«Мы так решили» продержится до среды. Максимум.",
            "low": "Вы слишком законопослушны для этого детективного сценария.",
        },
        "living_together": {
            "high": "Быт вас не разрушит — уже победа.",
            "mid": "Соседи по квартире с потенциалом.",
            "low": "Холодильник может стать полем битвы.",
        },
        "vacation": {
            "high": "В пути вы — dream team. Почти без срывов.",
            "mid": "Отпуск выживете — с мемами и одним спорным маршрутом.",
            "low": "Лучше ехать отдельно и встречаться у моря.",
        },
    }
    table = labels.get(format_id) or {
        "high": "Шуточная статистика на вашей стороне.",
        "mid": "50 на 50 — как в хорошей шутке.",
        "low": "Цифры просят другой сценарий.",
    }
    return table[_band(score)]


def _playful_verdict_en(format_id: str, score: int) -> str:
    labels = {
        "partner_in_crime": {
            "high": "Joint chaos probability: high. Someone will still fix the mess.",
            "mid": "Adventure possible — one of you will ask «are we sure?»",
            "low": "More DMV queue than heist crew.",
        },
        "after_wine": {
            "high": "After a glass you're dangerous — in a fun way.",
            "mid": "The evening will have stories. Hopefully good ones.",
            "low": "Even wine can't guarantee it'll be interesting.",
        },
    }
    table = labels.get(format_id) or {
        "high": "Stats lean your way — don't take it to court.",
        "mid": "Fifty-fifty — like a decent joke.",
        "low": "Numbers suggest picking another scenario.",
    }
    return table[_band(score)]


def _playful_block_takeaway(format_id: str, block_key: str, score: int, locale: str) -> str:
    loc = _loc(locale)
    key_map = {
        "emotions": "attraction",
        "communication": "stability",
        "conflicts": "conflicts",
        "sexuality": "sexuality",
        "long_term": "stability",
    }
    dim = key_map.get(block_key, block_key)
    b = _band(score)

    quips_ru: dict[str, dict[str, dict[str, str]]] = {
        "partner_in_crime": {
            "attraction": {"high": "Готовы к безумию без прогрева", "mid": "Риск есть, но кто-то спросит «точно?»", "low": "Скучнее очереди"},
            "stability": {"high": "План «Б» найдётся в 3 ночи", "mid": "Один тащит, второй помогает «морально»", "low": "«Это был не я» — ваш саундтрек"},
            "conflicts": {"high": "Спор, кто первым полез в огонь", "mid": "Чья идея была хуже — вечная тема", "low": "Даже спорить ленитесь"},
            "sexuality": {"high": "Адреналин + химия", "mid": "Искра не всегда вовремя", "low": "Больше напарники"},
        },
        "after_wine": {
            "attraction": {"high": "Флирт после второго бокала — в эфире", "mid": "Флирт через «ну ладно, один»", "low": "Awkward silence побеждает"},
            "stability": {"high": "Уют почти без сюрпризов", "mid": "Один домой, другой — ещё бокал", "low": "«Завтра всё объясню»"},
            "conflicts": {"high": "Правда быстрее закуски", "mid": "Лишнее сказали — утром отрицаете", "low": "Фильтры держатся"},
            "sexuality": {"high": "Искра раньше выключения света", "mid": "Намёки есть", "low": "Сериал важнее"},
        },
    }
    table = quips_ru.get(format_id, {}).get(dim, {})
    if table.get(b):
        return table[b]
    if loc == "en":
        return f"Stat check: {dim} — {b} band."
    return f"Показатель «{dim}» — зона {b}."


def _clamp_takeaway(text: str, *, max_len: int = 96) -> str:
    t = re.sub(r"\s+", " ", (text or "").strip())
    if len(t) <= max_len:
        return t
    return t[: max_len - 1].rstrip() + "…"


def apply_playful_surface_contract(
    surface: SignCompatibilityProductSurface,
    spec: ScenarioToneSpec,
    *,
    locale: str | None,
) -> SignCompatibilityProductSurface:
    """Trim product surface to playful stat-card contract (mutates in place)."""
    if spec.tone_mode != "playful":
        return surface

    loc = _loc(locale)
    sub = surface.subscores
    score = int((sub.attraction + sub.stability + sub.conflicts + sub.sexuality) / 4)

    tagline = _strip_irony_prefix(surface.score_tagline or "")
    if len(tagline) > 140:
        tagline = tagline[:139].rstrip() + "…"
    if not tagline or len(tagline) < 12:
        tagline = _t(
            _playful_verdict_ru(spec.format_id, score),
            _playful_verdict_en(spec.format_id, score),
            loc,
        )
    surface.score_tagline = tagline

    verdict = _t(
        _playful_verdict_ru(spec.format_id, score),
        _playful_verdict_en(spec.format_id, score),
        loc,
    )
    overview_line = tagline if len(tagline) <= 200 else verdict
    surface.overview_paragraphs = [overview_line]

    block_scores = {
        "emotions": sub.attraction,
        "communication": sub.stability,
        "conflicts": sub.conflicts,
        "sexuality": sub.sexuality,
        "long_term": sub.stability,
    }
    trimmed_blocks: list[SignCompatAnalysisBlock] = []
    for block in surface.blocks or []:
        sc = block_scores.get(block.key, score)
        quip = _playful_block_takeaway(spec.format_id, block.key, sc, loc)
        if block.takeaway and len(block.takeaway) <= 96 and block.takeaway != block.detail:
            quip = _clamp_takeaway(block.takeaway)
        trimmed_blocks.append(
            SignCompatAnalysisBlock(
                key=block.key,
                title=block.title,
                subtitle=block.subtitle,
                takeaway=_clamp_takeaway(quip),
                detail="",
                risk="",
                action="",
                tips=list(block.tips) if block.key == "sexuality" and block.tips else [],
            )
        )
    surface.blocks = trimmed_blocks
    surface.scenarios = []
    return surface


def playful_system_prompt_append(spec: ScenarioToneSpec, *, locale: str | None) -> str:
    loc = _loc(locale)
    title = _t(spec.title_ru, spec.title_en, loc)
    if loc == "en":
        return (
            f"\n\n--- PLAYFUL FORMAT (mandatory for {spec.format_id}) ---\n"
            f"Scenario: {title}. This is NOT a serious love analysis.\n"
            f"Return SHORT humorous stat-card copy themed to this scenario.\n"
            f"— score_tagline: one witty verdict about THIS scenario (max 140 chars). No therapy tone.\n"
            f"— overview_paragraphs: EXACTLY 1 item, max 2 sentences, playful insight tied to scenario.\n"
            f"— blocks: takeaway only (max 90 chars each, scenario-themed one-liner). detail, risk, action = empty strings.\n"
            f"— roles: max 1 bullet each, playful role labels in this scenario.\n"
            f"— scenarios: empty array []\n"
        )
    return (
        f"\n\n--- PLAYFUL FORMAT (обязательно для {spec.format_id}) ---\n"
        f"Сценарий: {title}. Это НЕ серьёзный любовный разбор.\n"
        f"Нужен КОРОТКИЙ шуточный stat-card текст строго по теме сценария.\n"
        f"— score_tagline: один остроумный вердикт по ЭТОМУ сценарию (max 140 символов). Без терапевтического тона.\n"
        f"— overview_paragraphs: РОВНО 1 абзац, max 2 предложения, шутливый insight по теме.\n"
        f"— blocks: только takeaway (max 90 символов, stat-строка по сценарию). detail, risk, action = пустые строки.\n"
        f"— roles: max 1 пункт в each, игровые роли в этом сценарии.\n"
        f"— scenarios: пустой массив []\n"
    )
