"""Character Engine → Profile consumption slice v0.

Architecture: Identity Core (+ Stage 1 evidence + Stage 3 Internal Engine when grounded)
become SoT for Profile journey and character slots. Natal instrument (wheel / houses /
aspects) stays Swiss facts. Archetype illustration seed remains FE visual only —
not recognition title SoT.

Owned when Stage 2 grounded + flag on:
  - recognition / identity_core
  - portrait_why
  - insight — Stage 1 grounded aspect_pair (K05); omit without F07. Trap bank / Stage3 identity tension cannot fill.
  - help — PIC-K04 one Internal Engine axis from F08 / harmonic F07 when grounded; else omit. Not seven widgets.
  - honest cost — PIC-K09 fill-empty into the same P3 node from K04+K05 excess; omit without grounded pair. No trap-bank / Stage4 LLM.
  - K06 secondary tensions — PIC OMIT-BY-DESIGN on the path. Stay in N / Explore schema. Do not copy into insight, help, effort, or spheres.
  - path spheres — PIC-K07 ≤2 from grounded F06 house arena of K01/K04/K05 bodies; omit without full natal / link. Not a relationships/career/money root.
  - Compass — PIC-K10 derived-only: `helps` = grounded K04 line or omit. No essay / Stage3 / Stage4 / Stage5 fill of emptiness. Strengths / growth / energy / red flags have no independent generative root. Do not mint help to keep K07 spheres visible.
  - decision_style — Stage 3 internal_engine.decision when grounded, else editorial bank
  - relationship_style / money_style
  - recurring_patterns — editorial / Stage5 (not K05)
  - clears living_changes day-rhythm leak

Not owned yet: natal cusp/sign/degree facts stay Swiss.
"""

from __future__ import annotations

import re
from typing import Any

from todayflow_backend.core.config import settings

# PIC: docs/profile/PROFILE_INFORMATION_CONTRACT_V1.md
PIC_K = ("K01", "K02", "K04", "K05", "K06", "K07", "K09", "K10", "K12")
PIC_F = ("F01", "F03", "F04", "F05", "F06", "F07", "F08", "F09")

PROJECTION_VERSION = "character_engine_profile_consumption_v0.14"
# Soft ceilings only — clip_prose prefers sentence end; never mid-word stumps for UI.
_MAX_RECOGNITION = 900
_MAX_CORE = 900
_MAX_TRAP = 900
_MAX_ESSAY = 480

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
            "Сделать один явный выбор — без полного согласования со всеми.",
            "Назвать границу вслух: что ты оставляешь своим, а что открываешь.",
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
            "Спросить себя, чего хочешь ты — до ответа «чем помочь».",
            "Поставить одну мягкую, но явную границу.",
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
            "Назвать цель импульса одним предложением — и сделать первый шаг.",
            "Оставить один огонь — погасить остальные.",
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
    "autonomy_high": "Автономия",
    "analysis_before_action": "Сначала понять — потом шаг",
    "direction_through_air_mind": "Путь через идеи и связи",
    "stability_through_earth": "Опора на осязаемое и прочное",
    "care_through_water_sun": "Забота и проницаемость",
    "emotional_sensitivity_high": "Эмоциональная глубина",
    "anchor_through_earth_moon": "Земной якорь ритма",
    "freedom_vs_stability": "Свобода и опора рядом",
    "drive_through_fire_mars": "Огненный импульс действия",
    "presence_through_air_asc": "Первый контакт через вопросы, разговор и лёгкую дистанцию",
    "presence_through_fire_asc": "Первый контакт через прямой заход и тепло",
    "presence_through_earth_asc": "Первый контакт через плотный спокойный темп",
    "presence_through_water_asc": "Первый контакт через чуткость поля",
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
    from todayflow_backend.services.prose_clip_v1 import clip_prose

    t = re.sub(r"\s+", " ", str(text or "").strip())
    return clip_prose(t, limit)


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


# Profile journey forbids day agenda in Act 3–4 helps (Forms + PROFILE_V2 lexicon).
_DAY_AGENDA_RE = re.compile(r"\b(сегодня|завтра|на сегодня)\b", re.I)
_KITCHEN_HELP_RE = re.compile(
    r"механизм проявляется|identity-линии|builds_through_|зоне\s*«?(decision|perception|stress|risk|recovery|growth|burnout)»?",
    re.I,
)


