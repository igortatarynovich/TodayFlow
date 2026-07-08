"""guide_decision_v0 — детерминированное «решение дня» для guide (без LLM).

Сводит day_model_v0, ритуал, луну из foundation и короткий контур профиля в один
набор полей, который затем кладётся в DayContext и **подменяет** headline/subline/
core_message/do/avoid/риски/сигналы в `today_narrative` (RU; EN — упрощённо).

Идея: сначала решение и причинность, потом LLM оформляет вторичные блоки; ядро
не заполняется абстрактными парами существительных из «пустой» генерации.
"""

from __future__ import annotations

import re
from typing import Any

from todayflow_backend.services.day_logic_shared_v0 import (
    clip_day_logic_text as _clip,
    foundation_spine_dict,
    fusion_energy_score_int,
    humanize_day_direction_en,
    humanize_day_direction_ru,
    humanize_day_focus_key,
    ritual_core_fields,
    spine_text_fields,
)

_SLUG_GENERAL = re.compile(r"\bgeneral\b", re.I)
_SLUG_IN_QUOTES = re.compile(r"'([a-z][a-z0-9_]{0,24})'", re.I)


def _lunar_phase_name(foundation: dict[str, Any] | None) -> str:
    if not isinstance(foundation, dict):
        return ""
    ce = foundation.get("celestial_events")
    if not isinstance(ce, dict):
        return ""
    lp = ce.get("lunar_phase")
    if isinstance(lp, dict):
        return str(lp.get("name") or "").strip()
    return ""


def _mood_low_bandwidth(mood: str) -> bool:
    m = (mood or "").lower()
    return any(
        x in m
        for x in (
            "устал",
            "тяжел",
            "тяжёл",
            "выбит",
            "разбит",
            "сил нет",
            "измотан",
            "tired",
            "exhaust",
            "drain",
        )
    )


def _sanitize_spine_line(text: str) -> str:
    """Убираем служебные slug'и из строк стержня (general и т.д.)."""
    t = (text or "").strip()
    if not t:
        return ""
    if _SLUG_GENERAL.search(t):
        return "размытая линия «всё сразу» без одного ясного приоритета"

    def _repl(m: re.Match[str]) -> str:
        return f"«{humanize_day_focus_key(m.group(1))}»"

    t = _SLUG_IN_QUOTES.sub(_repl, t)
    return t


def _profile_hook_sentence(user_core: dict[str, Any] | None, *, locale_en: bool) -> str:
    if not isinstance(user_core, dict):
        return ""
    base = user_core.get("baseline")
    if isinstance(base, dict):
        rs = str(base.get("rhythm_style") or "").strip()
        if len(rs) > 10:
            return (
                f"Your usual rhythm pattern: {_clip(rs, 140)}."
                if locale_en
                else f"Твоя база по ритму: {_clip(rs, 140)}."
            )
    ls = str(user_core.get("living_summary") or "").strip()
    if len(ls) > 20:
        return (
            f"How days tend to land for you: {_clip(ls, 200)}."
            if locale_en
            else f"Как дни у тебя обычно складываются: {_clip(ls, 200)}."
        )
    return ""


