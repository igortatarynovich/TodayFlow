"""CE consumption — life_spheres + applied ASC/house cards by Identity thesis.

Natal cusp/sign/degree stay Swiss. CE owns person-voice recognition theses.
Rules:
- Each house = one self-recognition sentence (house domain × cusp sign).
- No mechanism tint, no day-agenda «do», no planet-label dump in how.
- Emit ASC + MC + **all 12 houses**. Aspects keep Swiss/natal gists.
"""

from __future__ import annotations

from typing import Any

# Sphere IDs that Profile V2 contract builder accepts (full 6 fields required).
_SPHERE_IDS = ("love", "money", "decisions", "work", "family", "friends", "body")

_PERSONAL_PLANETS = frozenset({"Sun", "Moon", "Mercury", "Venus", "Mars"})

# Compact mechanism tag — used sparingly (not every line).
_MECH: dict[str, str] = {
    "builds_through_autonomy": "автономию и собственную систему",
    "builds_through_analysis": "анализ до шага",
    "builds_through_air_mind": "идеи и связи",
    "builds_through_earth_stability": "осязаемую опору",
    "builds_through_water_care": "заботу и проницаемость",
    "builds_through_emotional_depth": "эмоциональную глубину",
    "builds_through_earth_anchor": "привычный якорь и порядок",
    "builds_through_freedom_vs_stability": "ось свободы и опоры",
    "builds_through_fire_drive": "импульс действия",
    "builds_through_air_presence": "лёгкий контакт и разговор",
    "builds_through_fire_presence": "прямой вход",
    "builds_through_earth_presence": "плотную надёжную форму",
    "builds_through_water_presence": "чуткий вход",
}

_SIGN_RU: dict[str, str] = {
    "aries": "Овне",
    "taurus": "Тельце",
    "gemini": "Близнецах",
    "cancer": "Раке",
    "leo": "Льве",
    "virgo": "Деве",
    "libra": "Весах",
    "scorpio": "Скорпионе",
    "sagittarius": "Стрельце",
    "capricorn": "Козероге",
    "aquarius": "Водолее",
    "pisces": "Рыбах",
}

_SIGN_ELEMENT: dict[str, str] = {
    "aries": "fire",
    "taurus": "earth",
    "gemini": "air",
    "cancer": "water",
    "leo": "fire",
    "virgo": "earth",
    "libra": "air",
    "scorpio": "water",
    "sagittarius": "fire",
    "capricorn": "earth",
    "aquarius": "air",
    "pisces": "water",
}

# Cusp sign → lived modality (what others feel / how you move).
_SIGN_MODALITY: dict[str, str] = {
    "aries": "прямой старт без разведки",
    "taurus": "спокойная плотность и устойчивость",
    "gemini": "вопросы, варианты и лёгкая дистанция",
    "cancer": "сначала «свои», потом открытость",
    "leo": "тепло и право быть увиденным",
    "virgo": "точность деталей и проверка",
    "libra": "взаимность и баланс двоих",
    "scorpio": "дозированный доступ вглубь",
    "sagittarius": "смысл и широкий горизонт",
    "capricorn": "обязательства и статус",
    "aquarius": "дистанция идей и свой метод",
    "pisces": "эмпатия и мягкие границы",
}

_PLANET_RU: dict[str, str] = {
    "Sun": "Солнце",
    "Moon": "Луна",
    "Mercury": "Меркурий",
    "Venus": "Венера",
    "Mars": "Марс",
}

