"""Personalized surface for natal-chart interpretations."""

from __future__ import annotations

import re
from typing import Any


_HOUSE_AREAS: dict[int, str] = {
    1: "identity",
    2: "money",
    3: "general",
    4: "family",
    5: "love",
    6: "career",
    7: "love",
    8: "general",
    9: "general",
    10: "career",
    11: "general",
    12: "family",
}

_HOUSE_INTROS: dict[int, str] = {
    1: "Этот дом показывает, как ты входишь в жизнь, заявляешь о себе и собираешь личную линию.",
    2: "Здесь особенно видно, на чём держатся твоя ценность, деньги и ощущение устойчивости.",
    3: "Через этот дом читается твой способ думать, говорить и собирать повседневную среду вокруг себя.",
    4: "Эта тема напрямую связана с тем, как ты создаёшь дом, восстанавливаешься и держишь близких рядом.",
    5: "Здесь раскрывается твоя живая энергия: радость, романтика, творчество и смелость проявляться.",
    6: "Этот дом показывает, как ты держишь рабочий ритм, тело, нагрузку и повседневные обязательства.",
    7: "Через этот дом особенно видно, как ты входишь в близость, партнёрство и живые договорённости.",
    8: "Здесь карта показывает, как ты проходишь через напряжение, доверие, глубину и общие ресурсы.",
    9: "Этот дом говорит о том, как ты расширяешь взгляд, ищешь смысл и выбираешь дальний горизонт.",
    10: "Здесь читается твоя взрослая реализация: карьера, ответственность, статус и направление пути.",
    11: "Этот дом показывает, с кем ты идёшь дальше, во что веришь и как видишь своё будущее.",
    12: "Через эту сферу карта показывает, как ты восстанавливаешься, перевариваешь чувства и слышишь себя в тишине.",
}

_PLANET_AREAS: dict[str, str] = {
    "Sun": "identity",
    "Moon": "family",
    "Mercury": "career",
    "Venus": "love",
    "Mars": "career",
    "Jupiter": "general",
    "Saturn": "career",
    "Uranus": "general",
    "Neptune": "family",
    "Pluto": "general",
    "Chiron": "family",
    "North Node": "general",
    "South Node": "identity",
}

# Знаки с движка часто приходят по-английски — для связного русского текста в profile_lens.
_SIGN_EN_TO_RU: dict[str, str] = {
    "Aries": "Овне",
    "Taurus": "Тельце",
    "Gemini": "Близнецах",
    "Cancer": "Раке",
    "Leo": "Льве",
    "Virgo": "Деве",
    "Libra": "Весах",
    "Scorpio": "Скорпионе",
    "Sagittarius": "Стрельце",
    "Capricorn": "Козероге",
    "Aquarius": "Водолее",
    "Pisces": "Рыбах",
}

_SIGN_RU_TO_PREP: dict[str, str] = {
    "Овен": "Овне",
    "Телец": "Тельце",
    "Близнецы": "Близнецах",
    "Рак": "Раке",
    "Лев": "Льве",
    "Дева": "Деве",
    "Весы": "Весах",
    "Скорпион": "Скорпионе",
    "Стрелец": "Стрельце",
    "Козерог": "Козероге",
    "Водолей": "Водолее",
    "Рыбы": "Рыбах",
}

# Именительный падеж для вставки в fallback («образ Водолея», не aquarius)
_SIGN_EN_TO_NOM: dict[str, str] = {
    "Aries": "Овна",
    "Taurus": "Тельца",
    "Gemini": "Близнецов",
    "Cancer": "Рака",
    "Leo": "Льва",
    "Virgo": "Девы",
    "Libra": "Весов",
    "Scorpio": "Скорпиона",
    "Sagittarius": "Стрельца",
    "Capricorn": "Козерога",
    "Aquarius": "Водолея",
    "Pisces": "Рыб",
}


def _sign_label_prepositional(sign: str | None) -> str:
    """Знак в предложном падеже после «в» («в Деве»); понимает en и ru."""
    if not sign:
        return ""
    key = str(sign).strip()
    if key in _SIGN_EN_TO_RU:
        return _SIGN_EN_TO_RU[key]
    return _SIGN_RU_TO_PREP.get(key, key)


