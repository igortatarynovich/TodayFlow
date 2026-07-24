"""Rich celestial_events payload for Today morning ritual."""

from __future__ import annotations

from datetime import date
from typing import Any

from todayflow_backend.services import astro
from todayflow_backend.services.aspects import AspectEngine
from todayflow_backend.services.day_sources.timed_lunar_aspects import (
    find_moon_sign_ingress_time,
    find_timed_major_moon_aspects,
)
from todayflow_backend.services.day_sources.void_of_course import build_void_of_course_v0
from todayflow_backend.services.lunar import LunarService
from todayflow_backend.services.retrograde import RetrogradeService

_PLANET_RU: dict[str, str] = {
    "Sun": "Солнце",
    "Moon": "Луна",
    "Mercury": "Меркурий",
    "Venus": "Венера",
    "Mars": "Марс",
    "Jupiter": "Юпитер",
    "Saturn": "Сатурн",
    "Uranus": "Уран",
    "Neptune": "Нептун",
    "Pluto": "Плутон",
    "Chiron": "Хирон",
    "North Node": "Северный узел",
    "South Node": "Южный узел",
}

_ASPECT_RU: dict[str, str] = {
    "conjunction": "соединение",
    "square": "квадрат",
    "trine": "тригон",
    "opposition": "оппозиция",
    "sextile": "секстиль",
}

_RETROGRADE_RU: dict[str, str] = {
    "Mercury": "Меркурий ретрограден — перепроверяй договорённости и не спеши с новыми запусками.",
    "Venus": "Венера ретроградна — ценности и отношения просят честного пересмотра, не быстрых решений.",
    "Mars": "Марс ретрограден — энергия действия идёт внутрь: лучше доработать, чем форсировать.",
    "Jupiter": "Юпитер ретрограден — рост сегодня больше про смысл и веру, чем про внешний размах.",
    "Saturn": "Сатурн ретрограден — границы и обязательства стоит пересмотреть, а не только ужесточать.",
    "Uranus": "Уран ретрограден — перемены начинаются изнутри, прежде чем проявиться снаружи.",
    "Neptune": "Нептун ретрограден — интуиция и творчество просят тишины, а не шума.",
    "Pluto": "Плутон ретрограден — трансформация уходит в глубину, без спешки с внешними рычагами.",
    "Chiron": "Хирон ретрограден — исцеление через понимание старых ран, не через контроль.",
}

_SIGN_RU: dict[str, str] = {
    "Aries": "Овен",
    "Taurus": "Телец",
    "Gemini": "Близнецы",
    "Cancer": "Рак",
    "Leo": "Лев",
    "Virgo": "Дева",
    "Libra": "Весы",
    "Scorpio": "Скорпион",
    "Sagittarius": "Стрелец",
    "Capricorn": "Козерог",
    "Aquarius": "Водолей",
    "Pisces": "Рыбы",
}

_DAILY_SYMBOL_PRESETS: list[dict[str, str]] = [
    {"color": "Лазурь", "stone": "Сапфир", "totem_id": "eagle", "totem_name": "Орёл", "totem_emoji": "🦅",
     "totem_story": "Орёл напоминает смотреть на день с высоты — один приоритет важнее десяти суетных."},
    {"color": "Глубокий синий", "stone": "Лунный камень", "totem_id": "wolf", "totem_name": "Волк", "totem_emoji": "🐺",
     "totem_story": "Волк — про верность своему ритму: стая важна, но путь выбираешь ты."},
    {"color": "Индиго", "stone": "Аметист", "totem_id": "owl", "totem_name": "Сова", "totem_emoji": "🦉",
     "totem_story": "Сова усиливает наблюдение — ответы приходят, когда перестаёшь их выдавливать."},
    {"color": "Изумрудный", "stone": "Малахит", "totem_id": "deer", "totem_name": "Олень", "totem_emoji": "🦌",
     "totem_story": "Олень мягко ведёт через чувствительность — нежность сегодня не слабость."},
    {"color": "Янтарный", "stone": "Цитрин", "totem_id": "bear", "totem_name": "Медведь", "totem_emoji": "🐻",
     "totem_story": "Медведь даёт опору: сначала восстановление, потом действие."},
    {"color": "Коралловый", "stone": "Коралл", "totem_id": "dolphin", "totem_name": "Дельфин", "totem_emoji": "🐬",
     "totem_story": "Дельфин — про лёгкость связи: разговор может снять напряжение быстрее давления."},
    {"color": "Бордовый", "stone": "Гранат", "totem_id": "fox", "totem_name": "Лиса", "totem_emoji": "🦊",
     "totem_story": "Лиса учит гибкости — обойти препятствие иногда мудрее, чем ломать его."},
    {"color": "Перламутровый", "stone": "Жемчуг", "totem_id": "whale", "totem_name": "Кит", "totem_emoji": "🐋",
     "totem_story": "Кит напоминает о глубине: большие смыслы не терпят спешки."},
    {"color": "Оливковый", "stone": "Нефрит", "totem_id": "turtle", "totem_name": "Черепаха", "totem_emoji": "🐢",
     "totem_story": "Черепаха — символ терпения: медленный шаг всё равно двигает вперёд."},
    {"color": "Сливовый", "stone": "Обсидиан", "totem_id": "panther", "totem_name": "Пантера", "totem_emoji": "🐆",
     "totem_story": "Пантера усиливает концентрацию — один точный ход лучше шумной активности."},
    {"color": "Песочный", "stone": "Яшма", "totem_id": "horse", "totem_name": "Конь", "totem_emoji": "🐴",
     "totem_story": "Конь несёт энергию движения — направь её в одну дорогу, не в десять."},
    {"color": "Серебряный", "stone": "Лунный камень", "totem_id": "swan", "totem_name": "Лебедь", "totem_emoji": "🦢",
     "totem_story": "Лебедь — про достоинство в простом: спокойная ясность сильнее демонстрации."},
]