# House × cusp sign → one recognition sentence (person sees themselves).
# Degree/sign labels stay Swiss in UI; this is meaning only.
_HOUSE_SIGN_THESIS: dict[int, dict[str, str]] = {
    1: {
        "aries": "Входишь сразу и прямо — без долгой разведки.",
        "taurus": "В первом контакте держишь спокойный темп и плотность.",
        "gemini": "Сначала проверяешь людей, потом открываешься.",
        "cancer": "Сначала ищешь «своих» — чужим сразу не открываешься.",
        "leo": "В первом контакте тебе важно быть увиденным.",
        "virgo": "Сначала проверяешь детали — потом даёшь доступ.",
        "libra": "Входишь через взаимность: важно, как принимают тебя вдвоём.",
        "scorpio": "Доступ даёшь дозированно — не сразу вглубь.",
        "sagittarius": "В первом контакте говоришь про смысл и горизонт, не только про форму.",
        "capricorn": "Входишь серьёзно: сначала статус и правила, потом тепло.",
        "aquarius": "Держишь дистанцию идей: близость не равна сдаче метода.",
        "pisces": "Входишь мягко — сначала чуткость, потом правила.",
    },
    2: {
        "aries": "Деньги и навыки берёшь в свои руки — без чужих условий.",
        "taurus": "Своё копишь и бережёшь: устойчивость важнее эффекта.",
        "gemini": "Своё обсуждаешь редко — сначала варианты, потом обмен.",
        "cancer": "Свои деньги и навыки не отдаёшь и не обсуждаешь.",
        "leo": "Своё должно быть видно и оценено — иначе обесценивается.",
        "virgo": "Своё проверяешь и ведёшь точно — хаос в ресурсах бесит.",
        "libra": "В ресурсах ищешь честный обмен — не одностороннюю отдачу.",
        "scorpio": "Своё держишь под контролем доступа — не для всех.",
        "sagittarius": "Ресурсы должны служить смыслу, а не только запасу.",
        "capricorn": "Своё строишь через обязательства и статус — не через хаос.",
        "aquarius": "Деньги и навыки — рычаг своей системы, не чужой повестки.",
        "pisces": "Своё отдаёшь мягко — и легко теряешь границы ресурса.",
    },
    3: {
        "aries": "Говоришь прямо и быстро — без долгой подводки.",
        "taurus": "Говоришь спокойно и по делу — без лишнего шума.",
        "gemini": "Думаешь вслух через вопросы и варианты.",
        "cancer": "Открыто говоришь только с близкими.",
        "leo": "В разговоре тебе важно быть услышанным и замеченным.",
        "virgo": "В речи точность важнее красоты — проверяешь каждое слово.",
        "libra": "В общении ищешь баланс — чтобы никто не перетягивал.",
        "scorpio": "Говоришь мало, но вглубь — поверхностный треп не твой.",
        "sagittarius": "В словах нужен смысл и горизонт — не только факты.",
        "capricorn": "Речь держишь серьёзной: договорённости и статус важны.",
        "aquarius": "Общаешься через идеи и дистанцию — не через слияние.",
        "pisces": "Говоришь мягко и по настроению — тон важнее тезиса.",
    },
    4: {
        "aries": "Дома тебе нужен прямой старт — без чужих правил.",
        "taurus": "Дома держишь устойчивость и привычный ритм.",
        "gemini": "Дома тебе нужен воздух для разговора и вариантов.",
        "cancer": "Дома важно чувство «своих» и безопасность.",
        "leo": "Дома тебе важно, чтобы тебя видели и принимали.",
        "virgo": "Дома всё должно быть точно и в порядке — хаос выматывает.",
        "libra": "Дома важен баланс двоих — не тянуть всё на себе.",
        "scorpio": "Дома доступ дозируешь: приватность — не для всех.",
        "sagittarius": "Дома нужен смысл совместной жизни, не только быт.",
        "capricorn": "Дома важны обязательства и ясный порядок.",
        "aquarius": "Дома нужен воздух для своего метода — не клетка.",
        "pisces": "Дома восстанавливаешься через мягкость — или растворяешься.",
    },
    5: {
        "aries": "Ради себя действуешь импульсом — без долгого разрешения.",
        "taurus": "Ради себя выбираешь устойчивое удовольствие, не вспышку.",
        "gemini": "Ради себя нужны варианты и лёгкость — скука гасит игру.",
        "cancer": "Ради себя важно тепло «своих» и безопасная игра.",
        "leo": "Ради себя тебе важно быть увиденным и оценённым.",
        "virgo": "Даже отдыхая, ты всё проверяешь и делаешь точно.",
        "libra": "В игре ищешь взаимность — односторонняя отдача не радует.",
        "scorpio": "Играешь вглубь: доступ к себе дозируешь.",
        "sagittarius": "Ради себя нужен смысл и приключение, не только роль.",
        "capricorn": "Даже в игре держишь рамку и результат.",
        "aquarius": "Ради себя оставляешь свой метод — чужая сцена не заводит.",
        "pisces": "Ради себя нужна мягкая фантазия — жёсткая польза гасит.",
    },
    6: {
        "aries": "В быту стартуешь сам — долги бесят быстрее чужих норм.",
        "taurus": "В быту держишь устойчивый ритм тела и мелочей.",
        "gemini": "В быту крутишь варианты — один жёсткий режим душит.",
        "cancer": "В быту важна забота о «своих» и телесная безопасность.",
        "leo": "В быту хочешь, чтобы твой вклад замечали.",
        "virgo": "В быту всё проверяешь: мелочь без «готово» копится.",
        "libra": "В быту тебе важно равенство — не делать больше других.",
        "scorpio": "В быту контроль доступа к своему режиму — иначе выгораешь.",
        "sagittarius": "В быту нужен смысл рутины, не только чеклист.",
        "capricorn": "В быту держишь обязательства и статус «сделано».",
        "aquarius": "В быту свой метод важнее чужой эффективности.",
        "pisces": "В быту легко растворяешься в чужих нуждах.",
    },
    7: {
        "aries": "В отношениях идёшь прямо — без долгих намёков.",
        "taurus": "В отношениях нужна устойчивость и явные правила двоих.",
        "gemini": "В отношениях оставляешь пространство для вариантов и разговора.",
        "cancer": "В отношениях сначала безопасность «своих», потом открытость.",
        "leo": "В отношениях тебе важно быть увиденным партнёром.",
        "virgo": "В отношениях проверяешь детали договорённостей.",
        "libra": "В отношениях ищешь баланс — не тянуть всё на себе.",
        "scorpio": "В отношениях доступ дозируешь — слияние пугает.",
        "sagittarius": "В отношениях ты не растворяешься в партнёре.",
        "capricorn": "В отношениях важны обязательства и статус пары.",
        "aquarius": "В отношениях держишь свой контур — «мы» не стирает «я».",
        "pisces": "В отношениях легко растворяешься — границы мягкие.",
    },
    8: {
        "aries": "В уязвимости действуешь резко — контроль через напор.",
        "taurus": "В уязвимости цепляешься за устойчивость и запас.",
        "gemini": "В уязвимости уходишь в варианты и разговор вместо риска.",
        "cancer": "В уязвимости ищешь безопасность «своих».",
        "leo": "В уязвимости тебе важно не потерять лицо.",
        "virgo": "В уязвимости всё разбираешь и проверяешь.",
        "libra": "В уязвимости ищешь честный обмен — не скрытый долг.",
        "scorpio": "В уязвимости дозируешь доступ ещё жёстче.",
        "sagittarius": "В уязвимости ищешь смысл — иначе контроль пустой.",
        "capricorn": "Когда уязвим — начинаешь всё контролировать.",
        "aquarius": "В уязвимости уходишь в свой метод и дистанцию.",
        "pisces": "В уязвимости растворяешься или теряешь опору.",
    },
    9: {
        "aries": "Смысл берёшь действием — сначала шаг, потом философия.",
        "taurus": "Смысл строишь на устойчивых убеждениях и практике.",
        "gemini": "Смысл собираешь через вопросы, учёбу и связи идей.",
        "cancer": "Смысл ищешь через «своих» и безопасный горизонт.",
        "leo": "Смысл для тебя связан с видимостью и признанием пути.",
        "virgo": "Смысл проверяешь деталями — абстракция без опоры не держит.",
        "libra": "Смысл ищешь в балансе убеждений двоих.",
        "scorpio": "Смысл берёшь глубоко — поверхностные лозунги не работают.",
        "sagittarius": "Тебе нужен широкий горизонт — узкий план душит.",
        "capricorn": "Тебе нужен смысл происходящего, а не только план действий.",
        "aquarius": "Смысл — своя система взглядов, не чужая повестка.",
        "pisces": "Смысл чувствуешь — не всегда формулируешь.",
    },
    10: {
        "aries": "На работе берёшь инициативу — видимость через действие.",
        "taurus": "На работе важны устойчивость и проверяемый результат.",
        "gemini": "На работе сильнее через разговор, связи и варианты.",
        "cancer": "На работе нужна безопасность роли и «своих».",
        "leo": "На работе тебе важно быть увиденным.",
        "virgo": "На работе точность и проверка важнее шоу.",
        "libra": "На работе ищешь баланс вклада и признания.",
        "scorpio": "На работе доступ к власти дозируешь.",
        "sagittarius": "На работе нужен смысл роли, не только статус.",
        "capricorn": "На работе важны обязательства и проверяемый статус.",
        "aquarius": "На работе важнее делать по-своему, чем быть на виду.",
        "pisces": "На работе легко растворяешься в чужой роли.",
    },
    11: {
        "aries": "В круге идёшь к тем, с кем можно стартовать вместе.",
        "taurus": "В круге ищешь устойчивых людей, не случайный шум.",
        "gemini": "В круге важны идеи, разговор и лёгкие связи.",
        "cancer": "В круге оставляешь близких — остальным дистанцию.",
        "leo": "В круге тебе важно быть увиденным среди своих.",
        "virgo": "В круге выбираешь точно — не всех подряд.",
        "libra": "В круге ищешь взаимность, не одностороннюю поддержку.",
        "scorpio": "В круге доступ дозируешь — сеть не равна близости.",
        "sagittarius": "В круге нужен общий горизонт и смысл.",
        "capricorn": "В круге важны обязательства и ясный вектор.",
        "aquarius": "В круге свой метод важнее обязательной социальности.",
        "pisces": "Ты различаешь, кто тебе реально нужен, а кто просто знакомый.",
    },
    12: {
        "aries": "Наедине с собой ты либо отдыхаешь, либо теряешь опору.",
        "taurus": "Наедине восстанавливаешься через простой устойчивый ритм.",
        "gemini": "Наедине крутишь мысли и варианты — тишина может шуметь.",
        "cancer": "Наедине ищешь безопасность — иначе теряешь себя.",
        "leo": "Наедине тебе важно не исчезнуть без свидетелей.",
        "virgo": "Наедине всё разбираешь — отдых тоже с проверкой.",
        "libra": "Наедине нужен баланс паузы и контакта с собой.",
        "scorpio": "Наедине дозируешь доступ к себе даже без людей.",
        "sagittarius": "Наедине ищешь смысл — пустая пауза пугает.",
        "capricorn": "Наедине держишь рамку — иначе расползаешься.",
        "aquarius": "Наедине нужен свой контур — иначе растворяешься в шуме головы.",
        "pisces": "Наедине либо мягко восстанавливаешься, либо теряешь края.",
    },
}