_PLANET_INTROS: dict[str, str] = {
    "Sun": "Это главный слой характера: здесь видно, чем ты светишь, на чём держится чувство себя и куда тебя естественно тянет.",
    "Moon": "Здесь раскрывается твоя эмоциональная линия: что даёт безопасность, как ты переживаешь близость и где быстрее всего накапливается усталость.",
    "Mercury": "Это про твой способ мыслить, говорить и собирать смысл вокруг себя в работе и в обычной жизни.",
    "Venus": "Здесь карта показывает, что для тебя красиво, дорого и по-настоящему ценно в любви и в выборе людей.",
    "Mars": "Это про твой двигатель: как ты идёшь в действие, держишь напор, злишься и продавливаешь важное.",
    "Jupiter": "Через эту планету видно, где у тебя включается рост, смысл, расширение и чувство перспективы.",
    "Saturn": "Здесь карта показывает, где ты взрослеешь, выдерживаешь нагрузку и строишь долгую опору.",
    "Uranus": "Это про твою свободу, неожиданные повороты и ту часть, которая не любит жить по чужому шаблону.",
    "Neptune": "Через эту планету видно твою чувствительность, интуицию, идеализацию и глубину внутреннего мира.",
    "Pluto": "Здесь лежит твоя сила глубокой перестройки: то, что меняет тебя не поверхностно, а по-настоящему.",
    "Chiron": "Этот слой показывает старую чувствительность и тот опыт, через который со временем приходит зрелое понимание себя и других.",
    "North Node": "Здесь карта подсказывает, в какую сторону тебя постепенно разворачивает жизнь и что просит дорастить.",
    "South Node": "Это привычный опыт, на который ты легко опираешься, но в котором можно и застрять, если всё время жить только им.",
}


def _clean_text(value: str | None, fallback: str = "") -> str:
    text = " ".join((value or "").strip().split())
    return text or fallback


def _first_sentence(value: str | None, fallback: str = "", max_len: int = 220) -> str:
    text = _clean_text(value, fallback)
    if not text:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", text)
    sentence = parts[0].strip() if parts else text
    if len(sentence) <= max_len:
        return sentence
    return sentence[: max_len - 1].rstrip() + "…"


def _core_area_text(core_profile: dict[str, Any] | None, area: str) -> str:
    payload = core_profile or {}
    interpretation = payload.get("interpretation") if isinstance(payload.get("interpretation"), dict) else {}
    daily = payload.get("daily_interpretation") if isinstance(payload.get("daily_interpretation"), dict) else {}
    daily_lenses = daily.get("daily_lenses") if isinstance(daily.get("daily_lenses"), dict) else {}
    baseline = payload.get("baseline") if isinstance(payload.get("baseline"), dict) else {}

    if area == "identity":
        seed_raw = baseline.get("archetype_seed")
        seed_key = str(seed_raw).strip() if seed_raw is not None else ""
        seed_norm = seed_key.title() if seed_key else ""
        if seed_norm in _SIGN_EN_TO_NOM:
            archetype_phrase = f"образа {_SIGN_EN_TO_NOM[seed_norm]}"
        elif seed_key:
            archetype_phrase = f"архетипа «{seed_key}»"
        else:
            archetype_phrase = "твоей личной линии"
        return _first_sentence(
            interpretation.get("identity"),
            fallback=(
                f"Твоя карта опирается на {archetype_phrase} "
                f"и ритм {baseline.get('rhythm_style') or 'спокойного устойчивого темпа'}."
            ),
        )
    if area == "general":
        return _first_sentence(
            daily_lenses.get("general") or interpretation.get("identity"),
            fallback=(
                f"Тебе лучше всего работает формат, где есть {baseline.get('element_focus') or 'понятная опора'} "
                f"и {baseline.get('rhythm_style') or 'мягкий ритм без лишних рывков'}."
            ),
        )

    life_areas = interpretation.get("life_areas") if isinstance(interpretation.get("life_areas"), dict) else {}
    life_text = life_areas.get(area)
    daily_text = daily_lenses.get(area)
    if area == "career":
        fallback = "Рабочая реализация раскрывается лучше там, где у тебя есть своя роль, ясная ответственность и видимый результат."
    elif area == "money":
        fallback = "Денежная линия растёт там, где чувство своей ценности не отрывается от реального результата и практичной опоры."
    elif area == "love":
        fallback = "Близость раскрывается лучше там, где можно не угадывать, а говорить прямо, чувствовать надёжность и живой отклик."
    else:
        fallback = "Тема дома и внутренней безопасности напрямую влияет на твой ресурс, поэтому тебе особенно важны ясность и ощущение надёжности."
    return _first_sentence(life_text or daily_text, fallback=fallback)


def _compose_profile_lens(intro: str, profile_text: str, emphasis: str | None = None) -> str:
    parts = [_clean_text(intro), _clean_text(profile_text)]
    if emphasis:
        parts.append(_clean_text(emphasis))
    return " ".join(part for part in parts if part).strip()


