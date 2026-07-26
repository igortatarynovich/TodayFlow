"""Character Engine → Profile consumption slice v0.

Architecture: Identity Core (+ Stage 1 evidence + Stage 3 Internal Engine when grounded)
become SoT for Profile journey and character slots. Natal instrument (wheel / houses /
aspects) stays Swiss facts. Archetype illustration seed remains FE visual only —
not recognition title SoT.

Owned when Stage 2 grounded + flag on:
  - recognition / identity_core
  - portrait_why
  - insight trap (+ help) — Stage 3 primary_tension when grounded, else editorial bank
  - strengths / growth_zones / helps
  - decision_style — Stage 3 internal_engine.decision when grounded, else editorial bank
  - relationship_style / money_style
  - recurring_patterns
  - clears living_changes day-rhythm leak

Not owned yet: natal cusp/sign/degree facts stay Swiss.
"""

from __future__ import annotations

import re
from typing import Any

from todayflow_backend.core.config import settings

PROJECTION_VERSION = "character_engine_profile_consumption_v0.7"
_MAX_RECOGNITION = 160
_MAX_CORE = 420
_MAX_TRAP = 220
_MAX_ESSAY = 360

# Deterministic trap lines — editorial SoT for this slice (Architecture impact: overwrite trap).
_TRAP_BY_IDENTITY_THESIS: dict[str, str] = {
    "builds_through_autonomy": (
        "Пока ты держишь дистанцию как способ сохранить ясность, выбор и близость "
        "откладываются — контроль растёт, а жизнь перестаёт двигаться."
    ),
    "builds_through_analysis": (
        "Пока ты продолжаешь анализировать вместо выбора, ощущение контроля растёт, "
        "а движение останавливается."
    ),
    "builds_through_air_mind": (
        "Пока ты собираешь идеи и связи вместо направления, понимание растёт, "
        "а решение не наступает."
    ),
    "builds_through_earth_stability": (
        "Пока ты ждёшь идеальной прочности основания, жизнь остаётся на паузе — "
        "устойчивость превращается в отсрочку."
    ),
    "builds_through_water_care": (
        "Пока ты растворяешь границы ради чужой боли, собственные контуры стираются — "
        "забота становится потерей себя."
    ),
    "builds_through_emotional_depth": (
        "Пока ты проживаешь всё слишком глубоко до любого шага, чувства заполняют поле, "
        "а действие откладывается."
    ),
    "builds_through_earth_anchor": (
        "Пока ты цепляешься за привычный порядок как за единственную опору, "
        "новое не входит — якорь становится клеткой."
    ),
    "builds_through_freedom_vs_stability": (
        "Пока свобода и опора тянут в разные стороны без выбора, ты тратишь силу "
        "на удержание напряжения вместо движения."
    ),
    "builds_through_fire_drive": (
        "Пока импульс важнее направления, скорость растёт, а выбранный путь не собирается."
    ),
    "builds_through_air_presence": (
        "Пока ты входишь в мир через лёгкий контакт и разговор, глубина связи "
        "остаётся недоступной."
    ),
    "builds_through_fire_presence": (
        "Пока первый контакт строится на напоре, вокруг появляется реакция, "
        "а не устойчивое пространство."
    ),
    "builds_through_earth_presence": (
        "Пока ты показываешь только надёжную форму, живое движение остаётся спрятанным."
    ),
    "builds_through_water_presence": (
        "Пока ты встречаешь мир через чуткую оболочку, собственные желания "
        "остаются неназванными."
    ),
}

