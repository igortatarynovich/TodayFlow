"""Deterministic sphere_cues for profile.spheres.synthesis.v1.

Builds prepared semantic facts (no raw planet=sign homework for the model).
Kitchen may retain planet/sign used to select cues.
"""

from __future__ import annotations

from typing import Any

from todayflow_backend.context_engine_v0.question_registry_v0 import QUESTION_SPECS
from todayflow_backend.services.life_spheres_traits_v0 import (
    normalize_sign,
    resolve_sphere_trait,
)

# Derived from P5 question registry (single SoT for question/value/style_key).
_SPHERE_NAMES = {"love": "Любовь", "money": "Деньги", "decisions": "Решения"}
SPHERE_CONTRACTS: dict[str, dict[str, str]] = {}
for _qid, _spec in QUESTION_SPECS.items():
    _sid = str(_spec.get("sphere_id") or "")
    if not _sid:
        continue
    SPHERE_CONTRACTS[_sid] = {
        "sphere_name": _SPHERE_NAMES.get(_sid, _sid),
        "user_question": str(_spec.get("user_question") or ""),
        "user_value": str(_spec.get("user_value") or ""),
        "style_key": str(_spec.get("style_key") or ""),
        "question_id": _qid,
    }
del _qid, _spec, _sid

# Short behavioral cues (RU). Selected by sphere × anchor planet × sign.
# Not user-facing final copy — synthesis input only.
_CUES_RU: dict[str, dict[str, dict[str, list[str]]]] = {
    "love": {
        "venus": {
            "aries": [
                "быстрее зажигается от прямой инициативы и явного интереса",
                "намёки вместо прямых слов охлаждают сближение",
                "нужен честный темп без игр в недосказанность",
            ],
            "taurus": [
                "раскрывается через устойчивый телесный комфорт и предсказуемый ритм",
                "резкие смены настроения партнёра выбивают почву",
                "ценит спокойную постоянность касаний и обещаний",
            ],
            "gemini": [
                "оживляется живым разговором и сменой ракурса",
                "затянувшаяся тишина без смысла ощущается как разрыв",
                "близость держится на обновлении темы, не на давлении",
            ],
            "cancer": [
                "сначала ищет эмоциональную безопасность, прежде чем раскрыться",
                "замечает заботу через постоянство и мелкие действия",
                "может защищать уязвимость уходом в себя",
            ],
            "leo": [
                "важно быть увиденным: тёплый отклик и щедрость внимания",
                "обесценивание желания гасит контакт быстрее мелкого отказа",
                "нужно право сиять без стыда за хотение близости",
            ],
            "virgo": [
                "включается через точные жесты заботы и порядок рядом",
                "хаос в мелочах копится в обиду без большого скандала",
                "уважение к телесным границам обязательнее громких слов",
            ],
            "libra": [
                "ищет равный обмен и взаимность шага",
                "перекос без разговора разрушает тепло",
                "нужен тон, где его не перетягивают",
            ],
            "scorpio": [
                "нужна глубина доверия сильнее множества поверхностных знаков",
                "фальшь в мелочи бьёт сильнее открытого конфликта",
                "проверяет правду чувством безопасности",
            ],
            "sagittarius": [
                "питает пространство свободы рядом и общий смысл",
                "ощущение клетки гасит влечение",
                "честный юмор важнее контроля",
            ],
            "capricorn": [
                "опирается на надёжность поступка сильнее красивых слов",
                "пустые обещания ломают близость",
                "ценит то, что можно проверить делом",
            ],
            "aquarius": [
                "нужен воздух дружбы внутри пары и личный контур",
                "липкий контроль выключает тепло",
                "уважение к странности важнее слияния",
            ],
            "pisces": [
                "тонко считывает настроение и легко растворяется в эмпатии",
                "жёсткий тон без объяснения ранит сильнее отказа",
                "нужна ясная бережная граница «я / мы»",
            ],
        },
        "sun": {
            "aries": [
                "базовый ход в любви — начинать контакт самому",
                "без ясного «да» инициатива выгорает в раздражении",
            ],
            "taurus": [
                "нужна стабильность под ногами в близости",
                "резкие качели настроения бьют больнее спора о деталях",
            ],
            "gemini": [
                "держит связь через обновление темы",
                "тишина без смысла читается как разрыв",
            ],
            "cancer": [
                "защищает внутренний дом в отношениях",
                "холодная отстранённость ранит сильнее прямой критики",
            ],
            "leo": [
                "важно чувство взаимного света",
                "обесценивание желания гасит контакт",
            ],
            "virgo": [
                "чинит связь делом",
                "невыполненные мелочи копятся в обиду",
            ],
            "libra": [
                "балансирует «мы»",
                "перекос без разговора разрушает тепло",
            ],
            "scorpio": [
                "проверяет правду взглядом и тоном",
                "фальшь бьёт сильнее открытого конфликта",
            ],
            "sagittarius": [
                "нужен горизонт вместе",
                "клетка гасит влечение быстрее бытовой усталости",
            ],
            "capricorn": [
                "строит на долгом доверии",
                "пустые обещания ломают близость сильнее дистанции",
            ],
            "aquarius": [
                "нужна честная дистанция внутри связи",
                "контроль выключает тепло быстрее ссоры",
            ],
            "pisces": [
                "тонко считывает настроение",
                "жёсткий тон без объяснения ранит сильнее отказа",
            ],
        },
    },
    "money": {
        "jupiter": {
            "aries": [
                "рост через смелый первый вклад с потолком",
                "без потолка импульс съедает запас",
            ],
            "taurus": [
                "легче наращивать ценность регулярными шагами, чем рывком",
                "стабильность базы важнее случайного куша",
            ],
            "gemini": [
                "возможности открываются через несколько каналов",
                "риск — размазать фокус между ними",
            ],
            "cancer": [
                "спокойнее, когда есть запас на близких и на себя",
                "рост без чувства безопасности не держится",
            ],
            "leo": [
                "щедрый жест усиливает чувство ценности",
                "без учёта жест превращается в дыру статуса",
            ],
            "virgo": [
                "рост через точную правку расхода",
                "маленькая настройка даёт больше громкого плана",
            ],
            "libra": [
                "важен взаимный обмен ценности",
                "односторонние вложения размывают ресурс",
            ],
            "scorpio": [
                "сила в контроле скрытых обязательств",
                "прозрачность долга важнее оптимистичного обещания роста",
            ],
            "sagittarius": [
                "горизонт расширяется через обучение и дальний ход",
                "без якоря цифр энтузиазм разлетается",
            ],
            "capricorn": [
                "рост как лестница достижений и платёжная дисциплина",
                "случайный куш менее надёжен, чем график",
            ],
            "aquarius": [
                "ближе нестандартный канал дохода",
                "честный разговор о ценности важнее чужого шаблона успеха",
            ],
            "pisces": [
                "граница «своё / чужое» легко размывается",
                "явная сумма и срок спасают от тихого истощения",
            ],
        },
        "saturn": {
            "aries": ["дисциплина — вовремя остановить импульс покупки"],
            "taurus": ["опора — скучный регулярный платёж себе"],
            "gemini": ["полезен один выбранный фокус учёта"],
            "cancer": ["отделить заботу о близких от самопожертвования бюджетом"],
            "leo": ["статусный жест только из просчитанного слота"],
            "virgo": ["довести учёт до конца недели важнее идеальной таблицы"],
            "libra": ["вовремя назвать цену своего вклада"],
            "scorpio": ["жёсткая ясность по долгам снимает тревогу"],
            "sagittarius": ["одна дальняя цель вместо трёх параллельных «важных» трат"],
            "capricorn": ["долгий платёжный каркас надёжнее рывка"],
            "aquarius": ["зафиксировать свои правила обмена, даже если они необычны"],
            "pisces": ["сумма и дата важнее настроения «помогу потом»"],
        },
        "sun": {
            "aries": ["базовый ход — решить и двинуть сумму"],
            "taurus": ["базовый ход — удержать уже заработанное"],
            "gemini": ["собрать факты из двух источников, выбрать один канал"],
            "cancer": ["сначала закрыть чувство безопасности, потом рост"],
            "leo": ["связать трату с самоуважением осознанно"],
            "virgo": ["починить одну дыру в учёте до новых вложений"],
            "libra": ["выровнять обмен в ясных единицах"],
            "scorpio": ["вскрыть скрытый хвост обязательств до обещания роста"],
            "sagittarius": ["выбрать один горизонт и отрезать параллельные ставки"],
            "capricorn": ["поставить платёж в календарь как работу"],
            "aquarius": ["назвать свою нестандартную цену вслух"],
            "pisces": ["отделить помощь другим от минимального запаса одной цифрой"],
        },
    },
    "decisions": {
        "saturn": {
            "aries": [
                "зрелость — зафиксировать ход и точку проверки, а не переигрывать выбор",
                "импульс «ещё раз» разрушает уже принятое",
            ],
            "taurus": [
                "помогает медленная фиксация выбранного варианта",
                "не дергать решение без новых фактов",
            ],
            "gemini": [
                "рамка — сузить до двух формулировок",
                "иначе ум плодит ветки без закрытия",
            ],
            "cancer": [
                "отделить страх за близких от своего критерия",
                "иначе выбор тонет в чужой тревоге",
            ],
            "leo": [
                "нужна видимая ответственность за выбор",
                "назвать выбор вслух и принять его цену",
            ],
            "virgo": [
                "довести один критерий до конца",
                "не улучшать список критериев бесконечно",
            ],
            "libra": [
                "ловушка — вечный баланс",
                "сила — объявить перевес и жить с ним до пересмотра",
            ],
            "scorpio": [
                "нужна правда о цене выбора",
                "сладкая версия без риска не даёт опереться",
            ],
            "sagittarius": [
                "горизонт без даты хода остаётся мечтой",
                "нужен срок первому шагу",
            ],
            "capricorn": [
                "превратить выбор в график: критерий, срок, ответственный — ты",
                "несделанное — долг перед собой",
            ],
            "aquarius": [
                "опереться на своё правило, даже если круг ждёт «как принято»",
                "назвать своё условие отдельно",
            ],
            "pisces": [
                "туман настроения снимается внешней опорой",
                "цифра, дата или ясный факт до выбора",
            ],
        },
        "mercury": {
            "aries": ["формулировать выбор в одном предложении"],
            "taurus": ["повторить вывод своими словами и дать отлежаться"],
            "gemini": ["записать две ветки и вычеркнуть третью как шум"],
            "cancer": ["вынести критерий на бумагу, чтобы не решить из обиды"],
            "leo": ["сказать выбор так, чтобы можно было за него стоять"],
            "virgo": ["ограничить проверку одним кругом фактов, затем закрыть"],
            "libra": ["формулировки за/против помогают выйти из качелей"],
            "scorpio": ["проверить один скрытый мотив вслух до утверждения хода"],
            "sagittarius": ["сжать большую идею в следующий конкретный шаг"],
            "capricorn": ["сухой протокол: что решено, к какому сроку, что сделано"],
            "aquarius": ["зафиксировать своё условие отдельно от мнения большинства"],
            "pisces": ["перевести ощущение в одну проверяемую фразу"],
        },
        "sun": {
            "aries": ["выбрать быстро и назначить проверку"],
            "taurus": ["не дергать выбранное без новых фактов"],
            "gemini": ["сравнить две опции и отбросить остальное"],
            "cancer": ["спросить, что защищает спокойствие, и выбрать от этого"],
            "leo": ["взять авторство выбора на себя"],
            "virgo": ["исправить один изъян плана, затем действовать"],
            "libra": ["объявить временный перевес до даты пересмотра"],
            "scorpio": ["назвать настоящую цену варианта"],
            "sagittarius": ["связать выбор с дальним смыслом и ближайшим шагом"],
            "capricorn": ["вписать выбор в срок"],
            "aquarius": ["проверить, не подменяешь ли своё правило чужим удобством"],
            "pisces": ["вынести выбор из тумана настроения на внешнюю опору"],
        },
    },
}