def _scrub_day_agenda(text: str) -> str | None:
    """Drop or soften day-agenda tokens; null if the line collapses."""
    t = re.sub(r"\s+", " ", str(text or "").strip())
    if not t:
        return None
    if _KITCHEN_HELP_RE.search(t):
        return None
    if not _DAY_AGENDA_RE.search(t):
        return t
    cleaned = _DAY_AGENDA_RE.sub("", t)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = re.sub(r"\s+([,.—–-])", r"\1", cleaned).strip(" ,.—–-")
    if len(cleaned) < 12 or _DAY_AGENDA_RE.search(cleaned):
        return None
    return cleaned


def _scrub_day_agenda_list(items: list[str]) -> list[str]:
    out: list[str] = []
    for item in items:
        scrubbed = _scrub_day_agenda(item)
        if scrubbed and scrubbed not in out:
            out.append(scrubbed)
    return out


def _clip_person(text: str, limit: int, *, identity_thesis: str | None = None) -> str:
    return _clip(_scrub_machine_thesis(text, identity_thesis), limit)


def _fact_label(fact: dict[str, Any]) -> str | None:
    from todayflow_backend.services.natal_chart_personalization import _sign_label_prepositional

    ft = str(fact.get("fact_type") or "")
    value = fact.get("value")
    sign = None
    if isinstance(value, dict):
        sign = str(value.get("sign") or "").strip()
    elif value is not None and ft.startswith("life_path"):
        return f"число пути {value}"
    if not sign:
        return None
    prep = _sign_label_prepositional(sign)
    if not prep:
        return None
    if ft == "planet_sign:sun":
        return f"Солнце в {prep}"
    if ft == "planet_sign:moon":
        return f"Луна в {prep}"
    if ft == "angle_sign:ascendant":
        return f"Асцендент в {prep}"
    if ft == "angle_sign:midheaven":
        return f"Середина неба в {prep}"
    if ft == "planet_sign:mars":
        return f"Марс в {prep}"
    if ft.startswith("planet_sign:"):
        body = ft.split(":", 1)[-1]
        body_ru = {
            "mercury": "Меркурий",
            "venus": "Венера",
            "jupiter": "Юпитер",
            "saturn": "Сатурн",
        }.get(body.lower(), body.capitalize() if body.isascii() else body)
        return f"{body_ru} в {prep}"
    return None


_NATAL_INFLUENCED_IDS = frozenset({"sun", "moon", "asc", "rising", "mc", "element", "rhythm"})


def _occupancy_thesis(thesis: str) -> bool:
    key = str(thesis or "").lower()
    return (
        key.startswith("planet_in_sign:")
        or key.startswith("planet_in_house:")
        or key.startswith("aspect_pair:")
    )


def _k05_insight(stage1: dict[str, Any]) -> tuple[str, str]:
    """P3.insight = one grounded hard aspect_pair. Trap-bank / Stage3 cannot beat it; else omit."""
    claims = stage1.get("claims") if isinstance(stage1.get("claims"), list) else []
    grounded: list[dict[str, Any]] = []
    for claim in claims:
        if not isinstance(claim, dict):
            continue
        if str(claim.get("evidence_status") or "grounded") != "grounded":
            continue
        if str(claim.get("claim_kind") or "") != "tension":
            continue
        thesis = str(claim.get("thesis_key") or "")
        if not thesis.startswith("aspect_pair:"):
            continue
        line = str(claim.get("il_line") or "").strip()
        if "↔" not in line:
            continue
        grounded.append(claim)
    if len(grounded) != 1:
        return "", "omitted_no_grounded_aspect_tension"
    line = str(grounded[0].get("il_line") or "").strip()
    return line, "stage1_aspect_pair"