# Editorial essays keyed by Identity Core thesis — overwrite funnel «Вы» blocks.
# Architecture impact: formula bank is SoT for these slots while consumption flag is on.
_ESSAYS_BY_IDENTITY: dict[str, dict[str, Any]] = {
    "builds_through_autonomy": {
        "strengths": [
            "Ясная собственная система — ты видишь структуру там, где другие тонут в шуме.",
            "Способность держать дистанцию как инструмент ясности, а не как обиду.",
            "Независимое мышление: доходишь до вывода сам, не подстраиваясь под чужой темп.",
            "Чутьё на связи идей и людей — без потери внутреннего контура.",
        ],
        "growth_zones": [
            "Учиться входить в близость, не сдавая автономию как единственную защиту.",
            "Переводить понимание в выбор — не оставлять жизнь на паузе анализа.",
            "Замечать, когда дистанция уже не ясность, а отсрочка контакта.",
        ],
        "helps": [
            "Сделай один явный выбор сегодня — без полного согласования со всеми.",
            "Назови границу вслух: что ты оставляешь своим, а что открываешь.",
        ],
        "decision_style": (
            "Ты решаешь через собственную систему: сначала внутренний контур и смысл, "
            "потом внешнее согласие. Решение зреет, когда ты сам дошёл до ясности — "
            "чужой темп редко становится достаточным аргументом."
        ),
        "relationship_style": (
            "В близости тебе нужна свобода дышать своим ритмом. Ты серьёзен в связи, "
            "но входишь осторожно: сначала доверие к своей ясности, потом открытость. "
            "Партнёрство работает, когда автономия не читается как холод."
        ),
        "money_style": (
            "Деньги для тебя — ресурс независимости и пространства для своей системы. "
            "Ты лучше чувствуешь нестандартные схемы и совместные форматы, если в них "
            "сохраняется твой контур выбора, а не только чужие ожидания."
        ),
    },
    "builds_through_analysis": {
        "strengths": [
            "Точность до шага — ты разбираешь устройство раньше, чем действуешь.",
            "Системное видение: находишь скрытые связи и закономерности.",
            "Способность удерживать сложность без паники.",
        ],
        "growth_zones": [
            "Не путать полноту картины с правом на выбор.",
            "Давать телу и ритму место рядом с умом.",
            "Замечать, когда анализ уже защищает от риска контакта.",
        ],
        "helps": [
            "Выбери один неполный, но честный следующий шаг.",
            "Ограничь сбор данных сроком — потом действуй.",
        ],
        "decision_style": (
            "Ты решаешь через разбор: взвешиваешь структуру, мотивы и последствия. "
            "Сила — в точности; риск — застрять в проверке вместо движения."
        ),
        "relationship_style": (
            "В близости ты сначала понимаешь устройство связи, потом открываешься. "
            "Тебе важны ясность и честный разговор о правилах — эмоции входят, "
            "когда есть карта."
        ),
        "money_style": (
            "К финансам ты подходишь как к системе: схема, риск, горизонт. "
            "Деньги работают лучше, когда план ясен, а не когда импульс ведёт."
        ),
    },
    "builds_through_air_mind": {
        "strengths": [
            "Идеи и связи собираются быстро — ты видишь сеть раньше формы.",
            "Лёгкость входа в разговор и обмен смыслами.",
            "Способность держать несколько линий внимания без потери любопытства.",
        ],
        "growth_zones": [
            "Сводить идеи к одному направлению, а не к бесконечному ветвлению.",
            "Давать телу и обязательству место рядом с умом.",
            "Не путать интерес с завершённым выбором.",
        ],
        "helps": [
            "Выбери одну идею и доведи её до видимого шага.",
            "Закрой одну ветку разговора решением, не новым вопросом.",
        ],
        "decision_style": (
            "Ты решаешь через карту идей: сравниваешь смыслы, связи и варианты. "
            "Решение становится живым, когда одна линия побеждает остальные."
        ),
        "relationship_style": (
            "Близость для тебя начинается с разговора и обмена мирами. "
            "Глубина появляется, когда интерес переходит в выбранное присутствие."
        ),
        "money_style": (
            "Деньги связаны с идеями, сетями и свободой манёвра. "
            "Ты сильнее, когда поток средств обслуживает ясное направление, а не только любопытство."
        ),
    },
    "builds_through_earth_stability": {
        "strengths": [
            "Опора на осязаемое — ты строишь то, что держит.",
            "Терпение к процессу и уважение к фундаменту.",
            "Практическая надёжность в долгих линиях.",
        ],
        "growth_zones": [
            "Не ждать идеальной прочности перед первым шагом.",
            "Пускать новое, пока основание ещё «достаточно».",
            "Замечать, когда устойчивость стала отсрочкой.",
        ],
        "helps": [
            "Сделай маленький шаг на неидеальном основании.",
            "Отдели «нужно укрепить» от «можно уже двигаться».",
        ],
        "decision_style": (
            "Ты решаешь через прочность: что выдержит время и нагрузку. "
            "Сила — в опоре; риск — отложить жизнь до идеальных условий."
        ),
        "relationship_style": (
            "В связи тебе важны надёжность, предсказуемость и общий быт как опора. "
            "Близость растёт, когда безопасность не требует заморозки движения."
        ),
        "money_style": (
            "Деньги — материал устойчивости. Ты лучше чувствуешь долгий горизонт, "
            "накопление и понятные обязательства, чем чистый риск ради скорости."
        ),
    },
    "builds_through_water_care": {
        "strengths": [
            "Проницаемость к чужой боли и тонким сигналам поля.",
            "Способность создавать мягкое пространство для других.",
            "Интуитивное чтение настроений и несказанного.",
        ],
        "growth_zones": [
            "Держать собственные границы рядом с заботой.",
            "Не растворять «я» в чужой нужде.",
            "Называть свои желания так же ясно, как чужие.",
        ],
        "helps": [
            "Спроси себя, чего хочешь ты — до ответа «чем помочь».",
            "Поставь одну мягкую, но явную границу сегодня.",
        ],
        "decision_style": (
            "Ты решаешь через чувственное поле: что бережёт связь и что ранит. "
            "Сила — в чуткости; риск — отдать выбор чужой боли."
        ),
        "relationship_style": (
            "Близость для тебя — пространство заботы и эмоциональной правды. "
            "Связь жива, когда забота двусторонняя и твои контуры не стираются."
        ),
        "money_style": (
            "Деньги часто связаны с поддержкой и смыслом «для кого». "
            "Тебе важна ясность: щедрость не должна становиться самопотерей."
        ),
    },
    "builds_through_emotional_depth": {
        "strengths": [
            "Глубина переживания — ты чувствуешь слой глубже поверхности.",
            "Способность выдерживать сложные эмоции без упрощения.",
            "Честность с внутренним миром как источник правды.",
        ],
        "growth_zones": [
            "Не откладывать шаг, пока чувство «не до конца прожито».",
            "Отделять интенсивность от необходимости действовать.",
            "Пускать лёгкость рядом с глубиной.",
        ],
        "helps": [
            "Сделай один внешний шаг при неполном внутреннем закрытии темы.",
            "Назови чувство коротко — и перейди к действию.",
        ],
        "decision_style": (
            "Ты решаешь из глубины: решение должно быть прожито, не только понято. "
            "Сила — в правде чувства; риск — застрять в переживании до шага."
        ),
        "relationship_style": (
            "В близости тебе нужна эмоциональная плотность и честность. "
            "Ты открываешься глубоко — и ждёшь такого же уровня присутствия."
        ),
        "money_style": (
            "К деньгам ты относишься лично: смысл и безопасность важнее статуса. "
            "Финансы стабильнее, когда не несут весь груз невысказанных чувств."
        ),
    },
    "builds_through_earth_anchor": {
        "strengths": [
            "Якорь в порядке и ритме — ты даёшь устойчивость себе и другим.",
            "Умение возвращать поле к понятной структуре.",
            "Практическая опора в хаосе.",
        ],
        "growth_zones": [
            "Не путать привычный порядок с единственно возможным.",
            "Пускать новое без полной перестройки якоря.",
            "Замечать, когда стабильность стала клеткой.",
        ],
        "helps": [
            "Оставь один привычный ритуал — и добавь один новый жест.",
            "Спроси: что держит меня, а что только привычно.",
        ],
        "decision_style": (
            "Ты решаешь через якорь: что сохранит ритм и не разрушит опору. "
            "Сила — в устойчивости; риск — отвергнуть живое ради знакомого."
        ),
        "relationship_style": (
            "В связи тебе важны ритуал, дом и предсказуемый контур. "
            "Близость растёт, когда якорь не запрещает обновление."
        ),
        "money_style": (
            "Деньги — часть якоря: бюджет, регулярность, понятные правила. "
            "Ты спокойнее, когда финансы не требуют постоянной импровизации."
        ),
    },
    "builds_through_freedom_vs_stability": {
        "strengths": [
            "Чутьё на оба полюса — свободу и опору — как живую ось характера.",
            "Способность видеть цену любого крайнего выбора.",
            "Гибкость между движением и укоренением.",
        ],
        "growth_zones": [
            "Не держать напряжение вместо явного выбора на этот этап.",
            "Перестать тратить силу на удержание обоих полюсов сразу.",
            "Называть, какой полюс сейчас ведущий.",
        ],
        "helps": [
            "Выбери на эту неделю: больше свободы или больше опоры — явно.",
            "Сними одно обязательство, которое держит оба полюса в тупике.",
        ],
        "decision_style": (
            "Ты решаешь между свободой и опорой — и часто слышишь оба голоса. "
            "Сила — в честном выборе на этап; риск — вечный компромисс без движения."
        ),
        "relationship_style": (
            "В близости тебе нужны и воздух, и надёжность. "
            "Связь работает, когда вы договариваетесь о ритме, а не тянете молча в разные стороны."
        ),
        "money_style": (
            "Деньги отражают ту же ось: свобода манёвра против прочного основания. "
            "Ясный приоритет на сезон снимает лишнее напряжение."
        ),
    },
    "builds_through_fire_drive": {
        "strengths": [
            "Импульс к действию — ты зажигаешь движение.",
            "Смелость начинать без полного согласия окружения.",
            "Энергия, которая собирает других вокруг живого старта.",
        ],
        "growth_zones": [
            "Давать импульсу направление, а не только скорость.",
            "Доводить начатое после первого огня.",
            "Слышать тело и паузу рядом с напором.",
        ],
        "helps": [
            "Назови цель импульса одним предложением — и сделай первый шаг.",
            "Оставь один огонь, погаси остальные на сегодня.",
        ],
        "decision_style": (
            "Ты решаешь через искру: тело уже знает «да» раньше длинного разбора. "
            "Сила — в старте; риск — размазать энергию по многим фронтам."
        ),
        "relationship_style": (
            "В близости ты прям и горяч: контакт живой, когда есть взаимный отклик. "
            "Связь держится, если напор не подменяет устойчивое присутствие."
        ),
        "money_style": (
            "Деньги часто приходят через инициативу и риск. "
            "Импульс силён — структура после старта сохраняет результат."
        ),
    },
    "builds_through_air_presence": {
        "strengths": [
            "Лёгкий вход в контакт через слово и атмосферу.",
            "Умение разговорить поле и снять напряжение разговором.",
            "Гибкость первого впечатления.",
        ],
        "growth_zones": [
            "Не останавливаться на лёгкости, когда нужна глубина.",
            "Доводить контакт до явного «мы».",
            "Замечать, когда разговор заменяет решение.",
        ],
        "helps": [
            "После лёгкого контакта сделай один конкретный следующий шаг вместе.",
            "Скажи прямо, чего хочешь от связи — коротко.",
        ],
        "decision_style": (
            "Ты решаешь в разговоре и обмене: ясность приходит, когда мысль проговорена. "
            "Сила — в воздухе контакта; риск — растворить выбор в беседе."
        ),
        "relationship_style": (
            "Близость начинается с лёгкости и интереса. "
            "Глубина появляется, когда ты остаёшься после первого обмена."
        ),
        "money_style": (
            "Финансы связаны с сетью, переговорами и гибкими форматами. "
            "Ясная договорённость важнее бесконечного обсуждения."
        ),
    },
    "builds_through_fire_presence": {
        "strengths": [
            "Прямой вход — тебя сразу видно и слышно.",
            "Способность задавать температуру поля.",
            "Честность первого контакта без долгих прелюдий.",
        ],
        "growth_zones": [
            "Не путать силу входа с устойчивым пространством.",
            "Оставлять место для ответа другого.",
            "Мягче дозировать напор в близких зонах.",
        ],
        "helps": [
            "Войди прямо — и дай паузу на отклик.",
            "Спроси, как другой переносит твой темп.",
        ],
        "decision_style": (
            "Ты решаешь в контакте: решение часто рождается в живом столкновении. "
            "Сила — в прямом входе; риск — продавить вместо согласовать."
        ),
        "relationship_style": (
            "В близости ты зажигаешь поле сразу. "
            "Связь держится, когда жар становится теплом, а не только вспышкой."
        ),
        "money_style": (
            "Деньги могут идти через видимость, инициативу и смелый заход. "
            "После яркого старта нужна рамка, иначе поток рассеивается."
        ),
    },
    "builds_through_earth_presence": {
        "strengths": [
            "Плотная, читаемая форма — на тебя можно опереться с первого контакта.",
            "Спокойная телесная присутственность.",
            "Умение держать рамку без лишнего шума.",
        ],
        "growth_zones": [
            "Пускать живое движение из-под надёжной оболочки.",
            "Не прятать желание за «правильной» формой.",
            "Показывать уязвимость без потери опоры.",
        ],
        "helps": [
            "Покажи один живой жест поверх привычной формы.",
            "Скажи желание прямо, не только через дела.",
        ],
        "decision_style": (
            "Ты решаешь через ощущение прочности формы: что выглядит цельно и выдерживает. "
            "Сила — в присутствии; риск — застыть в правильной оболочке."
        ),
        "relationship_style": (
            "В близости ты даёшь опору и плотность. "
            "Связь оживает, когда форма пропускает тепло, а не только надёжность."
        ),
        "money_style": (
            "К деньгам — через осязаемый результат и понятную форму обмена. "
            "Ты спокойнее, когда ценность видна и измерима."
        ),
    },
    "builds_through_water_presence": {
        "strengths": [
            "Чуткий вход — ты считываешь поле раньше слов.",
            "Мягкая оболочка, в которой другим безопасно.",
            "Тонкое присутствие без давления.",
        ],
        "growth_zones": [
            "Называть свои желания так же ясно, как чужие.",
            "Не растворяться в атмосфере комнаты.",
            "Держать контур «я» в мягком контакте.",
        ],
        "helps": [
            "Произнеси одно своё желание до настройки на других.",
            "Отметь границу мягко, но вслух.",
        ],
        "decision_style": (
            "Ты решаешь через атмосферу и тон: что сохраняет бережность поля. "
            "Сила — в чуткости; риск — не назвать собственный вектор."
        ),
        "relationship_style": (
            "Близость для тебя — тонкое совместное поле. "
            "Связь крепнет, когда мягкость не отменяет твои желания."
        ),
        "money_style": (
            "Деньги связаны с доверием и ощущением безопасности обмена. "
            "Ясные условия защищают чуткость от размытых ожиданий."
        ),
    },
}