_SPHERE_PLANETS = {
    "love": ("venus", "sun"),
    "money": ("jupiter", "saturn", "sun"),
    "decisions": ("saturn", "mercury", "sun"),
}


def _house_cues(natal: dict[str, Any], sphere_id: str) -> list[dict[str, str]]:
    if not natal.get("houses_available"):
        return []
    houses = natal.get("houses") if isinstance(natal.get("houses"), dict) else {}
    mapping = {"love": ("7",), "money": ("2", "8"), "decisions": ("9",)}
    out: list[dict[str, str]] = []
    for n in mapping.get(sphere_id) or ():
        row = houses.get(str(n))
        if not isinstance(row, dict):
            continue
        text = str(row.get("description") or row.get("theme") or "").strip()
        if len(text) < 12:
            continue
        # Strip explicit "N дом" labels if present — behavioral locus only
        out.append({"id": f"house:{n}", "text": text[:220]})
    return out


def build_sphere_cues(sphere_id: str, foundations: dict[str, Any]) -> dict[str, Any]:
    """Return synthesis input pack + kitchen trace."""
    contract = SPHERE_CONTRACTS.get(sphere_id)
    if not contract:
        return {"ok": False, "reason": "unknown_sphere", "sphere_id": sphere_id}

    styles = foundations.get("styles") if isinstance(foundations.get("styles"), dict) else {}
    identity = foundations.get("identity") if isinstance(foundations.get("identity"), dict) else {}
    natal = foundations.get("natal") if isinstance(foundations.get("natal"), dict) else {}
    style_key = contract["style_key"]
    relevant_style = str(styles.get(style_key) or "").strip()
    if len(relevant_style) < 12:
        return {"ok": False, "reason": "style_missing", "sphere_id": sphere_id}

    cues: list[dict[str, str]] = []
    kitchen: dict[str, Any] = {"planets_used": [], "signs_used": [], "cue_source": []}

    for planet in _SPHERE_PLANETS.get(sphere_id) or ():
        sign = normalize_sign(str(natal.get(f"{planet}_sign") or "") or None)
        if not sign:
            continue
        bullets = ((_CUES_RU.get(sphere_id) or {}).get(planet) or {}).get(sign) or []
        if not bullets:
            continue
        kitchen["planets_used"].append(planet)
        kitchen["signs_used"].append(sign)
        for i, text in enumerate(bullets):
            cid = f"cue:{sphere_id}.{planet}.{sign}.{i}"
            cues.append({"id": cid, "text": text})
            kitchen["cue_source"].append(cid)
        # Prefer primary planet cues; add sun only if primary missing enough
        if planet != "sun" and len(cues) >= 2:
            break

    if not cues:
        trait = resolve_sphere_trait(sphere_id, natal, locale=str(foundations.get("locale") or "ru"))
        if trait:
            cues.append(
                {
                    "id": str(trait["trait_rule_id"]),
                    "text": str(trait["text"]),
                }
            )
            kitchen["cue_source"].append(trait["trait_rule_id"])
            kitchen["planets_used"].append(trait.get("planet"))
            kitchen["signs_used"].append(trait.get("sign"))
            kitchen["fallback"] = "trait_paragraph"

    if not cues:
        return {"ok": False, "reason": "cues_empty", "sphere_id": sphere_id, "kitchen": kitchen}

    house_cues = _house_cues(natal, sphere_id)
    return {
        "ok": True,
        "sphere_id": sphere_id,
        "sphere_name": contract["sphere_name"],
        "user_question": contract["user_question"],
        "user_value": contract["user_value"],
        "identity_core": str(identity.get("identity_core") or "").strip(),
        "strengths": identity.get("strengths") if isinstance(identity.get("strengths"), list) else [],
        "growth_zones": identity.get("growth_zones") if isinstance(identity.get("growth_zones"), list) else [],
        "relevant_style": relevant_style,
        "style_key": style_key,
        "sphere_cues": cues,
        "house_cues": house_cues,
        "locale": str(foundations.get("locale") or "ru"),
        "kitchen": kitchen,
    }