# When cusp unknown — still one punchy recognition line.
_HOUSE_FALLBACK_HOW: dict[int, str] = {
    1: "В первом контакте тебя считывают по темпу и дистанции — ещё до ядра.",
    2: "Своё — деньги, навыки, право не оправдываться — держишь при себе.",
    3: "Открыто говоришь там, где есть доверие — не для всех подряд.",
    4: "Дом либо восстанавливает тебя, либо становится клеткой.",
    5: "Ради себя тебе нужна своя игра — не только роль для других.",
    6: "Быт и тело либо держат тебя, либо копятся как долг.",
    7: "В равной связи ты не сдаёшь себя целиком партнёру.",
    8: "В уязвимости контроль спорит с прямым разговором.",
    9: "Тебе нужен смысл шире «как сделать».",
    10: "В публичной роли важнее свой метод, чем чужая видимость.",
    11: "В круге отличаешь взаимный вектор от галочки связи.",
    12: "Наедине ты либо восстанавливаешься, либо теряешь опору.",
}


def _mech(identity_thesis: str) -> str:
    return _MECH.get(identity_thesis, "своё ядро характера")


def _norm_sign(raw: Any) -> str | None:
    if raw is None:
        return None
    s = str(raw).strip().lower()
    if not s:
        return None
    aliases = {
        "овен": "aries",
        "телец": "taurus",
        "близнецы": "gemini",
        "рак": "cancer",
        "лев": "leo",
        "дева": "virgo",
        "весы": "libra",
        "скорпион": "scorpio",
        "стрелец": "sagittarius",
        "козерог": "capricorn",
        "водолей": "aquarius",
        "рыбы": "pisces",
    }
    if s in aliases:
        return aliases[s]
    if s in _SIGN_RU:
        return s
    return s if s in _SIGN_ELEMENT else None