_CLAIM_WHY_LABEL: dict[str, str] = {
    "autonomy_high": "Автономия — главный механизм ядра",
    "analysis_before_action": "Сначала анализ, потом шаг — рабочий механизм ядра",
    "direction_through_air_mind": "Путь через идеи и связи задаёт направление ядра",
    "stability_through_earth": "Опора на осязаемое и прочное держит ядро",
    "care_through_water_sun": "Забота и проницаемость — способ строить мир",
    "emotional_sensitivity_high": "Эмоциональная глубина окрашивает ядро",
    "anchor_through_earth_moon": "Земная луна якорит ритм и даёт устойчивость",
    "freedom_vs_stability": "Напряжение свободы и опоры — ось характера",
    "drive_through_fire_mars": "Огненный марс усиливает импульс действия",
    "presence_through_air_asc": "Воздушный ASC задаёт способ первого контакта",
    "presence_through_fire_asc": "Огненный ASC задаёт способ первого контакта",
    "presence_through_earth_asc": "Земной ASC задаёт способ первого контакта",
    "presence_through_water_asc": "Водный ASC задаёт способ первого контакта",
}

_RECOGNITION_LABEL: dict[str, str] = {
    "builds_through_autonomy": "Автономия",
    "builds_through_analysis": "Анализ",
    "builds_through_air_mind": "Исследователь идей",
    "builds_through_earth_stability": "Опора",
    "builds_through_water_care": "Забота",
    "builds_through_emotional_depth": "Глубина",
    "builds_through_earth_anchor": "Якорь",
    "builds_through_freedom_vs_stability": "Свобода и опора",
    "builds_through_fire_drive": "Импульс",
    "builds_through_air_presence": "Лёгкий контакт",
    "builds_through_fire_presence": "Прямой вход",
    "builds_through_earth_presence": "Плотная форма",
    "builds_through_water_presence": "Чуткий вход",
}