_COLOR_DAY_GUIDE: dict[str, dict[str, str]] = {
    "Лазурь": {
        "benefit_ru": "Успокаивает ум и помогает держать ясность, когда день требует решений.",
        "clothing_ru": "Светлая рубашка, шарф или носки лазурного оттенка.",
        "accessory_ru": "Тонкий браслет, часы с голубым циферблатом или блокнот в мягком синем.",
        "amount_ru": "Достаточно одного акцента — 10–15% образа.",
        "avoid_color_ru": "Кислотно-оранжевый",
        "avoid_why_ru": "Разгоняет темп и мешает спокойному фокусу лазури.",
    },
    "Глубокий синий": {
        "benefit_ru": "Даёт опору и глубину — легче не сорваться на суету.",
        "clothing_ru": "Тёмно-синий свитер, пиджак или джинсы глубокого синего.",
        "accessory_ru": "Сумка, ремень или перстень в спокойном синем.",
        "amount_ru": "Один заметный элемент или два мелких.",
        "avoid_color_ru": "Неоновый жёлтый",
        "avoid_why_ru": "Резкий контраст перегружает день, который просит собранности.",
    },
    "Индиго": {
        "benefit_ru": "Усиливает интуицию — услышать себя до действия.",
        "clothing_ru": "Индиго в нижнем слое: футболка, носки.",
        "accessory_ru": "Платок, шарф или обложка телефона.",
        "amount_ru": "Мягкий акцент ближе к телу — достаточно почувствовать.",
        "avoid_color_ru": "Красный «сигнал тревоги»",
        "avoid_why_ru": "Толкает к реакции раньше, чем успеешь понять, что важно.",
    },
}


def _build_color_symbol(color_name: str) -> dict[str, str]:
    guide = _COLOR_DAY_GUIDE.get(color_name, {})
    return {
        "name": color_name,
        "story_ru": guide.get("benefit_ru") or "Оттенок, который помогает удержать сегодняшний ритм.",
        "benefit_ru": guide.get("benefit_ru") or "Поддерживает спокойный фокус на день.",
        "clothing_ru": guide.get("clothing_ru") or "Один предмет одежды этого оттенка.",
        "accessory_ru": guide.get("accessory_ru") or "Небольшой аксессуар того же тона.",
        "amount_ru": guide.get("amount_ru") or "Достаточно одного акцента — цвет дня не костюм.",
        "avoid_color_ru": guide.get("avoid_color_ru") or "Слишком кричащий неон",
        "avoid_why_ru": guide.get("avoid_why_ru") or "Перегружает день и мешает выбранному ритму.",
    }


_PERSONAL_TRANSIT_STORY: dict[str, str] = {
    "square": "Создаёт напряжение, которое просит осознанного выбора — не автоматической реакции.",
    "opposition": "Подсвечивает полярность: важно найти баланс между двумя полюсами.",
    "conjunction": "Собирает энергию в одну точку — день может казаться более сжатым и точным.",
    "trine": "Даёт естественный поток — легче опираться на то, что уже знаешь о себе.",
    "sextile": "Открывает мягкую возможность — достаточно одного маленького шага.",
}


def _planet_ru(name: str | None) -> str:
    raw = (name or "").strip()
    if not raw:
        return "Планета"
    return _PLANET_RU.get(raw, raw)


def _aspect_ru(aspect: str | None) -> str:
    raw = (aspect or "").strip().lower().replace("_", " ")
    return _ASPECT_RU.get(raw, raw or "аспект")