def _sign_ru_prep(sign: str | None) -> str | None:
    if not sign:
        return None
    return _SIGN_RU.get(sign)


def _house_recognition_how(house: int, cusp_sign: str | None) -> str:
    """One self-recognition sentence: house domain × cusp sign."""
    if cusp_sign:
        pack = _HOUSE_SIGN_THESIS.get(house) or {}
        hit = pack.get(cusp_sign)
        if hit:
            return hit
    return _HOUSE_FALLBACK_HOW.get(
        house,
        "Эта зона жизни читается по твоему куспиду — без общей энциклопедии дома.",
    )

def _card(how: str, do: str, *, anchors: dict[str, Any] | None = None) -> dict[str, Any]:
    how_c = " ".join(how.split()).strip()
    do_c = " ".join(do.split()).strip()
    row: dict[str, Any] = {
        "how": how_c,
        "do": do_c,
        "line": how_c,  # backward-compat alias for FE readers of `.line`
    }
    if anchors:
        row["anchors"] = anchors
    return row


def build_life_spheres_for_identity_v0(identity_thesis: str) -> dict[str, dict[str, str]]:
    """Person theses about life spheres overall — not day agenda, not engine how-it-works."""
    # Autonomy-flavoured default (most CE canaries); air_mind gets idea-led variants below.
    packs: dict[str, dict[str, str]] = {
        "love": {
            "how": (
                "В любви тебе сначала нужна ясность своего контура — иначе близость "
                "читается как давление сдать способ быть."
            ),
            "need": "Нужен партнёр и формат, где автономия не считается холодом.",
            "risk": "Риск — держать дистанцию там, где уже пора выбрать близость.",
            "turns_on": "Включает честный темп, уважение к ясности и взаимная зрелость.",
            "turns_off": "Выключает давление подогнать тебя под чужой темп.",
            "helps": "В связи держи одно явное правило: что твоё, что общее — без намёков.",
        },
        "money": {
            "how": (
                "Деньги для тебя — рычаг независимости: поток должен обслуживать выбор, "
                "а не чужие ожидания."
            ),
            "need": "Нужна рамка, где доход и траты не ломают самостоятельность.",
            "risk": "Риск — копить схемы и таблицы вместо одного ясного денежного выбора.",
            "turns_on": "Включает свобода манёвра и честный обмен без скрытых ожиданий.",
            "turns_off": "Выключает зависимость от чужих условий и размытые договорённости.",
            "helps": "Держи один денежный приоритет как закон месяца — без идеальной таблицы.",
        },
        "decisions": {
            "how": (
                "Решения зреют из внутреннего «да»: внешний хор редко ускоряет ясность, "
                "если контур ещё не собран."
            ),
            "need": "Нужно право дойти до вывода самому — без спешки чужого темпа.",
            "risk": "Риск — бесконечно уточнять картину вместо выбора.",
            "turns_on": "Включает тишина, структура и право на неполный, но честный шаг.",
            "turns_off": "Выключает давление решить «для всех» до собственной ясности.",
            "helps": "Сначала срок на сбор данных — потом один видимый шаг без идеальной схемы.",
        },
        "work": {
            "how": (
                "В работе тебе важны смысл и свой метод: роль жива, пока влияние "
                "не требует сдать контур."
            ),
            "need": "Нужна роль с влиянием и свободой метода — не только видимость занятости.",
            "risk": "Риск — уйти в автономный перфекционизм или не выходить в поле.",
            "turns_on": "Включает задача с ясной рамкой и свободой метода.",
            "turns_off": "Выключает микроконтроль и бессмысленная демонстрация занятости.",
            "helps": "В работе выбирай один фронт до «сделано» — до новых идей и схем.",
        },
        "family": {
            "how": (
                "Дом либо восстанавливает тебя, либо становится клеткой чужих правил — "
                "середины почти нет."
            ),
            "need": "Нужен быт, где можно восстановиться без потери себя.",
            "risk": "Риск — держать порядок или дистанцию вместо живого контакта с близкими.",
            "turns_on": "Включает уважение к границам и спокойный совместный ритм.",
            "turns_off": "Выключает вторжение в твой контур под видом «заботы».",
            "helps": "Дома держи право на явное «мне нужно» — коротко и без оправданий.",
        },
        "friends": {
            "how": (
                "В круге тебе важны близость идей и уважение темпа — не обязательная "
                "социальность «для галочки»."
            ),
            "need": "Нужны люди, с которыми можно быть цельным, не играя роль.",
            "risk": "Риск — держать сеть знакомств без настоящей взаимной связи.",
            "turns_on": "Включает честный разговор и свобода быть разным.",
            "turns_off": "Выключает обязательная социальность и скрытые долги внимания.",
            "helps": "В дружбе выбирай контакт по делу и смыслу — не по поддержанию статуса связи.",
        },
        "body": {
            "how": (
                "Тело у тебя сигналит «хватит / можно» раньше чужих норм — если дать "
                "этому голос, а не игнорировать."
            ),
            "need": "Нужен ритм, где нагрузка и пауза согласованы с твоим контуром.",
            "risk": "Риск — игнорировать тело, пока ум или долг ведут дальше.",
            "turns_on": "Включает ясный режим и движение без насилия над собой.",
            "turns_off": "Выключает чужие стандарты формы и гонка без восстановления.",
            "helps": "Телу нужен один устойчивый жест заботы: сон, еда или движение — по сигналу.",
        },
    }
    if identity_thesis == "builds_through_air_mind":
        packs["love"]["how"] = (
            "В любви тебе важно сначала понять устройство связи — иначе чувства "
            "кажутся хаосом без карты."
        )
        packs["work"]["how"] = (
            "В работе ты сильнее через идеи и связи: результат живёт, когда есть "
            "ясная рамка и пространство думать."
        )
        packs["decisions"]["how"] = (
            "Решения для тебя — сбор картины: варианты и смысл важнее чужой спешки."
        )
    return {sid: packs[sid] for sid in _SPHERE_IDS if sid in packs}