def character_engine_profile_consumption_enabled() -> bool:
    return bool(getattr(settings, "character_engine_profile_consumption", False))


def _clip(text: str, limit: int) -> str:
    t = re.sub(r"\s+", " ", str(text or "").strip())
    if len(t) <= limit:
        return t
    return t[: max(0, limit - 1)].rstrip() + "…"


def _scrub_machine_thesis(text: str, identity_thesis: str | None = None) -> str:
    """Never ship builds_through_* machine ids in person-facing copy."""
    raw = str(text or "")
    if not raw:
        return raw
    label = _RECOGNITION_LABEL.get(str(identity_thesis or "").strip()) or "ядро"
    out = raw
    thesis = str(identity_thesis or "").strip()
    if thesis and thesis in out:
        out = out.replace(thesis, label)
    out = re.sub(r"builds_through_[a-z0-9_]+", label, out)
    return out


def _clip_person(text: str, limit: int, *, identity_thesis: str | None = None) -> str:
    return _clip(_scrub_machine_thesis(text, identity_thesis), limit)


def _fact_label(fact: dict[str, Any]) -> str | None:
    ft = str(fact.get("fact_type") or "")
    value = fact.get("value")
    sign = None
    if isinstance(value, dict):
        sign = str(value.get("sign") or "").strip()
    elif value is not None and ft.startswith("life_path"):
        return f"число пути {value}"
    if not sign:
        return None
    sign_ru = sign[:1].upper() + sign[1:].lower() if sign else sign
    if ft == "planet_sign:sun":
        return f"Солнце в {sign_ru}"
    if ft == "planet_sign:moon":
        return f"Луна в {sign_ru}"
    if ft == "angle_sign:ascendant":
        return f"ASC в {sign_ru}"
    if ft == "planet_sign:mars":
        return f"Марс в {sign_ru}"
    if ft.startswith("planet_sign:"):
        body = ft.split(":", 1)[-1]
        return f"{body} в {sign_ru}"
    return None