def _sign_ru(sign: str | None) -> str:
    raw = (sign or "").strip()
    return _SIGN_RU.get(raw, raw)


def _symbol_preset_index(target_date: date, personal_day: int | None) -> int:
    seed = target_date.toordinal() + (personal_day or 0) * 7
    return abs(seed) % len(_DAILY_SYMBOL_PRESETS)


def _format_personal_transit(transit: dict[str, Any]) -> dict[str, Any] | None:
    planet_t = str(transit.get("transiting_planet") or "").strip()
    planet_n = str(transit.get("natal_planet") or "").strip()
    aspect = str(transit.get("aspect") or transit.get("aspect_id") or "").strip().lower()
    if not planet_t or not planet_n or not aspect:
        return None
    strength = str(transit.get("strength") or "").strip()
    title = f"{_planet_ru(planet_t)} — {_aspect_ru(aspect)} — {_planet_ru(planet_n)}"
    story = _PERSONAL_TRANSIT_STORY.get(aspect, "Активирует личную тему из натальной карты.")
    psych = str(transit.get("psychological_description") or "").strip()
    if psych and any("\u0400" <= c <= "\u04FF" for c in psych):
        story = psych[:220]
    elif psych:
        story = f"{story} ({psych[:120]})"
    return {
        "id": f"pt-{planet_t}-{aspect}-{planet_n}".lower(),
        "kind": "personal_transit",
        "transiting_planet": planet_t,
        "natal_planet": planet_n,
        "aspect": aspect,
        "title": title,
        "story_ru": story,
        "strength": strength or None,
    }


def _transit_sort_key(transit: dict[str, Any]) -> tuple[int, float]:
    strength = str(transit.get("strength") or "").lower()
    rank = {"exact": 0, "strong": 1, "medium": 2, "weak": 3}.get(strength, 4)
    tension = str(transit.get("tension_level") or "").lower()
    tension_rank = 0 if tension in {"high", "medium"} else 1
    return (tension_rank, rank)