def extract_swiss_house_asc_anchors_v0(payload: dict[str, Any]) -> dict[str, Any]:
    """Pull cusp signs, ASC/MC, and personal planets-in-house from payload."""
    cusp_signs: dict[int, str] = {}
    asc_sign: str | None = None
    mc_sign: str | None = None
    planets_by_house: dict[int, list[str]] = {}

    diagnostics = payload.get("diagnostics") if isinstance(payload.get("diagnostics"), dict) else {}
    stage2_art = diagnostics.get("character_engine_stage2") if isinstance(diagnostics, dict) else None
    stage0 = {}
    if isinstance(stage2_art, dict):
        stage0 = stage2_art.get("stage0") if isinstance(stage2_art.get("stage0"), dict) else {}
    facts = stage0.get("raw_facts") if isinstance(stage0.get("raw_facts"), list) else []

    for row in facts:
        if not isinstance(row, dict):
            continue
        ft = str(row.get("fact_type") or "").strip().lower()
        value = row.get("value")
        sign = None
        if isinstance(value, dict):
            sign = _norm_sign(value.get("sign"))
        else:
            sign = _norm_sign(value)
        if ft.startswith("house_cusp_sign:") and sign:
            try:
                house = int(ft.split(":", 1)[1])
            except (TypeError, ValueError):
                continue
            if 1 <= house <= 12:
                cusp_signs[house] = sign
        elif ft == "angle_sign:ascendant" and sign:
            asc_sign = sign
        elif ft == "angle_sign:mc" and sign:
            mc_sign = sign

    natal = payload.get("natal_summary") if isinstance(payload.get("natal_summary"), dict) else {}
    angles = natal.get("angles") if isinstance(natal.get("angles"), dict) else {}
    if not asc_sign:
        asc_sign = _norm_sign(angles.get("ascendant_sign"))
    if not mc_sign:
        mc_sign = _norm_sign(angles.get("midheaven_sign"))
    # House 1 cusp often equals ASC; house 10 often MC.
    if asc_sign and 1 not in cusp_signs:
        cusp_signs[1] = asc_sign
    if mc_sign and 10 not in cusp_signs:
        cusp_signs[10] = mc_sign

    # Fill remaining cusps from natal_summary.houses when stage0 facts are sparse.
    houses_raw = natal.get("houses")
    if isinstance(houses_raw, list):
        for item in houses_raw:
            if not isinstance(item, dict):
                continue
            try:
                house = int(item.get("house")) if item.get("house") is not None else None
            except (TypeError, ValueError):
                house = None
            sign = _norm_sign(item.get("sign"))
            if house and 1 <= house <= 12 and sign and house not in cusp_signs:
                cusp_signs[house] = sign
    elif isinstance(houses_raw, dict):
        for key, item in houses_raw.items():
            try:
                house = int(key)
            except (TypeError, ValueError):
                continue
            sign = None
            if isinstance(item, dict):
                sign = _norm_sign(item.get("sign"))
            else:
                sign = _norm_sign(item)
            if 1 <= house <= 12 and sign and house not in cusp_signs:
                cusp_signs[house] = sign

    for bucket in ("luminaries", "personal_planets"):
        rows = natal.get(bucket) if isinstance(natal.get(bucket), list) else []
        for row in rows:
            if not isinstance(row, dict):
                continue
            name = str(row.get("name") or "").strip()
            if name not in _PERSONAL_PLANETS:
                continue
            try:
                house = int(row.get("house")) if row.get("house") is not None else None
            except (TypeError, ValueError):
                house = None
            if house is None or not (1 <= house <= 12):
                continue
            planets_by_house.setdefault(house, [])
            if name not in planets_by_house[house]:
                planets_by_house[house].append(name)

    return {
        "cusp_signs": cusp_signs,
        "asc_sign": asc_sign,
        "mc_sign": mc_sign,
        "planets_by_house": planets_by_house,
    }