def _stage2_artifact(payload: dict[str, Any]) -> dict[str, Any] | None:
    diagnostics = payload.get("diagnostics")
    if not isinstance(diagnostics, dict):
        return None
    art = diagnostics.get("character_engine_stage2")
    if isinstance(art, dict) and art.get("stage2"):
        return art
    return art if isinstance(art, dict) and (art.get("stage2") or art.get("identity_core")) else None


def _stage3_internal(payload: dict[str, Any]) -> dict[str, Any] | None:
    diagnostics = payload.get("diagnostics")
    if not isinstance(diagnostics, dict):
        return None
    art = diagnostics.get("character_engine_stage3")
    if not isinstance(art, dict):
        return None
    stage3 = art.get("stage3") if isinstance(art.get("stage3"), dict) else art
    if str(stage3.get("status") or "") != "grounded":
        return None
    return stage3


def _stage4_life(payload: dict[str, Any]) -> dict[str, Any] | None:
    diagnostics = payload.get("diagnostics")
    if not isinstance(diagnostics, dict):
        return None
    art = diagnostics.get("character_engine_stage4")
    if not isinstance(art, dict):
        return None
    stage4 = art.get("stage4") if isinstance(art.get("stage4"), dict) else art
    if str(stage4.get("status") or "") != "grounded":
        return None
    return stage4


def _stage5_assembly(payload: dict[str, Any]) -> dict[str, Any] | None:
    diagnostics = payload.get("diagnostics")
    if not isinstance(diagnostics, dict):
        return None
    art = diagnostics.get("character_engine_stage5")
    if not isinstance(art, dict):
        return None
    stage5 = art.get("stage5") if isinstance(art.get("stage5"), dict) else art
    if str(stage5.get("status") or "") != "grounded":
        return None
    return stage5


