"""Deterministic life_spheres projector v0.1 (love · money · decisions).

SoT: docs/audits/PROFILE_LIFE_SPHERES_DETERMINISTIC_PROJECTOR_V0.md
Independent of patterns. No LLM.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

PROJECTION_VERSION = "life_spheres_projector_v0.1"
SLICE_SPHERE_IDS = ("love", "money", "decisions")
SPHERE_FIELDS = ("how", "need", "risk", "turns_on", "turns_off", "helps")

_FIELD_MIN = {
    "how": 40,
    "need": 24,
    "risk": 24,
    "turns_on": 20,
    "turns_off": 20,
    "helps": 20,
}
_FIELD_MAX = {
    "how": 520,
    "need": 280,
    "risk": 280,
    "turns_on": 220,
    "turns_off": 220,
    "helps": 220,
}

_HOUSE_MARKERS = ("в доме", " доме", "асцендент", "ascendant", " house ", "в 7", "в 2", "в 8", "в 9")
_LONGITUDINAL_MARKERS = ("регулярно", "каждый раз", "по чек-инам", "as your days show", "every time")

_GENERIC_RU = (
    "энергия вселенной",
    "дождитесь знака",
    "просто доверьтесь",
    "гармония во всём",
)

# Keyword → class for style lenses (v0.1).
_STYLE_BUCKETS: dict[str, tuple[str, ...]] = {
    "clarity": ("ясн", "прям", "честн", "говор", "clarity", "honest", "direct"),
    "pace": ("темп", "медлен", "быстр", "ритм", "pace", "slow", "fast"),
    "care": ("забот", "тепл", "поддерж", "care", "warm", "support"),
    "autonomy": ("автоном", "пространств", "границ", "сам", "autonomy", "space", "boundar"),
    "depth": ("глубин", "смысл", "близк", "depth", "intim"),
    "structure": ("структур", "порядок", "правил", "учёт", "structure", "order", "rule"),
    "growth": ("рост", "шаг", "развит", "growth", "grow"),
    "security": ("безопас", "устойчив", "стабил", "security", "stable"),
    "exchange": ("обмен", "ценност", "value", "exchange"),
    "speed": ("быстр", "сразу", "speed", "quick"),
    "consensus": ("соглас", "вместе", "consensus", "align"),
    "analysis": ("анализ", "критер", "взвес", "analysis", "criteria"),
}


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _clip(text: str, n: int) -> str:
    t = (text or "").strip()
    if len(t) <= n:
        return t
    return t[: max(0, n - 1)].rstrip() + "…"


def _first_sentence(text: str, max_len: int = 160) -> str:
    t = (text or "").strip()
    if not t:
        return ""
    for sep in (". ", "! ", "? ", ".\n"):
        if sep in t:
            t = t.split(sep, 1)[0].strip()
            if not t.endswith((".", "!", "?")):
                t += "."
            break
    return _clip(t, max_len)


def _style_quote(style: str, max_len: int = 40) -> str:
    t = (style or "").strip()
    if not t:
        return ""
    return _clip(t, max_len)


def _classify_style(style: str, preferred: tuple[str, ...]) -> str:
    n = _norm(style)
    for cls in preferred:
        keys = _STYLE_BUCKETS.get(cls) or ()
        if any(k in n for k in keys):
            return cls
    return "general"


def _token_set(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-zа-яё]{3,}", _norm(text))}


def _jaccard(a: str, b: str) -> float:
    sa, sb = _token_set(a), _token_set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def spheres_projection_allowed(foundations: dict[str, Any] | None) -> bool:
    """Natal-presence gate — independent of patterns_generation_allowed."""
    f = foundations if isinstance(foundations, dict) else {}
    person = f.get("person") if isinstance(f.get("person"), dict) else {}
    natal = f.get("natal") if isinstance(f.get("natal"), dict) else {}
    identity = f.get("identity") if isinstance(f.get("identity"), dict) else {}
    styles = f.get("styles") if isinstance(f.get("styles"), dict) else {}

    birth_date = str(person.get("birth_date") or natal.get("birth_date") or "").strip()
    sun = str(natal.get("sun_sign") or "").strip()
    # sun_sign implies birth foundations were calculated (same honesty as depth_from_profile_pack).
    has_birth_foundation = bool(birth_date or sun)
    if not has_birth_foundation or not sun:
        return False
    if len(str(identity.get("identity_core") or "").strip()) < 20:
        return False
    return any(
        len(str(styles.get(k) or "").strip()) >= 12
        for k in ("relationship_style", "money_style", "decision_style")
    )


def build_sphere_foundations_v0(
    *,
    shared: dict[str, Any],
    identity: dict[str, Any],
    styles: dict[str, Any],
) -> dict[str, Any]:
    """Assemble SphereFoundationsV0 from funnel shared pack + identity/styles steps."""
    person = shared.get("person") if isinstance(shared.get("person"), dict) else {}
    astro = shared.get("astro") if isinstance(shared.get("astro"), dict) else {}
    natal_in = shared.get("natal") if isinstance(shared.get("natal"), dict) else {}
    houses_raw = natal_in.get("houses") if isinstance(natal_in.get("houses"), dict) else {}
    houses_available = bool(natal_in.get("houses_available")) and bool(houses_raw)

    sun = str(astro.get("sun_sign") or natal_in.get("sun_sign") or "").strip()
    return {
        "locale": str(shared.get("locale") or "ru"),
        "person": {
            "birth_date": person.get("birth_date") or astro.get("birth_date"),
            "birth_time": person.get("birth_time") or astro.get("birth_time"),
            "time_unknown": person.get("time_unknown") if "time_unknown" in person else astro.get("time_unknown"),
        },
        "identity": {
            "identity_core": str(identity.get("identity_core") or "").strip(),
            "strengths": identity.get("strengths") if isinstance(identity.get("strengths"), list) else [],
            "growth_zones": identity.get("growth_zones") if isinstance(identity.get("growth_zones"), list) else [],
        },
        "styles": {
            "relationship_style": str(styles.get("relationship_style") or "").strip(),
            "money_style": str(styles.get("money_style") or "").strip(),
            "decision_style": str(styles.get("decision_style") or "").strip(),
        },
        "natal": {
            "sun_sign": sun,
            "moon_sign": natal_in.get("moon_sign") or astro.get("moon_sign"),
            "mercury_sign": natal_in.get("mercury_sign") or astro.get("mercury_sign"),
            "venus_sign": natal_in.get("venus_sign") or astro.get("venus_sign"),
            "mars_sign": natal_in.get("mars_sign") or astro.get("mars_sign"),
            "jupiter_sign": natal_in.get("jupiter_sign") or astro.get("jupiter_sign"),
            "saturn_sign": natal_in.get("saturn_sign") or astro.get("saturn_sign"),
            "houses_available": houses_available,
            "houses": houses_raw if houses_available else {},
            "planet_bullets": natal_in.get("planet_bullets")
            if isinstance(natal_in.get("planet_bullets"), dict)
            else {},
            "birth_date": person.get("birth_date") or astro.get("birth_date"),
        },
        "baseline": shared.get("baseline") if isinstance(shared.get("baseline"), dict) else {},
        "numerology": shared.get("numerology") if isinstance(shared.get("numerology"), dict) else {},
    }


def _planet_line(natal: dict[str, Any], *planets: str, locale: str) -> tuple[str, str | None]:
    bullets = natal.get("planet_bullets") if isinstance(natal.get("planet_bullets"), dict) else {}
    en = locale.lower().startswith("en")
    labels = {
        "sun": ("Солнце", "Sun"),
        "moon": ("Луна", "Moon"),
        "venus": ("Венера", "Venus"),
        "mars": ("Марс", "Mars"),
        "mercury": ("Меркурий", "Mercury"),
        "jupiter": ("Юпитер", "Jupiter"),
        "saturn": ("Сатурн", "Saturn"),
    }
    for p in planets:
        key = f"{p}_sign"
        sign = str(natal.get(key) or "").strip()
        bl = bullets.get(p)
        if isinstance(bl, list) and bl and str(bl[0]).strip():
            return _clip(str(bl[0]).strip(), 180), p
        if sign:
            label = labels.get(p, (p, p))[1 if en else 0]
            if en:
                return _clip(f"{label} in {sign} colors how this area shows up.", 180), p
            return _clip(f"{label} в знаке {sign} задаёт тон проявления в этой сфере.", 180), p
    sun = str(natal.get("sun_sign") or "").strip()
    if sun:
        if en:
            return _clip(f"Sun in {sun} sets a base tone for how this area shows.", 180), "sun"
        return _clip(f"Солнце в знаке {sun} задаёт базовый тон проявления в этой сфере.", 180), "sun"
    return "", None


def _house_line(natal: dict[str, Any], n: int) -> str | None:
    if not natal.get("houses_available"):
        return None
    houses = natal.get("houses") if isinstance(natal.get("houses"), dict) else {}
    row = houses.get(str(n))
    if not isinstance(row, dict):
        return None
    desc = str(row.get("description") or "").strip()
    theme = str(row.get("theme") or "").strip()
    text = desc or theme
    return _clip(text, 200) if text else None


def _join(*parts: str | None) -> str:
    return " ".join(p.strip() for p in parts if p and str(p).strip()).strip()


def _templates_love(cls: str, style: str, *, en: bool) -> dict[str, str]:
    q = _style_quote(style)
    if en:
        base = {
            "clarity": {
                "need": f"In love you need clear words and predictable contact — as in «{q}».",
                "risk": "The break point is guessing instead of naming what you want.",
                "turns_on": "Calm direct talk and matching pace of closeness.",
                "turns_off": "Hints, mixed signals, and pressure without a next step.",
                "helps": "One short honest agreement this week — not a full relationship audit.",
            },
            "pace": {
                "need": f"In love you need a pace that fits you — as in «{q}».",
                "risk": "Rushing intimacy or freezing when the tempo is wrong.",
                "turns_on": "A rhythm you can feel without performing.",
                "turns_off": "Sudden demands and chaotic availability.",
                "helps": "Name one tempo boundary before the next deep talk.",
            },
            "autonomy": {
                "need": f"In love you need room for yourself inside closeness — as in «{q}».",
                "risk": "Merging until resentment, or pulling away without words.",
                "turns_on": "Respect for space paired with steady contact.",
                "turns_off": "Control, checks, and no private air.",
                "helps": "Keep one personal slot sacred while staying in contact.",
            },
            "general": {
                "need": f"In love you need contact that matches «{q}».",
                "risk": "Losing yourself in the other person's tempo.",
                "turns_on": "Warm clarity and a shared next step.",
                "turns_off": "Vague pressure and unpaid emotional labor.",
                "helps": "One concrete closeness step — not a promise to fix everything.",
            },
        }
    else:
        base = {
            "clarity": {
                "need": f"В любви нужна ясность и предсказуемый контакт — в духе «{q}».",
                "risk": "Точка слома — ожидание, что другой угадает без слов.",
                "turns_on": "Спокойный прямой разговор и совпадение по темпу близости.",
                "turns_off": "Намёки, двойные сигналы и давление без следующего шага.",
                "helps": "Одна короткая честная договорённость на неделю — не разбор «всего сразу».",
            },
            "pace": {
                "need": f"В любви нужен свой темп — в духе «{q}».",
                "risk": "Слишком быстрый заход в близость или замирание при чужом ритме.",
                "turns_on": "Ритм, в котором можно быть без спектакля.",
                "turns_off": "Резкие требования и хаотичная доступность.",
                "helps": "Назови одну границу темпа до следующего глубокого разговора.",
            },
            "autonomy": {
                "need": f"В любви нужно пространство для себя внутри близости — в духе «{q}».",
                "risk": "Слияние до раздражения или уход без слов.",
                "turns_on": "Уважение к личному воздуху при устойчивом контакте.",
                "turns_off": "Контроль, проверки и отсутствие своей зоны.",
                "helps": "Оставь один личный слот неприкосновенным, оставаясь на связи.",
            },
            "care": {
                "need": f"В любви нужна тёплая опора без растворения — в духе «{q}».",
                "risk": "Забота ценой своих границ.",
                "turns_on": "Взаимная поддержка и мягкая устойчивость.",
                "turns_off": "Обесценивание чувств и холодная отстранённость.",
                "helps": "Один жест заботы о себе и один — о контакте, в один день.",
            },
            "depth": {
                "need": f"В любви нужна глубина смысла, а не только интенсивность — в духе «{q}».",
                "risk": "Путать драму с близостью.",
                "turns_on": "Честный разговор о важном без спешки.",
                "turns_off": "Поверхностность и игра в недосказанность.",
                "helps": "Выбери одну тему для глубины и закрой её одним шагом.",
            },
            "general": {
                "need": f"В любви нужен контакт, который совпадает с «{q}».",
                "risk": "Потерять себя в чужом темпе.",
                "turns_on": "Тёплая ясность и общий следующий шаг.",
                "turns_off": "Размытое давление и неоплаченный эмоциональный труд.",
                "helps": "Один конкретный шаг близости — не обещание «исправить всё».",
            },
        }
    return base.get(cls) or base["general"]


def _templates_money(cls: str, style: str, *, en: bool) -> dict[str, str]:
    q = _style_quote(style)
    if en:
        base = {
            "structure": {
                "need": f"With money you need simple rules of value — as in «{q}».",
                "risk": "Chaos in tracking or tightening control until it freezes action.",
                "turns_on": "Clear numbers and small regular steps.",
                "turns_off": "Shame about asks and foggy mutual settlements.",
                "helps": "One money focus this week and a note of what worked.",
            },
            "security": {
                "need": f"With money you need a sense of safety under the resource — as in «{q}».",
                "risk": "Anxiety spending or refusing any movement.",
                "turns_on": "A visible buffer and honest limits.",
                "turns_off": "Comparison and sudden holes in the plan.",
                "helps": "Name one safety number and protect it this week.",
            },
            "growth": {
                "need": f"With money you need a growth step without impulse — as in «{q}».",
                "risk": "Stretching too far or stalling with no next move.",
                "turns_on": "A small measurable expansion.",
                "turns_off": "All-or-nothing bets.",
                "helps": "One growth action with a cap — then review.",
            },
            "general": {
                "need": f"With money you need a stance that matches «{q}».",
                "risk": "Impulse or endless self-restriction.",
                "turns_on": "Honest accounting without moralizing.",
                "turns_off": "Fog around numbers and borrowed urgency.",
                "helps": "One weekly money check — fifteen minutes, one decision.",
            },
        }
    else:
        base = {
            "structure": {
                "need": f"В деньгах нужны простые правила ценности — в духе «{q}».",
                "risk": "Хаос в учёте или зажим контроля до остановки действий.",
                "turns_on": "Понятные цифры и маленькие регулярные шаги.",
                "turns_off": "Стыд за запросы и туман во взаиморасчётах.",
                "helps": "Один денежный фокус на неделю и запись «что сработало».",
            },
            "security": {
                "need": f"В деньгах нужно ощущение безопасности под ресурсом — в духе «{q}».",
                "risk": "Траты от тревоги или отказ от любого движения.",
                "turns_on": "Видимый запас и честные пределы.",
                "turns_off": "Сравнение с другими и внезапные дыры в плане.",
                "helps": "Назови одну цифру безопасности и держи её неделю.",
            },
            "growth": {
                "need": f"В деньгах нужен шаг роста без импульса — в духе «{q}».",
                "risk": "Перерастяжение или полный застой без следующего хода.",
                "turns_on": "Малое измеримое расширение.",
                "turns_off": "Ставки «всё или ничего».",
                "helps": "Одно действие роста с потолком — затем разбор.",
            },
            "exchange": {
                "need": f"В деньгах нужен честный обмен ценности — в духе «{q}».",
                "risk": "Отдавать больше, чем готовы, или обесценивать свой вклад.",
                "turns_on": "Прозрачные договорённости о цене и вкладе.",
                "turns_off": "Размытые «потом рассчитаемся».",
                "helps": "Одна ясная договорённость о цене до следующего обмена.",
            },
            "general": {
                "need": f"В деньгах нужна позиция, совпадающая с «{q}».",
                "risk": "Импульс или бесконечное самоограничение.",
                "turns_on": "Честный учёт без морализаторства.",
                "turns_off": "Туман в цифрах и чужая срочность.",
                "helps": "Одна денежная сверка в неделю — пятнадцать минут, одно решение.",
            },
        }
    return base.get(cls) or base["general"]


def _templates_decisions(cls: str, style: str, *, en: bool) -> dict[str, str]:
    q = _style_quote(style)
    if en:
        base = {
            "structure": {
                "need": f"In decisions you need a clear frame — as in «{q}».",
                "risk": "Endless options without a close.",
                "turns_on": "One criterion and a short deadline.",
                "turns_off": "Open tabs of unmade choices.",
                "helps": "Write three criteria, pick one move, timebox it.",
            },
            "analysis": {
                "need": f"In decisions you need enough analysis without freeze — as in «{q}».",
                "risk": "Overthinking past the useful window.",
                "turns_on": "A short evidence pass then a call.",
                "turns_off": "More data with no decision slot.",
                "helps": "Cap research at one sitting; decide at the end.",
            },
            "speed": {
                "need": f"In decisions you need a fast honest call — as in «{q}».",
                "risk": "Speed without a revisit point.",
                "turns_on": "A clear yes/no with a check-back date.",
                "turns_off": "Forced urgency from outside.",
                "helps": "Decide once; schedule one review, not ten.",
            },
            "general": {
                "need": f"In decisions you need a method that matches «{q}».",
                "risk": "Drifting without a next concrete step.",
                "turns_on": "A single next action after the call.",
                "turns_off": "Committees of one that never close.",
                "helps": "One decision hygiene: criteria → choose → calendar the first step.",
            },
        }
    else:
        base = {
            "structure": {
                "need": f"В решениях нужна ясная рамка — в духе «{q}».",
                "risk": "Бесконечные варианты без закрытия.",
                "turns_on": "Один критерий и короткий дедлайн.",
                "turns_off": "Открытые вкладки непринятых выборов.",
                "helps": "Запиши три критерия, выбери ход, поставь таймбокс.",
            },
            "analysis": {
                "need": f"В решениях нужен достаточный разбор без зависания — в духе «{q}».",
                "risk": "Переанализ мимо полезного окна.",
                "turns_on": "Короткая проверка фактов и затем выбор.",
                "turns_off": "Новые данные без слота на решение.",
                "helps": "Ограничь исследование одним заходом; в конце — решение.",
            },
            "speed": {
                "need": f"В решениях нужен быстрый честный выбор — в духе «{q}».",
                "risk": "Скорость без точки пересмотра.",
                "turns_on": "Ясное да/нет с датой проверки.",
                "turns_off": "Чужая навязанная срочность.",
                "helps": "Реши один раз; поставь один пересмотр, не десять.",
            },
            "consensus": {
                "need": f"В решениях нужно согласование без растворения — в духе «{q}».",
                "risk": "Ждать всех и потерять свой критерий.",
                "turns_on": "Короткий круг мнений и свой финальный ход.",
                "turns_off": "Бесконечные совещания без владельца решения.",
                "helps": "Собери два мнения, назови своё решение и следующий шаг.",
            },
            "general": {
                "need": f"В решениях нужен способ, совпадающий с «{q}».",
                "risk": "Дрейф без конкретного следующего шага.",
                "turns_on": "Одно действие сразу после выбора.",
                "turns_off": "Комитеты из одного человека, которые не закрываются.",
                "helps": "Гигиена решения: критерии → выбор → в календарь первый шаг.",
            },
        }
    return base.get(cls) or base["general"]


def validate_projected_row(
    row: dict[str, str],
    *,
    style: str,
    identity_core: str,
    houses_available: bool,
    locale: str = "ru",
) -> str | None:
    """Return omit_reason or None if row is acceptable."""
    for field, mn in _FIELD_MIN.items():
        if len(str(row.get(field) or "").strip()) < mn:
            return f"field_short:{field}"
    if _norm(row.get("how") or "") == _norm(style):
        return "style_passthrough"
    if identity_core:
        how_n, id_n = _norm(row.get("how") or ""), _norm(identity_core)
        if how_n and id_n and (id_n in how_n or how_n in id_n or _jaccard(row.get("how") or "", identity_core) >= 0.5):
            return "identity_echo"
    blob = _norm(" ".join(str(row.get(f) or "") for f in SPHERE_FIELDS))
    if not houses_available and any(m in blob for m in _HOUSE_MARKERS):
        return "house_overclaim"
    if any(m in blob for m in _LONGITUDINAL_MARKERS):
        return "longitudinal_leak"
    if not locale.lower().startswith("en") and any(g in blob for g in _GENERIC_RU):
        return "generic_phrase"
    return None


def _build_sphere(
    sid: str,
    *,
    foundations: dict[str, Any],
) -> tuple[dict[str, str] | None, dict[str, Any]]:
    locale = str(foundations.get("locale") or "ru")
    en = locale.lower().startswith("en")
    natal = foundations.get("natal") if isinstance(foundations.get("natal"), dict) else {}
    styles = foundations.get("styles") if isinstance(foundations.get("styles"), dict) else {}
    identity_core = str((foundations.get("identity") or {}).get("identity_core") or "")
    evidence: list[str] = []
    claim_depth = "sign_plus_styles" if natal.get("houses_available") else "sign_only"
    style = ""

    if sid == "love":
        style = str(styles.get("relationship_style") or "").strip()
        if len(style) < 12:
            return None, {"omit_reason": "style_missing", "evidence": []}
        evidence.append("style:relationship_style")
        planet, planet_id = _planet_line(natal, "venus", "sun", locale=locale)
        if not planet:
            return None, {"omit_reason": "planet_missing", "evidence": evidence}
        if planet_id:
            evidence.append(f"planet:{planet_id}")
            evidence.append("rule:love.how.planet")
        house = _house_line(natal, 7)
        if house:
            evidence.append("house:7")
            evidence.append("rule:love.how.house7")
            claim_depth = "houses_plus_styles"
        lead = "В любви" if not en else "In love"
        how = _join(
            f"{lead}: {planet}",
            (f"В партнёрском поле: {house}" if not en else f"In the partnership field: {house}") if house else None,
        )
        cls = _classify_style(style, ("clarity", "pace", "autonomy", "care", "depth"))
        t = _templates_love(cls, style, en=en)
        evidence.extend(
            [
                "rule:love.need.from_style",
                "rule:love.risk.from_style",
                "rule:love.on.from_style",
                "rule:love.off.from_style",
                "rule:love.helps.from_style",
            ]
        )
    elif sid == "money":
        style = str(styles.get("money_style") or "").strip()
        if len(style) < 12:
            return None, {"omit_reason": "style_missing", "evidence": []}
        evidence.append("style:money_style")
        planet, planet_id = _planet_line(natal, "jupiter", "saturn", "sun", locale=locale)
        if not planet:
            return None, {"omit_reason": "planet_missing", "evidence": evidence}
        if planet_id:
            evidence.append(f"planet:{planet_id}")
            evidence.append("rule:money.how.planet")
        h2 = _house_line(natal, 2)
        h8 = _house_line(natal, 8)
        house_bits = []
        if h2:
            evidence.append("house:2")
            evidence.append("rule:money.how.house2")
            house_bits.append(h2)
        if h8:
            evidence.append("house:8")
            evidence.append("rule:money.how.house8")
            house_bits.append(h8)
        if house_bits:
            claim_depth = "houses_plus_styles"
        lead = "В деньгах" if not en else "With money"
        how = _join(f"{lead}: {planet}", " ".join(house_bits) if house_bits else None)
        cls = _classify_style(style, ("structure", "security", "growth", "exchange"))
        t = _templates_money(cls, style, en=en)
        evidence.extend(
            [
                "rule:money.need.from_style",
                "rule:money.risk.from_style",
                "rule:money.on.from_style",
                "rule:money.off.from_style",
                "rule:money.helps.from_style",
            ]
        )
    elif sid == "decisions":
        style = str(styles.get("decision_style") or "").strip()
        if len(style) < 12:
            return None, {"omit_reason": "style_missing", "evidence": []}
        evidence.append("style:decision_style")
        planet, planet_id = _planet_line(natal, "saturn", "mercury", "sun", locale=locale)
        if not planet:
            return None, {"omit_reason": "planet_missing", "evidence": evidence}
        if planet_id:
            evidence.append(f"planet:{planet_id}")
            evidence.append("rule:decisions.how.planet")
        house = _house_line(natal, 9)
        if house:
            evidence.append("house:9")
            evidence.append("rule:decisions.how.house9")
            claim_depth = "houses_plus_styles"
        lead = "В решениях" if not en else "In decisions"
        how = _join(
            f"{lead}: {planet}",
            (f"В поле выбора: {house}" if not en else f"In the choice field: {house}") if house else None,
        )
        cls = _classify_style(style, ("structure", "analysis", "speed", "consensus"))
        t = _templates_decisions(cls, style, en=en)
        evidence.extend(
            [
                "rule:decisions.need.from_style",
                "rule:decisions.risk.from_style",
                "rule:decisions.on.from_style",
                "rule:decisions.off.from_style",
                "rule:decisions.helps.from_style",
            ]
        )
    else:
        return None, {"omit_reason": "not_in_slice_v0_1", "evidence": []}

    row = {
        "how": _clip(how, _FIELD_MAX["how"]),
        "need": _clip(t["need"], _FIELD_MAX["need"]),
        "risk": _clip(t["risk"], _FIELD_MAX["risk"]),
        "turns_on": _clip(t["turns_on"], _FIELD_MAX["turns_on"]),
        "turns_off": _clip(t["turns_off"], _FIELD_MAX["turns_off"]),
        "helps": _clip(t["helps"], _FIELD_MAX["helps"]),
    }

    reject = validate_projected_row(
        row,
        style=style,
        identity_core=identity_core,
        houses_available=bool(natal.get("houses_available")),
        locale=locale,
    )
    if reject:
        return None, {"omit_reason": reject, "evidence": evidence}

    return row, {"claim_depth": claim_depth, "evidence": evidence, "style_class": cls}


def _fingerprint(foundations: dict[str, Any], life_spheres: dict[str, Any], meta_per: dict[str, Any]) -> str:
    styles = foundations.get("styles") if isinstance(foundations.get("styles"), dict) else {}
    natal = foundations.get("natal") if isinstance(foundations.get("natal"), dict) else {}
    identity_core = str((foundations.get("identity") or {}).get("identity_core") or "")
    used_styles = {
        k: hashlib.sha256(_norm(str(styles.get(k) or "")).encode("utf-8")).hexdigest()[:16]
        for k in ("relationship_style", "money_style", "decision_style")
        if str(styles.get(k) or "").strip()
    }
    rule_ids: list[str] = []
    for sid, info in meta_per.items():
        for e in info.get("evidence") or []:
            if str(e).startswith("rule:"):
                rule_ids.append(str(e))
    houses_used: dict[str, str] = {}
    for sid, info in meta_per.items():
        for e in info.get("evidence") or []:
            if str(e).startswith("house:"):
                n = str(e).split(":", 1)[1]
                row = (natal.get("houses") or {}).get(n) if isinstance(natal.get("houses"), dict) else None
                if isinstance(row, dict):
                    txt = str(row.get("description") or row.get("theme") or "")
                    houses_used[n] = hashlib.sha256(_norm(txt).encode("utf-8")).hexdigest()[:16]

    payload = {
        "projection_version": PROJECTION_VERSION,
        "locale": foundations.get("locale") or "ru",
        "sphere_ids": sorted(life_spheres.keys()),
        "inputs": {
            "identity_core_hash": hashlib.sha256(_norm(identity_core).encode("utf-8")).hexdigest()[:16],
            "styles": used_styles,
            "natal": {
                "sun_sign": natal.get("sun_sign"),
                "houses_available": bool(natal.get("houses_available")),
                "houses_used": houses_used,
            },
            "rule_ids": sorted(set(rule_ids)),
        },
        "life_spheres": life_spheres,
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def project_life_spheres_v0(foundations: dict[str, Any]) -> tuple[dict[str, dict[str, str]], dict[str, Any]]:
    """Project PR-2 slice. Returns (life_spheres, meta)."""
    omitted: list[dict[str, str]] = []
    for sid in (
        "sex",
        "work",
        "family",
        "kids",
        "body",
        "friends",
    ):
        omitted.append({"id": sid, "reason": "not_in_slice_v0_1"})

    if not spheres_projection_allowed(foundations):
        return {}, {
            "projection_version": PROJECTION_VERSION,
            "fingerprint": None,
            "spheres_projected": [],
            "spheres_omitted": omitted
            + [{"id": sid, "reason": "gate_closed"} for sid in SLICE_SPHERE_IDS],
            "per_sphere": {},
            "spheres_source": "deterministic_projector_v0_1",
        }

    life_spheres: dict[str, dict[str, str]] = {}
    per_sphere: dict[str, Any] = {}
    hows: list[str] = []
    needs: list[str] = []

    styles = foundations.get("styles") if isinstance(foundations.get("styles"), dict) else {}
    identity_core = str((foundations.get("identity") or {}).get("identity_core") or "")
    natal = foundations.get("natal") if isinstance(foundations.get("natal"), dict) else {}
    locale = str(foundations.get("locale") or "ru")
    style_by_sid = {
        "love": str(styles.get("relationship_style") or ""),
        "money": str(styles.get("money_style") or ""),
        "decisions": str(styles.get("decision_style") or ""),
    }

    for sid in SLICE_SPHERE_IDS:
        row, info = _build_sphere(sid, foundations=foundations)
        if row is None:
            omitted.append({"id": sid, "reason": str(info.get("omit_reason") or "rejected")})
            continue
        # Re-validate (covers patched builders in tests + defense in depth).
        reject = validate_projected_row(
            row,
            style=style_by_sid.get(sid) or "",
            identity_core=identity_core,
            houses_available=bool(natal.get("houses_available")),
            locale=locale,
        )
        if reject:
            omitted.append({"id": sid, "reason": reject})
            continue
        # distinctness vs prior hows
        how_n = _norm(row["how"])
        need_n = _norm(row["need"])
        distinct_fail = False
        for prev in hows:
            if how_n == prev or (len(how_n) > 40 and (how_n in prev or prev in how_n)):
                distinct_fail = True
                break
        if not distinct_fail:
            for prev_need in needs:
                if need_n and need_n == prev_need:
                    distinct_fail = True
                    break
        if distinct_fail:
            omitted.append({"id": sid, "reason": "spheres_not_distinct"})
            continue
        life_spheres[sid] = row
        hows.append(how_n)
        needs.append(need_n)
        per_sphere[sid] = {
            "claim_depth": info.get("claim_depth"),
            "evidence": info.get("evidence") or [],
            "style_class": info.get("style_class"),
        }

    meta = {
        "projection_version": PROJECTION_VERSION,
        "fingerprint": _fingerprint(foundations, life_spheres, per_sphere) if life_spheres else None,
        "spheres_projected": sorted(life_spheres.keys()),
        "spheres_omitted": omitted,
        "per_sphere": per_sphere,
        "spheres_source": "deterministic_projector_v0_1",
    }
    return life_spheres, meta