def build_asc_applied_v0(
    identity_thesis: str,
    *,
    asc_sign: str | None,
) -> dict[str, Any] | None:
    """Applied ASC card: concrete first-contact thesis. None when ASC unknown."""
    if not asc_sign:
        return None
    modality = _SIGN_MODALITY.get(asc_sign, "свой темп")
    if identity_thesis == "builds_through_autonomy":
        how = (
            f"В первом контакте — {modality}: сначала проверка, "
            "что тебя не переформатируют, потом открытость."
        )
    else:
        how = (
            f"В первом контакте тебя считывают так: {modality} — "
            "манера начинать, ещё не весь характер."
        )
    do = "В новом знакомстве зафиксируй первый жест: дистанция, шаг ближе или сразу правила."
    return {
        "sign": asc_sign,
        **_card(how, do, anchors={"sign": asc_sign}),
    }


def build_mc_applied_v0(
    identity_thesis: str,
    *,
    mc_sign: str | None,
) -> dict[str, Any] | None:
    if not mc_sign:
        return None
    modality = _SIGN_MODALITY.get(mc_sign, "свой критерий результата")
    if identity_thesis == "builds_through_autonomy":
        how = (
            f"Публичная роль — {modality}: видимость без сдачи своего метода."
        )
    else:
        how = f"Публичная роль и результат — {modality}."
    do = "Выбери один видимый результат — маленький, но названный — и доведи до «сделано»."
    return {
        "sign": mc_sign,
        **_card(how, do, anchors={"sign": mc_sign}),
    }