def _adapter_value(stage5: dict[str, Any], field: str) -> Any:
    legacy = stage5.get("legacy_map") if isinstance(stage5.get("legacy_map"), dict) else {}
    fields = legacy.get("fields") if isinstance(legacy.get("fields"), dict) else {}
    row = fields.get(field) if isinstance(fields.get(field), dict) else None
    if not row:
        return None
    val = row.get("value")
    if val is None or val == "" or val == []:
        return None
    return val


def _scene_by_kind(stage4: dict[str, Any], *kinds: str) -> str | None:
    scenes = stage4.get("scenes") if isinstance(stage4.get("scenes"), list) else []
    for want in kinds:
        for sc in scenes:
            if isinstance(sc, dict) and str(sc.get("scene_kind") or "") == want:
                text = str(sc.get("surface_text") or "").strip()
                if text:
                    return text
    return None


def _essays_for(identity_thesis: str) -> dict[str, Any]:
    pack = _ESSAYS_BY_IDENTITY.get(identity_thesis)
    if isinstance(pack, dict):
        return pack
    # Generic fallback — still CE-owned, still «ты».
    return {
        "strengths": [
            "Ты держишь ясный внутренний механизм — это опора характера.",
            "Способность видеть свою линию среди чужих ожиданий.",
        ],
        "growth_zones": [
            "Переводить ядро характера в явный выбор, а не только в понимание.",
            "Замечать, где сила механизма становится отсрочкой жизни.",
        ],
        "helps": [
            "Сделай один шаг из ядра — маленький, но названный.",
        ],
        "decision_style": (
            "Ты решаешь из своего ядра характера: сначала внутренняя ясность, потом внешняя форма."
        ),
        "relationship_style": (
            "В близости тебе важно, чтобы связь не стирала твой основной механизм — "
            "а давала ему место рядом с другим."
        ),
        "money_style": (
            "Деньги для тебя — продолжение того же ядра: ресурс под твой способ строить жизнь."
        ),
    }