def build_guide_decision_v0(
    *,
    day_model: dict[str, Any] | None,
    ritual: dict[str, Any] | None,
    foundation: dict[str, Any] | None,
    user_core: dict[str, Any] | None,
    fusion_scores: dict[str, Any] | None,
    locale: str,
) -> dict[str, Any]:
    """Возвращает объект для `DayContext.layers.guide_decision` и merge в guide payload."""
    en = (locale or "").strip().lower().startswith("en")
    dm = day_model if isinstance(day_model, dict) else {}
    scales = dm.get("scales") if isinstance(dm.get("scales"), dict) else {}
    direction = str(scales.get("direction") or "transition").strip()
    tempo = str(scales.get("tempo") or "steady").strip()
    try:
        en_score = int(scales.get("energy_0_100") or fusion_energy_score_int(fusion_scores))
    except (TypeError, ValueError):
        en_score = fusion_energy_score_int(fusion_scores)

    vector = dm.get("vector") if isinstance(dm.get("vector"), dict) else {}
    tension = dm.get("tension") if isinstance(dm.get("tension"), dict) else {}
    risk_o = dm.get("risk") if isinstance(dm.get("risk"), dict) else {}
    opportunity = dm.get("opportunity") if isinstance(dm.get("opportunity"), dict) else {}
    strategy = dm.get("strategy") if isinstance(dm.get("strategy"), dict) else {}

    v_sum = _clip(str(vector.get("summary") or ""), 360)
    t_sum = _clip(str(tension.get("summary") or ""), 420)
    r_sum = _clip(str(risk_o.get("summary") or ""), 480)
    opp = _clip(str(opportunity.get("summary") or ""), 280)
    one_focus = _clip(str(strategy.get("one_focus") or opp or ""), 220)

    rc = ritual_core_fields(ritual if isinstance(ritual, dict) else None)
    card = rc["tarot_name_ru"]
    num = rc["numerology_value"]
    mood = rc["mood"]
    head_topic = rc["head_topic"]
    moon = _lunar_phase_name(foundation)

    spine = foundation_spine_dict(foundation if isinstance(foundation, dict) else None)
    sf = spine_text_fields(spine)
    main_risk_spine = _sanitize_spine_line(sf["main_risk"])
    dne = _sanitize_spine_line(sf["do_not_enter"])

    low = _mood_low_bandwidth(mood)
    profile_hook = _profile_hook_sentence(user_core, locale_en=en)

    # --- Ситуация (факты слоёв) ---
    if en:
        situ_parts: list[str] = []
        if card:
            situ_parts.append(f"Today's symbol card is «{card}»")
        if num:
            situ_parts.append(f"day number {num}")
        if moon:
            situ_parts.append(f"Moon phase: {moon}")
        if mood:
            situ_parts.append(f"check-in mood: {mood}")
        situation = ". ".join(situ_parts).strip()
        if situation:
            situation += ". "
        dir_en = humanize_day_direction_en(direction)
        situation += f"The day vector — {dir_en} — points to: {v_sum or 'one clear lane'}"
    else:
        situ_parts_ru: list[str] = []
        if card:
            situ_parts_ru.append(f"карта дня — «{card}»")
        if num:
            situ_parts_ru.append(f"число дня {num}")
        if moon:
            situ_parts_ru.append(f"луна — {moon}")
        if mood:
            situ_parts_ru.append(f"состояние после чек-ина: {mood}")
        situation = ""
        if situ_parts_ru:
            situation = "Сегодня в поле символов: " + ", ".join(situ_parts_ru) + ". "
        dir_ru = humanize_day_direction_ru(direction)
        situation += f"По расчёту дня — {dir_ru}: {v_sum or 'держи одну ясную линию, без распыления'}."

    # --- Конфликт ---
    if en:
        conflict = t_sum or "Push vs capacity: keep one lane instead of many parallel starts."
        if low:
            conflict = f"{conflict} Low bandwidth today — speed without closure turns into noise."
    else:
        conflict = t_sum or "Есть натяжение между тем, куда день зовёт, и тем, сколько у тебя реально тянет без хаоса."
        if low:
            conflict = (
                f"{conflict} Ты отметил усталость — движение без сужения фокуса быстро превращается в «много сделал, ничего не закрыл»."
            )
        if head_topic:
            conflict = f"{conflict} Тема «в голове» ({head_topic}) — учитывай её в выборе одной линии, не расползайся."

    # --- Где сломаешься ---
    if en:
        failure = (
            "You open too many tracks, answer everything at once, switch before anything is finished — "
            "by midday it feels like motion without closure."
        )
        if direction == "completion":
            failure = (
                "You try to 'catch up' the whole day: many starts, no finished line — exactly when the day asks for closure."
            )
    else:
        failure = (
            "Самый частый сценарий: откроешь несколько задач, начнёшь реагировать на всё подряд, "
            "будешь переключаться — к середине дня ощущение «я в движении, но ничего не довёл»."
        )
        if direction == "completion":
            failure = (
                "Риск именно сегодня: попытка «догнать день» множеством стартов вместо одного завершения — "
                "в тот момент, когда ось дня про закрытие линий."
            )

    # --- Что сработает ---
    if en:
        what_works = (
            f"Take control over **one** direction already in motion — not a brand-new hero task. {one_focus}".strip()
        )
    else:
        what_works = (
            "Не «возьми себя в руки» в абстракции, а сузь поле: одно направление, которое уже начато, "
            "и доведи его до честного конца в одном слоте без переключений."
        )
        if one_focus:
            what_works = f"{what_works} Опора дня: {one_focus}"

    # --- Один ход ---
    if en:
        one_move = (
            "Pick one task that is already started, creates light resistance, and can be truly finished — "
            "work it in a single 20-minute block without switching."
        )
    else:
        one_move = (
            "Выбери одну задачу, которая уже начата, вызывает лёгкое сопротивление, но реально может быть закрыта — "
            "и доведи её в одном слоте 20 минут без переключений."
        )
        if head_topic and "тел" in head_topic.lower():
            one_move = (
                "Тема тела в голове: один короткий слот на то, что уже висит (сон, еда, движение, врач) — "
                "доведи до конкретного результата, не открывая пятый фронт работы."
            )

    # --- Чего не делать ---
    if en:
        dont = [
            "Do not open brand-new big initiatives today.",
            "Do not answer every ping immediately — batch or defer.",
            "Do not use 'I must get it together' as a substitute for one finished step.",
        ]
    else:
        dont = [
            "Не начинай новую крупную инициативу «с нуля» — сначала закрой одно висящее.",
            "Не отвечай на всё входящее сразу — пакетно или после слота фокуса.",
            "Не дави на себя фразой «надо собраться» вместо одного завершённого куска.",
        ]
    if main_risk_spine:
        dont.append(_clip(f"Осторожнее с: {main_risk_spine}", 200))
    elif r_sum:
        dont.append(_clip(r_sum, 200))
    if dne:
        dont.append(_clip(dne, 200))
    dont = [_clip(x, 240) for x in dont if str(x).strip()][:4]

    # --- Заголовок / подзаголовок (конкретика, не «смысл и коммуникация») ---
    if en:
        headline = _clip(
            f"Day pulls {direction.replace('_', ' ')}, but closure beats more starts" if direction != "transition" else "One lane beats many open tabs",
            120,
        )
        if card:
            headline = _clip(f"«{card}» wants motion — finish one thread first", 120)
        subline = _clip(f"{conflict[:220]} {one_move[:180]}", 500)
    else:
        if card and low:
            headline = _clip(f"«{card}» зовёт в движение, а ты устал — сужай поле", 130)
        elif card:
            headline = _clip(f"«{card}» задаёт импульс дня — не превращай его в много недоделанного", 130)
        elif num:
            headline = _clip(f"Число {num} усиливает темп — держи одну линию до конца", 120)
        else:
            headline = _clip("Сегодня важно не количество стартов, а одно завершение", 120)
        subline = _clip(
            f"{situation[:280]} {conflict[:260]}",
            520,
        )

    # --- core body: связный блок ---
    if en:
        core_body = "\n\n".join(
            x
            for x in [
                situation.strip(),
                f"Tension: {conflict}",
                f"Where it breaks: {failure}",
                f"What works: {what_works}",
                profile_hook,
                f"Concrete move: {one_move}",
            ]
            if x
        )
    else:
        core_body = "\n\n".join(
            x
            for x in [
                "Что происходит",
                situation.strip(),
                "",
                "Где реальный конфликт",
                conflict,
                "",
                "Где ты сломаешься",
                failure,
                "",
                "Что реально сработает",
                what_works,
                profile_hook,
                "",
                "Конкретный ход",
                one_move,
            ]
            if x
        )
    core_body = _clip(core_body, 900)

    # --- do / avoid ---
    if en:
        do_items = [
            _clip(one_move, 280),
            _clip(f"Single 20-minute block on the chosen task — no switching ({tempo} tempo, {en_score}/100).", 280),
            _clip(opp or "Close one nagging item before opening another.", 280),
        ]
    else:
        do_items = [
            _clip(one_move, 280),
            _clip(
                f"Один слот 20 минут без переключений на выбранную задачу (темп «{tempo}», ресурс {en_score}/100).",
                280,
            ),
            _clip(opp or one_focus or "Закрой один висящий кусок, прежде чем брать новое.", 280),
        ]

    avoid_items = dont[:3]
    while len(avoid_items) < 3:
        avoid_items.append("Не распыляйся на лишние обещания без ресурса." if not en else "No extra promises without bandwidth.")

    # --- energy / focus lines (причинность + ритуал) ---
    if en:
        energy_line = f"Energy index ~{en_score}/100, tempo {tempo}. {moon + ' — factor in emotional bandwidth.' if moon else 'Keep cycles short.'}"
        focus_line = (
            "Attention on finishing what is already open — card/number are about motion, not new tabs."
            if card or num
            else "Attention on one finished step, not many starts."
        )
    else:
        moon_bit = f" {moon} добавляет эмоциональную громкость — не путай срочность с приоритетом." if moon else ""
        energy_line = _clip(
            f"Ресурс дня около {en_score}/100, темп «{tempo}». Карта и число задают импульс — не обязательно гнать сразу всё.{moon_bit}",
            500,
        )
        focus_line = _clip(
            (
                f"Фокус — на завершении уже начатого; «{card}» и число {num} про движение, а не про пять параллельных фронтов."
                if card and num
                else f"Фокус — довести одну линию; число {num} подсвечивает импульс, не распыляй его."
                if num
                else "Фокус — один доведённый кусок вместо множества недозакрытых."
            ),
            500,
        )

    risk_line = _clip(main_risk_spine or r_sum or ("overload" if en else "перегруз и недозакрытые линии"), 120)
    risk_detail = _clip(r_sum or failure, 500)

    return {
        "contract_version": "guide_decision_v0",
        "locale": "en" if en else "ru",
        "headline": headline,
        "subline": subline,
        "core_message": {
            "body": core_body,
            "risk": _clip(failure, 320),
            "best_move": _clip(one_move, 320),
        },
        "do_items": do_items[:3],
        "avoid_items": avoid_items[:3],
        "energy_line": energy_line,
        "focus_line": focus_line,
        "risk_line": risk_line,
        "risk_detail": risk_detail,
        "anchors": {
            "tarot": card or None,
            "numerology": num or None,
            "moon_phase": moon or None,
            "mood": mood or None,
            "head_topic": head_topic or None,
            "day_direction": direction,
            "tempo": tempo,
        },
    }