def _house_how_do(
    house: int,
    *,
    identity_thesis: str,
    cusp_sign: str | None,
    planets: list[str],
) -> tuple[str, str]:
    """Recognition thesis only — no agenda «do», no mechanism tint, no planet dump."""
    del identity_thesis, planets  # reserved; thesis is house×sign, not identity stamp
    how = _house_recognition_how(house, cusp_sign)
    return how, ""


def build_house_person_lines_for_identity_v0(
    identity_thesis: str,
    *,
    cusp_signs: dict[int, str] | None = None,
    planets_by_house: dict[int, list[str]] | None = None,
) -> dict[str, dict[str, Any]]:
    """Applied house cards for all 12 houses: domain + cusp modality + planet function when occupied."""
    cusp_signs = cusp_signs or {}
    planets_by_house = planets_by_house or {}
    out: dict[str, dict[str, Any]] = {}
    for house in range(1, 13):
        planets = [p for p in planets_by_house.get(house, []) if p in _PERSONAL_PLANETS]
        # Stable planet order
        planets = [p for p in ("Sun", "Moon", "Mercury", "Venus", "Mars") if p in planets]
        cusp = cusp_signs.get(house)
        how, do = _house_how_do(
            house,
            identity_thesis=identity_thesis,
            cusp_sign=cusp,
            planets=planets,
        )
        anchors: dict[str, Any] = {}
        if cusp:
            anchors["cusp_sign"] = cusp
        if planets:
            anchors["planets"] = planets
        out[str(house)] = _card(how, do, anchors=anchors or None)
    return out