def _k04_axis(
    stage0: dict[str, Any],
    stage3: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if isinstance(stage3, dict):
        axis = stage3.get("path_axis") if isinstance(stage3.get("path_axis"), dict) else None
        if isinstance(axis, dict) and str(axis.get("surface_text") or "").strip():
            return axis
    from todayflow_backend.services.character_engine_stage3_internal_v0 import (
        select_internal_engine_path_axis_v0,
    )

    axis = select_internal_engine_path_axis_v0(facts_pack=stage0)
    if isinstance(axis, dict) and str(axis.get("surface_text") or "").strip():
        return axis
    return None


def _k04_help(
    stage0: dict[str, Any],
    stage3: dict[str, Any] | None,
) -> tuple[str, str]:
    """P3.help = one Internal Engine axis from F08/harmonic F07. Identity thesis cannot beat it."""
    axis = _k04_axis(stage0, stage3)
    if not isinstance(axis, dict):
        return "", "omitted_no_grounded_engine_axis"
    line = str(axis.get("surface_text") or "").strip()
    if not line:
        return "", "omitted_no_grounded_engine_axis"
    return line, str(axis.get("source") or "stage0_element_balance")


def _k10_compass_helps(k04_line: str, k04_source: str) -> tuple[list[str], str | None, str]:
    """PIC-K10: Compass helps are the already-grounded K04 axis, or omit.

    Stage3 widgets, Stage4 potential, Stage5 adapters, and identity essays
    cannot fill emptiness. Do not mint a line so Inventory can show K07 spheres.
    """
    line = str(k04_line or "").strip()
    if not line:
        return [], None, "omitted_no_grounded_compass"
    return [line], line, k04_source


def _k09_honest_cost(
    *,
    axis: dict[str, Any] | None,
    insight: str,
    help_line: str,
) -> tuple[str, str]:
    """One honest cost inside P3. Requires grounded K04+K05. No trap-bank / LLM fill."""
    from todayflow_backend.services.character_engine_stage3_internal_v0 import (
        honest_cost_from_axis_v0,
    )

    cost = honest_cost_from_axis_v0(axis=axis, insight=insight, help_line=help_line)
    if not isinstance(cost, dict):
        return "", "omitted_no_grounded_honest_cost"
    line = str(cost.get("surface_text") or "").strip()
    if not line:
        return "", "omitted_no_grounded_honest_cost"
    return line, str(cost.get("source") or "sign_excess_of_k04_axis")


def _why_row_id(row: dict[str, Any]) -> str:
    rid = str(row.get("id") or "").strip()
    if rid == "rising":
        return "asc"
    return rid


def _natal_influenced_from_existing(existing: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    if not isinstance(existing, dict):
        return out
    for row in existing.get("portrait_influenced_by") or []:
        if not isinstance(row, dict):
            continue
        rid = _why_row_id(row)
        if rid in _NATAL_INFLUENCED_IDS and rid not in out:
            copied = dict(row)
            copied["id"] = rid
            out[rid] = copied
    return out


def _natal_influenced_from_facts(raw_facts: list[Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for fact in raw_facts:
        if not isinstance(fact, dict):
            continue
        ft = str(fact.get("fact_type") or "")
        label = _fact_label(fact)
        if not label:
            continue
        value = fact.get("value")
        sign = value.get("sign") if isinstance(value, dict) else None
        if ft == "planet_sign:sun":
            out.setdefault(
                "sun",
                {
                    "id": "sun",
                    "class": "portrait_influenced_by",
                    "fact_keys": ["astro.sun_sign"],
                    "value": sign,
                    "label": label,
                },
            )
        elif ft == "planet_sign:moon":
            out.setdefault(
                "moon",
                {
                    "id": "moon",
                    "class": "portrait_influenced_by",
                    "fact_keys": ["natal_summary.luminaries.moon"],
                    "value": sign,
                    "label": label,
                },
            )
        elif ft == "angle_sign:ascendant":
            out.setdefault(
                "asc",
                {
                    "id": "asc",
                    "class": "portrait_influenced_by",
                    "fact_keys": ["natal_summary.angles.ascendant_sign"],
                    "value": sign,
                    "label": label,
                },
            )
        elif ft == "angle_sign:midheaven":
            out.setdefault(
                "mc",
                {
                    "id": "mc",
                    "class": "portrait_influenced_by",
                    "fact_keys": ["natal_summary.angles.midheaven_sign"],
                    "value": sign,
                    "label": label,
                },
            )
    return out


def _life_path_anchor(
    existing: dict[str, Any] | None,
    raw_facts: list[Any],
    *,
    numerology: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    from todayflow_backend.services.profile_portrait_why_projection_v0 import life_path_k12_row

    value: Any = None
    birthday: Any = None
    num = numerology if isinstance(numerology, dict) else {}
    birthday = num.get("birthday_number")
    if num.get("life_path") is not None:
        value = num.get("life_path")
    for fact in raw_facts:
        if not isinstance(fact, dict):
            continue
        ft = str(fact.get("fact_type") or "")
        if ft in {"life_path_number", "life_path"} and fact.get("value") is not None:
            value = fact.get("value")
        if ft in {"birthday_number", "birthday"} and fact.get("value") is not None:
            birthday = fact.get("value")
    if value is None and isinstance(existing, dict):
        for row in existing.get("selected_by") or []:
            if isinstance(row, dict) and row.get("life_path") is not None:
                value = row.get("life_path")
                break
    return life_path_k12_row(value, birthday_number=birthday)


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


def _norm_slot(text: str) -> str:
    return " ".join(str(text or "").lower().split())


def _is_near_dupe(candidate: str, *forbidden: str) -> bool:
    """True if candidate equals or heavily overlaps a slot that already owns the meaning."""
    c = _norm_slot(candidate)
    if not c:
        return True
    for raw in forbidden:
        f = _norm_slot(raw)
        if not f:
            continue
        if c == f:
            return True
        if len(f) >= 40 and (f in c or c in f):
            return True
        # Trap paste into intimacy: "В близости это напряжение звучит так: …"
        if "напряжение звучит так" in c and f and f[:48] in c:
            return True
    return False


def _dedupe_list(items: list[str], *forbidden: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        t = str(item or "").strip()
        if not t or _is_near_dupe(t, *forbidden, *out):
            continue
        key = _norm_slot(t)
        if key in seen:
            continue
        seen.add(key)
        out.append(t)
    return out


def _essays_for(identity_thesis: str) -> dict[str, Any]:
    pack = _ESSAYS_BY_IDENTITY.get(identity_thesis)
    if isinstance(pack, dict):
        return pack
    # Generic fallback — still CE-owned, still «ты».
    return {
        "strengths": [
            "Ты держишь ясный внутренний контур — это опора характера.",
            "Способность видеть свою линию среди чужих ожиданий.",
        ],
        "growth_zones": [
            "Переводить ядро характера в явный выбор, а не только в понимание.",
            "Замечать, где сила контура становится отсрочкой жизни.",
        ],
        "helps": [
            "Сделай один шаг из ядра — маленький, но названный.",
        ],
        "decision_style": (
            "Ты решаешь из своего ядра характера: сначала внутренняя ясность, потом внешняя форма."
        ),
        "relationship_style": (
            "В близости тебе важно, чтобы связь не стирала твой основной способ быть — "
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

    recognition_raw = str(core.get("recognition_line") or "").strip()
    recognition = _clip(recognition_raw or surface, _MAX_RECOGNITION)
    k01_source = str(core.get("k01_source") or "").strip() or None
    stage3 = _stage3_internal(payload)
    stage4 = _stage4_life(payload)
    stage5 = _stage5_assembly(payload)
    trap_source = "editorial_bank"
    decision_source = "editorial_bank"
    relationship_source = "editorial_bank"
    money_source = "editorial_bank"
    growth_source = "omitted_no_grounded_compass"
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
    insight, insight_source = _k05_insight(stage1)
    insight = _clip(insight, _MAX_TRAP)
    # PIC-K06: leftover F07 / Stage3 secondary_tensions stay N for Explore.
    # Path M is OMIT-BY-DESIGN — P3 has no slot that can show them without
    # overloading K05 insight, minting a second node, or leaking into help/effort/spheres.
    k06_source = "omit_by_design"
    k04_axis = _k04_axis(stage0, stage3 if isinstance(stage3, dict) else None)
    k04_line, k04_source = _k04_help(stage0, stage3 if isinstance(stage3, dict) else None)
    k04_line = _clip(k04_line, _MAX_ESSAY)
    essays = _essays_for(identity_thesis)
    # PIC-K10: Compass (strengths / growth / helps) is derived-only from grounded K04.
    # Essays, Stage3 widgets, Stage4 potential, and Stage5 adapters cannot fill emptiness.
    strengths: list[str] = []
    growth: list[str] = []
    helps, help_line, help_source = _k10_compass_helps(k04_line, k04_source)
    decision = _clip(str(essays.get("decision_style") or ""), _MAX_ESSAY)
    if isinstance(stage3, dict):
        engine = stage3.get("internal_engine") if isinstance(stage3.get("internal_engine"), dict) else {}
        dec = engine.get("decision") if isinstance(engine.get("decision"), dict) else None
        dec_text = str((dec or {}).get("surface_text") or "").strip()
        if dec_text:
            decision = _clip(dec_text, _MAX_ESSAY)
            decision_source = "stage3_internal_engine.decision"
    essay_relationship = _clip(str(essays.get("relationship_style") or ""), _MAX_ESSAY)
    relationship = essay_relationship
    money = _clip(str(essays.get("money_style") or ""), _MAX_ESSAY)
    if isinstance(stage4, dict):
        intimacy = _scene_by_kind(stage4, "intimacy")
        if intimacy and not _is_near_dupe(intimacy, trap, surface):
            relationship = _clip(intimacy, _MAX_ESSAY)
            relationship_source = "stage4_scene.intimacy"
        money_scene = _scene_by_kind(stage4, "risk", "responsibility", "uncertainty")
        if money_scene and not _is_near_dupe(money_scene, trap, surface):
            money = _clip(money_scene, _MAX_ESSAY)
            money_source = "stage4_scene.resource_proxy"
    # Stage 5 adapters for Explore styles; Compass fields stay K10-derived.
    ce_root = payload.get("character_engine_v1") if isinstance(payload.get("character_engine_v1"), dict) else {}
    ce_sot = str(ce_root.get("status") or "") == "ready"
    if isinstance(stage5, dict):
        a_dec = _adapter_value(stage5, "decision_style")
        if isinstance(a_dec, str) and a_dec.strip() and not _is_near_dupe(a_dec, trap, surface):
            decision = _clip(a_dec, _MAX_ESSAY)
            decision_source = "character_engine_v1.legacy_map.decision_style" if ce_sot else "stage5_legacy_map.decision_style"
        a_rel = _adapter_value(stage5, "relationship_style")
        if isinstance(a_rel, str) and a_rel.strip() and not _is_near_dupe(a_rel, trap, surface):
            relationship = _clip(a_rel, _MAX_ESSAY)
            relationship_source = "stage5_legacy_map.relationship_style"
        a_money = _adapter_value(stage5, "money_patterns")
        if isinstance(a_money, str) and a_money.strip() and not _is_near_dupe(a_money, trap, surface):
            money = _clip(a_money, _MAX_ESSAY)
            money_source = "stage5_legacy_map.money_patterns"
        a_trap = _adapter_value(stage5, "recurring_patterns")
        if isinstance(a_trap, list) and a_trap and str(a_trap[0]).strip():
            trap = _clip(str(a_trap[0]), _MAX_TRAP)
            trap_source = "stage5_legacy_map.recurring_patterns"
    if _is_near_dupe(relationship, trap, surface):
        relationship = essay_relationship
        relationship_source = "editorial_bank"
    if help_line:
        scrubbed_help = _scrub_day_agenda(_scrub_machine_thesis(help_line, identity_thesis))
        help_line = scrubbed_help or None
        helps = [help_line] if help_line else []
        if not help_line:
            help_source = "omitted_no_grounded_compass"
    cost_line, cost_source = _k09_honest_cost(
        axis=k04_axis,
        insight=insight,
        help_line=k04_line,
    )
    if cost_line and insight:
        insight = f"{insight} {cost_line}".strip()
        insight = _clip(insight, _MAX_TRAP)
    trap = _scrub_machine_thesis(trap, identity_thesis)
    insight = _scrub_machine_thesis(insight, identity_thesis)
    decision = _scrub_machine_thesis(decision, identity_thesis)
    relationship = _scrub_machine_thesis(relationship, identity_thesis)
    money = _scrub_machine_thesis(money, identity_thesis)

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
        if _occupancy_thesis(thesis):
            continue
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

    existing_why = payload.get("portrait_why_v0") if isinstance(payload.get("portrait_why_v0"), dict) else {}
    raw_facts = [f for f in (stage0.get("raw_facts") or []) if isinstance(f, dict)]
    natal_influenced = {
        **_natal_influenced_from_facts(raw_facts),
        **_natal_influenced_from_existing(existing_why),
    }
    life_path_row = _life_path_anchor(
        existing_why,
        raw_facts,
        numerology=payload.get("numerology") if isinstance(payload.get("numerology"), dict) else None,
    )
    why_selected = [life_path_row] if life_path_row else []
    why_influenced = list(natal_influenced.values())
    seen_inf = {_why_row_id(r) for r in why_influenced}
    for row in influenced_by:
        rid = _why_row_id(row)
        if rid in seen_inf or _occupancy_thesis(str(row.get("thesis_key") or "")):
            continue
        why_influenced.append(row)
        seen_inf.add(rid)

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
        build_k07_path_spheres_v0,
    )

    apply_spheres_and_houses_to_payload(payload, identity_thesis=identity_thesis)
    spheres, sphere_source = build_k07_path_spheres_v0(
        stage0=stage0 if isinstance(stage0, dict) else {},
        stage1=stage1 if isinstance(stage1, dict) else {},
        k04_axis=k04_axis,
        k05_insight=insight,
    )
    contract = payload.get("profile_contract_v1")
    if isinstance(contract, dict):
        contract["life_spheres"] = spheres
        payload["profile_contract_v1"] = contract

    payload["portrait_why_v0"] = {
        "projection_version": f"{PROJECTION_VERSION}.why",
        "selected_by": why_selected,
        "portrait_influenced_by": why_influenced[:8],
        "source": "character_engine_stage2",
        "rules": {
            "natal_anchors_survive_ce": True,
            "occupancy_not_why_slot": True,
            "selected_life_path_is_f09_number_base": True,
        },
    }

    grounded_on: list[dict[str, Any]] = []
    seen_ground: set[str] = set()
    for row in selected_by[:1] + influenced_by[:5]:
        # Forms Step 3: fact anchors only (Солнце в …), not claim—fact mash / mechanism.
        raw_label = str(row.get("label") or "")
        facts_only: list[str] = []
        if " — " in raw_label or " – " in raw_label or " - " in raw_label:
            detail = re.split(r"\s+[—–-]\s+", raw_label, maxsplit=1)
            if len(detail) == 2:
                for part in re.split(r"\s*;\s*", detail[1]):
                    p = part.strip()
                    if p and p.lower() not in seen_ground:
                        facts_only.append(p)
                        seen_ground.add(p.lower())
        if not facts_only:
            # Claim without facts — skip (no kitchen claim title as «опора вывода»).
            continue
        for fl in facts_only[:2]:
            grounded_on.append(
                {
                    "id": row.get("id"),
                    "label": fl,
                    "fact_keys": list(row.get("fact_keys") or []),
                    "role": "grounded_on",
                }
            )
        if len(grounded_on) >= 4:
            break

    # Forms: birth-only → «Главное напряжение»; living quotes → «Самая большая ловушка».
    from todayflow_backend.services.profile_insight_nodes_projection_v0 import _living_quotes

    living_quotes = _living_quotes(
        payload.get("living") if isinstance(payload.get("living"), dict) else None
    )
    if living_quotes:
        node_kind = "repeat"
        node_title = "Самая большая ловушка"
        node_id = "node_ce_repeat_0"
    else:
        node_kind = "tension"
        node_title = "Главное напряжение"
        node_id = "node_ce_tension_0"
    node_source_fields = [
        "character_engine_stage2.identity_core",
        "character_engine_stage1.claims",
        "character_engine_stage3.primary_tension",
    ]
    ce_node: dict[str, Any] = {
        "id": node_id,
        "kind": node_kind,
        "title": node_title,
        "insight": insight,
        "grounded_on": grounded_on,
        "help": help_line,
        "source_fields": list(node_source_fields),
    }
    if living_quotes:
        ce_node["living_evidence"] = living_quotes
        ce_node["source_fields"] = [*node_source_fields, "living.signals.note"]

    payload["insight_nodes_v0"] = {
        "projection_version": f"{PROJECTION_VERSION}.insight",
        "nodes": [ce_node],
        "rules": {
            "source": "character_engine_identity_core",
            "trap_source": trap_source,
            "insight_source": insight_source,
            "help_source": help_source,
            "cost_source": cost_source,
            "k06_source": k06_source,
            "forbids_living_day_rhythm_as_identity_trap": True,
            "living_evidence_is_adjacent_context_not_proof": True,
            "titles_follow_forms_case_a_c": True,
            "snapshot_materials_may_differ": True,
        },
    }

    payload["character_engine_consumption_v0"] = {
        "projection_version": PROJECTION_VERSION,
        "applied": True,
        "identity_thesis": identity_thesis,
        "k01_source": k01_source,
        "recognition_label": _RECOGNITION_LABEL.get(identity_thesis) or "Ядро",
        "primary_claim_id": primary_id,
        "trap_source": trap_source,
        "insight_source": insight_source,
        "help_source": help_source,
        "cost_source": cost_source,
        "k06_source": k06_source,
        "sphere_source": sphere_source,
        "compass_source": help_source,
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
            "character_engine_asc_v0",
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