async def _sky_aspects_for_date(
    target_date: date,
    locale: str,
    astro_service: astro.AstroService,
    aspect_engine: AspectEngine,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Returns (sky_aspects, transit_signs) where transit_signs may include moon_sign/sun_sign."""
    birth_payload = {"date": target_date.isoformat(), "time": "12:00:00", "location": "Equator"}
    transit_signs: dict[str, Any] = {}
    try:
        chart = await astro_service.compute_chart(
            birth_payload=birth_payload,
            coordinates={"latitude": 0.0, "longitude": 0.0},
        )
    except Exception:
        return [], transit_signs

    for pos in chart.positions or []:
        if not isinstance(pos, dict):
            continue
        body = str(pos.get("body") or pos.get("planet") or "").strip()
        sign = str(pos.get("sign") or "").strip()
        if not body or not sign:
            continue
        if body.lower() == "moon":
            transit_signs["moon_sign"] = {"sign": sign, "sign_ru": _sign_ru(sign), "source": "transit_chart"}
        elif body.lower() == "sun":
            transit_signs["sun_sign"] = {"sign": sign, "sign_ru": _sign_ru(sign), "source": "transit_chart"}

    callouts = aspect_engine.callouts(chart.positions, locale=locale)
    out: list[dict[str, Any]] = []
    for callout in callouts.callouts[:4]:
        aspect_id = str(callout.aspect_id or "").replace("_", " ")
        title = callout.bodies or callout.label
        desc = (callout.description or "").strip()
        if not desc:
            continue
        out.append(
            {
                "id": f"sky-{callout.aspect_id}-{len(out)}",
                "kind": "sky_aspect",
                "aspect": aspect_id,
                "title": title.replace(" · ", " — "),
                "story_ru": desc[:240],
                "tension_level": callout.tension_level or None,
            }
        )
    return out, transit_signs


async def build_celestial_events(
    target_date: date,
    locale: str,
    *,
    personal_day: int | None = None,
    personal_transits: list[dict[str, Any]] | None = None,
    astro_service: astro.AstroService | None = None,
) -> dict[str, Any]:
    """Assemble lunar phase, retrogrades, sky aspects, personal transits, symbols."""
    astro_service = astro_service or astro.AstroService()
    aspect_engine = AspectEngine()
    lunar_service = LunarService()
    retrograde_service = RetrogradeService(astro_service=astro_service)

    lunar_phase: dict[str, Any] | None = None
    try:
        moon_phase = lunar_service.current_phase(locale=locale)
        if moon_phase.current:
            lunar_phase = {
                "id": moon_phase.current.id,
                "name": moon_phase.current.name,
                "themes": moon_phase.current.themes,
                "guidance": moon_phase.current.guidance,
                "keywords": moon_phase.current.keywords or [],
                "cycle_day": moon_phase.current.cycle_day,
                "next_phase": {
                    "name": moon_phase.next_phase.name,
                    "date": moon_phase.next_phase.date,
                    "in_days": moon_phase.next_phase.in_days,
                }
                if moon_phase.next_phase
                else None,
            }
    except Exception:
        lunar_phase = None

    retrogrades: list[dict[str, Any]] = []
    ingresses_today: list[dict[str, Any]] = []
    try:
        retro_status = await retrograde_service.get_retrograde_status(
            forecast_date=target_date,
            locale=locale,
        )
        for planet in retro_status.retrograde_planets[:4]:
            retrogrades.append(
                {
                    "planet": planet,
                    "planet_ru": _planet_ru(planet),
                    "story_ru": _RETROGRADE_RU.get(
                        planet,
                        f"{_planet_ru(planet)} ретрограден — тема планеты просит пересмотра, а не рывка.",
                    ),
                }
            )
        for ing in retro_status.ingresses[:6]:
            ing_date = ing.ingress_date if hasattr(ing, "ingress_date") else ing.get("ingress_date")
            if not ing_date:
                continue
            try:
                ing_day = date.fromisoformat(str(ing_date)[:10])
            except ValueError:
                continue
            if (ing_day - target_date).days > 2:
                continue
            planet = ing.planet if hasattr(ing, "planet") else ing.get("planet")
            sign = ing.sign if hasattr(ing, "sign") else ing.get("sign")
            ingresses_today.append(
                {
                    "planet": planet,
                    "planet_ru": _planet_ru(str(planet)),
                    "sign": sign,
                    "sign_ru": _sign_ru(str(sign)),
                    "ingress_date": str(ing_date)[:10],
                    "story_ru": f"{_planet_ru(str(planet))} переходит в {_sign_ru(str(sign))} — меняется тон тем, которые она подсвечивает.",
                }
            )
    except Exception:
        pass

    sky_aspects, transit_signs = await _sky_aspects_for_date(
        target_date, locale, astro_service, aspect_engine
    )

    personal: list[dict[str, Any]] = []
    sorted_transits = sorted(personal_transits or [], key=_transit_sort_key)
    seen: set[str] = set()
    for tr in sorted_transits:
        formatted = _format_personal_transit(tr)
        if not formatted or formatted["id"] in seen:
            continue
        seen.add(formatted["id"])
        personal.append(formatted)
        if len(personal) >= 3:
            break

    preset = _DAILY_SYMBOL_PRESETS[_symbol_preset_index(target_date, personal_day)]
    daily_symbols = {
        "color": _build_color_symbol(preset["color"]),
        "stone": {"name": preset["stone"], "story_ru": "Тихий якорь — можно вернуться к нему, когда день ускоряется."},
        "totem": {
            "id": preset["totem_id"],
            "name": preset["totem_name"],
            "emoji": preset["totem_emoji"],
            "story_ru": preset["totem_story"],
        },
    }

    # Timed major Moon aspects + refine Moon ingress clock time for VOC window.
    timed_lunar_aspects: list[dict[str, Any]] = []
    try:
        timed_lunar_aspects = await find_timed_major_moon_aspects(
            astro_service,
            target_date=target_date,
        )
    except Exception:
        timed_lunar_aspects = []

    for row in ingresses_today:
        if not isinstance(row, dict):
            continue
        planet = str(row.get("planet") or "")
        if "moon" not in planet.lower() and "лун" not in str(row.get("planet_ru") or "").lower():
            continue
        if row.get("exact_time"):
            continue
        try:
            ing_day = date.fromisoformat(str(row.get("ingress_date") or target_date)[:10])
        except ValueError:
            ing_day = target_date
        try:
            exact = await find_moon_sign_ingress_time(astro_service, around_date=ing_day)
        except Exception:
            exact = None
        if exact is not None:
            row["exact_time"] = exact.isoformat(timespec="seconds")
            row["ingress_date"] = exact.date().isoformat()

    void_of_course = build_void_of_course_v0(
        target_date=target_date,
        ingresses=ingresses_today,
        timed_lunar_aspects=timed_lunar_aspects,
    )

    payload: dict[str, Any] = {
        "lunar_phase": lunar_phase,
        "retrogrades": retrogrades,
        "sky_aspects": sky_aspects,
        "personal_transits": personal,
        "ingresses": ingresses_today,
        "daily_symbols": daily_symbols,
        "timed_lunar_aspects": timed_lunar_aspects,
        "void_of_course": void_of_course,
    }
    if transit_signs.get("moon_sign"):
        payload["moon_sign"] = transit_signs["moon_sign"]
    if transit_signs.get("sun_sign"):
        payload["sun_sign"] = transit_signs["sun_sign"]
    return payload