def _house_emphasis(house_number: int, sign_hint: str | None) -> str:
    sign_part = f" {sign_hint}" if sign_hint else ""
    if house_number in {1, 4, 7, 10}:
        return f"Это один из опорных домов карты, поэтому он сильнее влияет на твою общую жизненную линию.{sign_part}"
    if house_number in {2, 5, 6, 8}:
        return f"Здесь тема проявляется через конкретный быт, решения и повторяемые жизненные сценарии.{sign_part}"
    return f"Этот дом работает как фон, который со временем сильно влияет на твои выборы и направление движения.{sign_part}"


def _planet_emphasis(planet: str, sign: str | None, house: int | None) -> str:
    """Дополнение к планетам в списке positions (не путать с углами asc/mc в angles)."""
    ru = _sign_label_prepositional(sign)
    sign_part = f" В знаке {ru} это проявляется особенно отчётливо." if ru else ""
    house_part = f" Положение в {house}-м доме добавляет бытовой контекст: где это чаще всего заметно." if house else ""
    if planet in {"Sun", "Moon"}:
        return f"Солнце и Луна — опорные светила карты, их быстрее замечают и ты сам(а), и окружение.{sign_part}{house_part}"
    if planet in {"rising", "Rising", "Ascendant", "ASC"}:
        # В positions тело часто называется rising; это угол, не планета.
        return (
            f"Это асцендент (угол востока), а не планета: он задаёт «маску» первого контакта."
            f"{sign_part or (' Здесь важен знак на линии горизонта в момент рождения.' if not sign else '')}{house_part}"
        )
    if planet in {"Venus", "Mars", "Mercury"}:
        return f"Этот слой заметен в разговоре, решениях и реакции на близость или нагрузку.{sign_part}{house_part}"
    return f"Здесь речь о долгих циклах взросления и смены опор, а не о одном дне.{sign_part}{house_part}"


def _angle_profile_lens(core_line: str, *, kind: str, sign: str | None) -> str:
    """Один связный абзац для углов: без «планеты» и без дубля с полем meaning на фронте."""
    core = _clean_text(core_line)
    ru = _sign_label_prepositional(sign)
    if kind == "ascendant":
        tail = (
            f"Асцендент в {ru}: так чаще всего читают первый контакт и внешний тон."
            if ru
            else "Асцендент — угол востока в момент рождения; это не планета, а линия «как меня видят снаружи»."
        )
    else:
        tail = (
            f"MC в {ru}: видимая линия ролей, статуса и «наружного» вектора роста."
            if ru
            else "MC (середина неба) — угол карьеры и публичной линии, не планета."
        )
    return _compose_profile_lens(core, tail)


def apply_profile_lens_to_natal_interpretations(
    interpretations: dict[str, Any],
    core_profile: dict[str, Any] | None,
) -> dict[str, Any]:
    if not isinstance(interpretations, dict):
        return interpretations

    houses = interpretations.get("houses")
    if isinstance(houses, dict):
        for raw_house, payload in list(houses.items()):
            if not isinstance(payload, dict):
                continue
            try:
                house_number = int(raw_house)
            except (TypeError, ValueError):
                continue
            area = _HOUSE_AREAS.get(house_number, "general")
            payload["profile_lens"] = _compose_profile_lens(
                _HOUSE_INTROS.get(house_number, "Этот дом показывает отдельную, но важную часть твоей жизненной карты."),
                _core_area_text(core_profile, area),
                _house_emphasis(house_number, payload.get("sign_in_house")),
            )

    planets = interpretations.get("planets")
    if isinstance(planets, list):
        for payload in planets:
            if not isinstance(payload, dict):
                continue
            planet = str(payload.get("planet") or "")
            area = _PLANET_AREAS.get(planet, "general")
            house = payload.get("house")
            try:
                house_number = int(house) if house is not None else None
            except (TypeError, ValueError):
                house_number = None
            payload["profile_lens"] = _compose_profile_lens(
                _PLANET_INTROS.get(planet, "Этот слой карты показывает твою устойчивую часть характера и реакции."),
                _core_area_text(core_profile, area),
                _planet_emphasis(planet, payload.get("sign"), house_number),
            )

    angles = interpretations.get("angles")
    if isinstance(angles, dict):
        asc = angles.get("ascendant")
        if isinstance(asc, dict):
            asc["profile_lens"] = _angle_profile_lens(
                _core_area_text(core_profile, "identity"),
                kind="ascendant",
                sign=asc.get("sign"),
            )
        mc = angles.get("mc")
        if isinstance(mc, dict):
            mc["profile_lens"] = _angle_profile_lens(
                _core_area_text(core_profile, "career"),
                kind="mc",
                sign=mc.get("sign"),
            )

    return interpretations