# Back-compat name used by older tests / callers expecting angular-only map.
def build_house_person_lines_angular_only_v0(identity_thesis: str) -> dict[str, dict[str, Any]]:
    return build_house_person_lines_for_identity_v0(identity_thesis)


def matrix_style_fields_for_identity_v0(identity_thesis: str) -> dict[str, str]:
    """Contract fields that feed profile_matrix emotional / work / home slots."""
    if identity_thesis == "builds_through_air_mind":
        return {
            "emotional_style": (
                "Эмоции ты сначала переводишь в мысль и формулировку — и только потом "
                "отдаёшь наружу. Тебе нужно понять чувство, прежде чем жить им вслух."
            ),
            "work_and_realization": (
                "В работе ты сильнее через идеи, связи и ясный смысл задачи. "
                "Видимость полезна, если не требует сдать свой способ думать."
            ),
            "home_and_security": (
                "Дом должен давать воздух для головы и восстановления — не шум чужих "
                "правил и постоянную доступность."
            ),
        }
    # Default: autonomy / own-system contour.
    return {
        "emotional_style": (
            "Эмоции ты сначала проводишь через свой внутренний контур — и только потом "
            "наружу. Им нужно место в твоей системе, не красивость для других."
        ),
        "work_and_realization": (
            "В работе тебе нужна роль с влиянием без потери своего метода. "
            "Видимость важна, только если не требует сдать способ делать."
        ),
        "home_and_security": (
            "Дом и безопасность — воздух для восстановления, а не клетка из чужих "
            "правил и суеты."
        ),
    }


def apply_aspect_lines_to_payload(payload: dict[str, Any], *, identity_thesis: str) -> None:
    """Do not overwrite every aspect gist with the same CE template."""
    del identity_thesis  # reserved for future differentiated aspect essays
    payload["character_engine_aspect_lines_v0"] = {
        "projection_version": "character_engine_aspect_lines_v0.2",
        "aspects": {},
        "note": (
            "No blanket CE stamp on aspects — natal/Swiss gist remains. "
            "Differentiated aspect essays may land later."
        ),
    }


def apply_spheres_and_houses_to_payload(
    payload: dict[str, Any],
    *,
    identity_thesis: str,
) -> None:
    """Mutate payload: contract.life_spheres + applied ASC/houses + matrix + aspects."""
    spheres = build_life_spheres_for_identity_v0(identity_thesis)
    anchors = extract_swiss_house_asc_anchors_v0(payload)
    houses = build_house_person_lines_for_identity_v0(
        identity_thesis,
        cusp_signs=anchors["cusp_signs"],
        planets_by_house=anchors["planets_by_house"],
    )
    styles = matrix_style_fields_for_identity_v0(identity_thesis)
    contract = payload.get("profile_contract_v1")
    if isinstance(contract, dict):
        contract = dict(contract)
        contract["life_spheres"] = spheres
        contract.update(styles)
        payload["profile_contract_v1"] = contract
    payload["character_engine_house_lines_v0"] = {
        "projection_version": "character_engine_house_lines_v0.8",
        "identity_thesis": identity_thesis,
        "houses": houses,
        "note": (
            "One recognition sentence per house (house × cusp sign). "
            "No agenda do / no mechanism tint. Cusp/sign/degree remain Swiss."
        ),
    }
    asc = build_asc_applied_v0(identity_thesis, asc_sign=anchors.get("asc_sign"))
    mc = build_mc_applied_v0(identity_thesis, mc_sign=anchors.get("mc_sign"))
    payload["character_engine_asc_v0"] = {
        "projection_version": "character_engine_asc_v0.1",
        "identity_thesis": identity_thesis,
        "asc": asc,
        "mc": mc,
        "note": "Applied first-contact / role cards; omit when angle unknown.",
    }
    apply_aspect_lines_to_payload(payload, identity_thesis=identity_thesis)