def apply_character_engine_profile_consumption_v0(payload: dict[str, Any]) -> dict[str, Any]:
    """Overwrite Profile journey + character slots from CE Identity Core + evidence."""
    if not character_engine_profile_consumption_enabled():
        return payload
    if not isinstance(payload, dict):
        return payload

    art = _stage2_artifact(payload)
    if not isinstance(art, dict):
        return payload

    stage2 = art.get("stage2") if isinstance(art.get("stage2"), dict) else art
    stage1 = art.get("stage1") if isinstance(art.get("stage1"), dict) else {}
    stage0 = art.get("stage0") if isinstance(art.get("stage0"), dict) else {}
    if str(stage2.get("status") or "") != "grounded":
        payload["character_engine_consumption_v0"] = {
            "projection_version": PROJECTION_VERSION,
            "applied": False,
            "reason": "identity_core_not_grounded",
            "status": stage2.get("status"),
        }
        return payload

    core = stage2.get("identity_core") if isinstance(stage2.get("identity_core"), dict) else None
    if not core:
        return payload

    surface = _clip(str(core.get("surface_text") or ""), _MAX_CORE)
    identity_thesis = str(core.get("thesis_key") or "").strip()
    if not surface or not identity_thesis:
        return payload

    recognition = _clip(surface, _MAX_RECOGNITION)
    stage3 = _stage3_internal(payload)
    stage4 = _stage4_life(payload)
    stage5 = _stage5_assembly(payload)
    trap_source = "editorial_bank"
    decision_source = "editorial_bank"
    relationship_source = "editorial_bank"
    money_source = "editorial_bank"
    growth_source = "editorial_bank"
    trap = _TRAP_BY_IDENTITY_THESIS.get(identity_thesis) or (
        "Пока ядро характера не переводится в выбор, сила уходит в удержание формы вместо движения."
    )
    if isinstance(stage3, dict):
        pt = stage3.get("primary_tension") if isinstance(stage3.get("primary_tension"), dict) else None
        pt_text = str((pt or {}).get("surface_text") or "").strip()
        if pt_text:
            trap = pt_text
            trap_source = "stage3_primary_tension"
    trap = _clip(trap, _MAX_TRAP)
    essays = _essays_for(identity_thesis)
    strengths = [str(x).strip() for x in (essays.get("strengths") or []) if str(x).strip()][:4]
    growth = [str(x).strip() for x in (essays.get("growth_zones") or []) if str(x).strip()][:3]
    helps = [str(x).strip() for x in (essays.get("helps") or []) if str(x).strip()][:3]
    decision = _clip(str(essays.get("decision_style") or ""), _MAX_ESSAY)
    if isinstance(stage3, dict):
        engine = stage3.get("internal_engine") if isinstance(stage3.get("internal_engine"), dict) else {}
        dec = engine.get("decision") if isinstance(engine.get("decision"), dict) else None
        dec_text = str((dec or {}).get("surface_text") or "").strip()
        if dec_text:
            decision = _clip(dec_text, _MAX_ESSAY)
            decision_source = "stage3_internal_engine.decision"
        growth_slot = engine.get("growth") if isinstance(engine.get("growth"), dict) else None
        recovery_slot = engine.get("recovery") if isinstance(engine.get("recovery"), dict) else None
        stage3_helps: list[str] = []
        for slot in (growth_slot, recovery_slot):
            t = str((slot or {}).get("surface_text") or "").strip()
            if t:
                stage3_helps.append(_clip(t, _MAX_ESSAY))
        if stage3_helps:
            helps = stage3_helps[:3]
    relationship = _clip(str(essays.get("relationship_style") or ""), _MAX_ESSAY)
    money = _clip(str(essays.get("money_style") or ""), _MAX_ESSAY)
    if isinstance(stage4, dict):
        intimacy = _scene_by_kind(stage4, "intimacy")
        if intimacy:
            relationship = _clip(intimacy, _MAX_ESSAY)
            relationship_source = "stage4_scene.intimacy"
        money_scene = _scene_by_kind(stage4, "risk", "responsibility", "uncertainty")
        if money_scene:
            money = _clip(money_scene, _MAX_ESSAY)
            money_source = "stage4_scene.resource_proxy"
        pot = stage4.get("potential") if isinstance(stage4.get("potential"), dict) else None
        pot_text = str((pot or {}).get("surface_text") or "").strip()
        if pot_text:
            pot_clean = _clip_person(pot_text, _MAX_ESSAY, identity_thesis=identity_thesis)
            growth = [pot_clean, *growth][:3]
            growth_source = "stage4_potential"
            helps = [pot_clean, *helps][:3]
    # Stage 5 adapters preferred; when character_engine_v1.status=ready, SoT is the envelope.
    ce_root = payload.get("character_engine_v1") if isinstance(payload.get("character_engine_v1"), dict) else {}
    ce_sot = str(ce_root.get("status") or "") == "ready"
    if isinstance(stage5, dict):
        a_dec = _adapter_value(stage5, "decision_style")
        if isinstance(a_dec, str) and a_dec.strip():
            decision = _clip(a_dec, _MAX_ESSAY)
            decision_source = "character_engine_v1.legacy_map.decision_style" if ce_sot else "stage5_legacy_map.decision_style"
        a_rel = _adapter_value(stage5, "relationship_style")
        if isinstance(a_rel, str) and a_rel.strip():
            relationship = _clip(a_rel, _MAX_ESSAY)
            relationship_source = "stage5_legacy_map.relationship_style"
        a_money = _adapter_value(stage5, "money_patterns")
        if isinstance(a_money, str) and a_money.strip():
            money = _clip(a_money, _MAX_ESSAY)
            money_source = "stage5_legacy_map.money_patterns"
        a_growth = _adapter_value(stage5, "growth_zones")
        if isinstance(a_growth, list) and a_growth:
            growth = [_clip(str(x), _MAX_ESSAY) for x in a_growth if str(x).strip()][:3]
            growth_source = "stage5_legacy_map.growth_zones"
        a_helps = _adapter_value(stage5, "helps")
        if isinstance(a_helps, list) and a_helps:
            helps = [_clip(str(x), _MAX_ESSAY) for x in a_helps if str(x).strip()][:3]
        a_trap = _adapter_value(stage5, "recurring_patterns")
        if isinstance(a_trap, list) and a_trap and str(a_trap[0]).strip():
            trap = _clip(str(a_trap[0]), _MAX_TRAP)
            trap_source = "stage5_legacy_map.recurring_patterns"
        a_strengths = _adapter_value(stage5, "strengths")
        if isinstance(a_strengths, list) and a_strengths:
            strengths = [_clip(str(x), _MAX_ESSAY) for x in a_strengths if str(x).strip()][:4]
    help_line = _scrub_machine_thesis(helps[0], identity_thesis) if helps else None
    if help_line:
        helps = [_scrub_machine_thesis(h, identity_thesis) for h in helps]
    growth = [_scrub_machine_thesis(g, identity_thesis) for g in growth]
    trap = _scrub_machine_thesis(trap, identity_thesis)
    decision = _scrub_machine_thesis(decision, identity_thesis)
    relationship = _scrub_machine_thesis(relationship, identity_thesis)
    money = _scrub_machine_thesis(money, identity_thesis)
    strengths = [_scrub_machine_thesis(s, identity_thesis) for s in strengths]

    claims = stage1.get("claims") if isinstance(stage1.get("claims"), list) else []
    facts_by_id = {
        str(f.get("fact_id")): f
        for f in (stage0.get("raw_facts") or [])
        if isinstance(f, dict) and f.get("fact_id")
    }
    primary_id = str(core.get("primary_claim_id") or "")
    selected_by: list[dict[str, Any]] = []
    influenced_by: list[dict[str, Any]] = []

    for c in claims:
        if not isinstance(c, dict) or not c.get("thesis_key"):
            continue
        thesis = str(c.get("thesis_key"))
        label = _CLAIM_WHY_LABEL.get(thesis) or thesis
        fact_bits: list[str] = []
        for fid in c.get("supporting_fact_ids") or []:
            fl = _fact_label(facts_by_id.get(str(fid)) or {})
            if fl:
                fact_bits.append(fl)
        detail = "; ".join(fact_bits[:3])
        row = {
            "id": f"ce_claim:{thesis}",
            "class": "selected_by" if str(c.get("claim_id")) == primary_id else "portrait_influenced_by",
            "fact_keys": [f"character_engine.claim:{thesis}"],
            "label": f"{label} — {detail}" if detail else label,
            "thesis_key": thesis,
            "claim_id": c.get("claim_id"),
        }
        if row["class"] == "selected_by":
            selected_by.append(row)
        else:
            influenced_by.append(row)

    selected_by.sort(key=lambda r: 0 if r.get("claim_id") == primary_id else 1)

    contract = payload.get("profile_contract_v1")
    if not isinstance(contract, dict):
        contract = {}
    else:
        contract = dict(contract)

    contract["identity_core"] = surface
    contract["recognition_line"] = recognition
    contract["recurring_patterns"] = [trap]
    contract["strengths"] = strengths
    contract["growth_zones"] = growth
    contract["helps"] = helps
    contract["decision_style"] = decision
    contract["relationship_style"] = relationship
    contract["money_style"] = money
    # Living day-rhythm is not identity «что уже меняется».
    contract["living_changes"] = None
    payload["profile_contract_v1"] = contract

    from todayflow_backend.services.character_engine_profile_consumption_spheres_houses_v0 import (
        apply_spheres_and_houses_to_payload,
    )

    apply_spheres_and_houses_to_payload(payload, identity_thesis=identity_thesis)

    payload["portrait_why_v0"] = {
        "projection_version": f"{PROJECTION_VERSION}.why",
        "title": "Почему портрет звучит именно так",
        "selected_by": selected_by[:1],
        "portrait_influenced_by": influenced_by[:5],
        "honesty_line": (
            "Ядро собрано из Character Engine: один механизм личности и факты, "
            "которые его держат — не список ярлыков и не ритм дня."
        ),
        "source": "character_engine_stage2",
    }

    grounded_on: list[dict[str, Any]] = []
    for row in selected_by[:1] + influenced_by[:3]:
        grounded_on.append(
            {
                "id": row.get("id"),
                "label": row.get("label"),
                "fact_keys": list(row.get("fact_keys") or []),
                "role": "grounded_on",
            }
        )

    payload["insight_nodes_v0"] = {
        "projection_version": f"{PROJECTION_VERSION}.insight",
        "nodes": [
            {
                "id": "node_ce_trap_0",
                "kind": "tension",
                "title": "Самая большая ловушка",
                "insight": trap,
                "grounded_on": grounded_on,
                "help": help_line,
                "source_fields": [
                    "character_engine_stage2.identity_core",
                    "character_engine_stage1.claims",
                    "character_engine_stage3.primary_tension",
                ],
            }
        ],
        "rules": {
            "source": "character_engine_identity_core",
            "trap_source": trap_source,
            "forbids_living_day_rhythm_as_identity_trap": True,
            "snapshot_materials_may_differ": True,
        },
    }

    payload["character_engine_consumption_v0"] = {
        "projection_version": PROJECTION_VERSION,
        "applied": True,
        "identity_thesis": identity_thesis,
        "recognition_label": _RECOGNITION_LABEL.get(identity_thesis) or "Ядро",
        "primary_claim_id": primary_id,
        "trap_source": trap_source,
        "decision_source": decision_source,
        "relationship_source": relationship_source,
        "money_source": money_source,
        "growth_source": growth_source,
        "stage3_status": (stage3 or {}).get("status") if isinstance(stage3, dict) else None,
        "stage4_status": (stage4 or {}).get("status") if isinstance(stage4, dict) else None,
        "stage5_status": (stage5 or {}).get("status") if isinstance(stage5, dict) else None,
        "visual_note": "archetype_seed remains FE illustration only; recognition title is CE",
        "slots_owned": [
            "profile_contract_v1.identity_core",
            "profile_contract_v1.recognition_line",
            "profile_contract_v1.recurring_patterns",
            "profile_contract_v1.strengths",
            "profile_contract_v1.growth_zones",
            "profile_contract_v1.helps",
            "profile_contract_v1.decision_style",
            "profile_contract_v1.relationship_style",
            "profile_contract_v1.money_style",
            "profile_contract_v1.living_changes",
            "profile_contract_v1.life_spheres",
            "profile_contract_v1.emotional_style",
            "profile_contract_v1.work_and_realization",
            "profile_contract_v1.home_and_security",
            "character_engine_house_lines_v0",
            "character_engine_aspect_lines_v0",
            "natal_summary.notable_aspects.gist",
            "portrait_why_v0",
            "insight_nodes_v0",
        ],
        "slots_not_owned_yet": [
            "natal_instrument_facts",
        ],
    }
    return payload
