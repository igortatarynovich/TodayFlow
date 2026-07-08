"""Spread-first Guidance assembly: structure → question → profile bridge → single action.

Guidance is defined only for a full spread session (question + spread + cards in positions).
This module does not call an LLM; it composes copy from the dealt spread and lane templates.
"""

from __future__ import annotations

import re
from typing import Any

from todayflow_backend.core import models as core_models

GUIDANCE_SPREAD_GOALS = frozenset(
    {
        "understand_situation",
        "choose_action",
        "understand_person",
        "see_risk",
        "close_cycle",
        "clarify_feelings",
    }
)

GUIDANCE_DEPTH = frozenset({"quick", "normal", "deep"})


def _is_en(locale: str | None) -> bool:
    return (locale or "").startswith("en")


def position_weight(position_id: str) -> float:
    """Semantic weight by position id (not all slots are equal for synthesis)."""
    pid = (position_id or "").lower()
    high = (
        "risk",
        "block",
        "fear",
        "obstacle",
        "blind",
        "tension",
        "main_risk",
        "illusion",
        "suppress",
        "stop",
        "harm",
        "nuance",
    )
    elevated = (
        "advice",
        "best_action",
        "next_step",
        "practical",
        "unstick",
        "move",
        "best_step",
        "next_move",
        "main_chance",
        "weights",
    )
    if any(tag in pid for tag in high):
        return 1.38
    if any(tag in pid for tag in elevated):
        return 1.22
    return 1.0


def _clip(text: str, max_len: int) -> str:
    t = " ".join(text.split()).strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 1].rstrip() + "…"


def _meaning_snippet(meaning: str, limit: int) -> str:
    return _clip(meaning.replace("\n", " "), limit)


def assess_guidance_question(
    question: str,
    *,
    memory_context: dict[str, Any] | None,
    locale: str | None = None,
) -> dict[str, Any]:
    q = " ".join((question or "").split()).strip()
    low = q.lower()
    words = re.findall(r"[а-яёa-z0-9]+", low)

    too_general = len(words) < 5 or (len(q) < 28 and "?" not in q)
    fortune_telling = bool(
        re.search(
            r"\b(верн[её]тся|напишет|позвонит|когда\s|что\s+будет\s+12|точно\s|гарант)",
            low,
        )
    )
    low_actionability = bool(re.search(r"\b(он\s|она\s|они\s).*(напишет|позвонит|верн)", low)) and not re.search(
        r"\b(я\s|мне\s|мой|моя|как\s+мне|что\s+мне)", low
    )
    repeated = int((memory_context or {}).get("repeated_questions_count") or 0)
    possible_repeat = repeated >= 2

    flags = {
        "too_general": too_general,
        "fortune_telling_tone": fortune_telling,
        "low_actionability": low_actionability,
        "possible_repeat": possible_repeat,
    }

    suggestion: str | None = None
    weak_warning: str | None = None
    if _is_en(locale):
        if too_general:
            suggestion = "Try naming one situation and one thing you want to understand or do about it."
        if fortune_telling:
            suggestion = (
                "A stronger question sounds like: what matters for me here, and what is one healthy step I can take?"
            )
        if possible_repeat:
            weak_warning = "Similar questions showed up before — the spread will be stronger if you test one action rather than look for a new sign."
    else:
        if too_general:
            suggestion = "Сузи до одной ситуации и одного узла: что именно ты хочешь понять или сделать?"
        if fortune_telling:
            suggestion = (
                "Сильнее звучит вопрос в духе: что мне важно понять в этой связи и какой шаг будет для меня здоровым?"
            )
        if low_actionability and not fortune_telling:
            suggestion = "Добавь, что важно именно тебе сделать или понять — не только что сделает другой человек."
        if possible_repeat:
            weak_warning = (
                "Похоже, это не первый похожий запрос. Расклад сильнее, если проверить действие, а не искать новый «знак»."
            )
        if too_general and fortune_telling:
            weak_warning = "Если оставить вопрос слишком общим или про чужое действие, разбор легко станет размытым."

    return {"flags": flags, "suggestion": suggestion, "weak_reading_warning": weak_warning}


def build_spread_schema(
    spread_id: str,
    spread_title: str,
    cards: list[core_models.TarotSpreadCard],
) -> dict[str, Any]:
    positions_out: list[dict[str, Any]] = []
    for c in cards or []:
        pos = c.position
        pid = pos.id if isinstance(pos, core_models.TarotSpreadPosition) else "position"
        title = pos.title if isinstance(pos, core_models.TarotSpreadPosition) else str(pos)
        prompt = pos.prompt if isinstance(pos, core_models.TarotSpreadPosition) else None
        w = position_weight(pid)
        positions_out.append(
            {
                "id": pid,
                "title": title,
                "prompt": prompt,
                "weight": round(w, 3),
            }
        )
    return {"spread_id": spread_id, "spread_title": spread_title, "positions": positions_out}


def structural_spread_analysis(
    cards: list[core_models.TarotSpreadCard],
    *,
    locale: str | None = None,
) -> dict[str, Any]:
    if not cards:
        return {
            "dominant_position_id": None,
            "dominant_card_name": None,
            "tension_position_id": None,
            "support_position_id": None,
            "conflict_note": "",
            "themes": [],
        }

    scored: list[tuple[float, core_models.TarotSpreadCard, str]] = []
    tension_candidates: list[tuple[float, str]] = []
    support_candidates: list[tuple[float, str]] = []
    for c in cards:
        pos = c.position
        pid = pos.id if isinstance(pos, core_models.TarotSpreadPosition) else ""
        w = position_weight(pid)
        orient_boost = 1.12 if c.orientation == "reversed" else 1.0
        score = w * orient_boost
        scored.append((score, c, pid))
        low_pid = pid.lower()
        if any(k in low_pid for k in ("risk", "block", "fear", "tension", "blind", "illusion", "nuance")):
            tension_candidates.append((score, pid))
        if any(k in low_pid for k in ("support", "chance", "gives", "can_work", "advice", "best_action", "practical")):
            support_candidates.append((score, pid))

    scored.sort(key=lambda x: x[0], reverse=True)
    dominant = scored[0][1]
    dom_pos = dominant.position
    dom_pid = dom_pos.id if isinstance(dom_pos, core_models.TarotSpreadPosition) else None
    dom_title = dom_pos.title if isinstance(dom_pos, core_models.TarotSpreadPosition) else str(dom_pos)

    tension_position_id = None
    if tension_candidates:
        tension_candidates.sort(key=lambda x: x[0], reverse=True)
        tension_position_id = tension_candidates[0][1]
    elif scored:
        tension_position_id = scored[0][2] or None

    support_position_id = None
    if support_candidates:
        support_candidates.sort(key=lambda x: x[0], reverse=True)
        support_position_id = support_candidates[0][1]
    elif len(scored) > 1:
        support_position_id = scored[-1][2] or None

    upright_n = sum(1 for _, card, __ in scored if card.orientation == "upright")
    rev_n = len(scored) - upright_n
    themes: list[str] = []
    for kw in dominant.card.keywords or []:
        if isinstance(kw, str) and kw.strip():
            themes.append(kw.strip())
    themes = themes[:4]

    if _is_en(locale):
        if rev_n >= 2 and upright_n >= 2:
            conflict_note = (
                "The spread pulls in two directions: part of the line pushes for clarity or movement, "
                "another part flags friction or delay — that tension is the reading, not a mistake."
            )
        elif rev_n >= 3:
            conflict_note = (
                "Several reversed cards highlight inner brakes or unfinished business; the value is naming that drag, not forcing a neat story."
            )
        else:
            conflict_note = "The positions do not collapse into one slogan — the spread is read through the strongest slot and the friction between roles of each card."
    else:
        if rev_n >= 2 and upright_n >= 2:
            conflict_note = (
                "В раскладе есть натяжение: одна линия тянет к ясности или шагу, другая показывает торможение или риск — "
                "это и есть смысл, а не «ошибка» карт."
            )
        elif rev_n >= 3:
            conflict_note = (
                "Несколько перевёрнутых карт подчёркивают внутренние тормоза или незавершённость; ценность — назвать это сопротивление, а не сгладить в одну сказку."
            )
        else:
            conflict_note = (
                "Позиции не складываются в один лозунг: чтение идёт через самый сильный узел и через то, как роли карт спорят друг с другом."
            )

    return {
        "dominant_position_id": dom_pid,
        "dominant_card_name": dominant.card.name,
        "tension_position_id": tension_position_id,
        "support_position_id": support_position_id,
        "conflict_note": conflict_note,
        "themes": themes,
    }


def _goal_phrase(goal: str | None, *, locale: str | None) -> str:
    g = (goal or "").strip() or "understand_situation"
    if _is_en(locale):
        mapping = {
            "understand_situation": "mapping what is alive in the situation",
            "choose_action": "choosing one grounded move",
            "understand_person": "seeing the other person without losing your boundary",
            "see_risk": "spotting where the real risk sits",
            "close_cycle": "closing a loop instead of re-reading the same worry",
            "clarify_feelings": "sorting feelings without fortune-telling",
        }
        return mapping.get(g, mapping["understand_situation"])
    mapping = {
        "understand_situation": "понять, что в ситуации живое и что сейчас главное",
        "choose_action": "выбрать один заземлённый шаг",
        "understand_person": "увидеть другого человека, не теряя свои границы",
        "see_risk": "поймать, где настоящий риск",
        "close_cycle": "закрыть цикл, а не перечитывать ту же тревогу",
        "clarify_feelings": "разложить чувства без гадания на даты",
    }
    return mapping.get(g, mapping["understand_situation"])


def _extract_profile_bridge(
    core_profile: dict[str, Any] | None,
    *,
    topic: str | None,
    lane: str,
    locale: str | None = None,
) -> str:
    if not core_profile:
        return ""
    interpretation = core_profile.get("interpretation") if isinstance(core_profile.get("interpretation"), dict) else {}
    daily = (
        core_profile.get("daily_interpretation")
        if isinstance(core_profile.get("daily_interpretation"), dict)
        else {}
    )
    lenses = daily.get("daily_lenses") if isinstance(daily.get("daily_lenses"), dict) else {}

    candidates: list[str] = []
    if topic in {"relationships", "intimacy"} or lane == "love":
        for key in ("relationships", "love", "bonding"):
            chunk = interpretation.get(key)
            if isinstance(chunk, str) and chunk.strip():
                candidates.append(chunk.strip())
    elif topic in {"work", "money"} or lane == "money_career":
        for key in ("work", "money", "ambition"):
            chunk = interpretation.get(key)
            if isinstance(chunk, str) and chunk.strip():
                candidates.append(chunk.strip())
    elif lane == "state":
        for key in ("nervous_system", "energy", "recovery"):
            chunk = interpretation.get(key)
            if isinstance(chunk, str) and chunk.strip():
                candidates.append(chunk.strip())
    else:
        ident = interpretation.get("identity")
        if isinstance(ident, str) and ident.strip():
            candidates.append(ident.strip())

    for k, v in lenses.items():
        if isinstance(v, str) and v.strip() and topic and k.lower() in topic.lower():
            candidates.append(v.strip())

    if not candidates:
        baseline = core_profile.get("baseline") if isinstance(core_profile.get("baseline"), dict) else {}
        arch = baseline.get("archetype_seed")
        if isinstance(arch, str) and arch.strip():
            if _is_en(locale):
                return f"Your current baseline reads through the {arch.strip()} pattern — use it to pace the step, not to override the cards."
            return (
                f"Твоя базовая линия сейчас читается через архетип «{arch.strip()}» — это про темп шага, а не замену карт."
            )

    snippet = _clip(candidates[0], 220) if candidates else ""
    if not snippet:
        return ""
    if _is_en(locale):
        return (
            f"In this spread the cards stay central; your profile adds pacing: {snippet} "
            f"Hold that as adjustment, not as a verdict over the layout."
        )
    return (
        f"Карты остаются центром; профиль добавляет темп и акцент: {snippet} "
        f"Это уточнение, а не приговор вместо расклада."
    )


def _learning_mode_line(learning_context: dict[str, Any] | None, *, locale: str | None) -> str:
    if not learning_context:
        return ""
    rs = str(learning_context.get("response_style") or "").lower()
    ss = str(learning_context.get("support_style") or "").lower()
    if _is_en(locale):
        if "anxious" in rs or "anxiety" in rs or "worried" in rs:
            return "Favor tiny, reversible moves and write the thought for yourself before any confrontation."
        if "overload" in ss or "burnout" in ss or "depleted" in ss:
            return "Keep the step within today's real capacity — one short block of time is enough."
        return ""
    if "тревог" in rs or "беспокойств" in rs:
        return "В тревожном режиме лучше маленький обратимый шаг и сначала формулировка мысли для себя, а не «срочный разговор»."
    if "перегруз" in ss or "устал" in ss:
        return "Если ресурс низкий, шаг должен укладываться в один короткий блок времени — без героизма."
    return ""


def compose_guidance_reading(
    *,
    question: str,
    spread_id: str,
    spread_title: str,
    cards: list[core_models.TarotSpreadCard],
    lane: str,
    base_answer: dict[str, str],
    core_profile: dict[str, Any] | None,
    topic: str | None,
    user_intent: str | None,
    requested_depth: str | None,
    question_assessment: dict[str, Any],
    structural: dict[str, Any],
    learning_context: dict[str, Any] | None,
    today_context: str | None,
    locale: str | None = None,
) -> tuple[dict[str, str], dict[str, Any]]:
    """Returns (remapped QuestionAnswerBlock dict, interpretation contract dict)."""

    depth = (requested_depth or "normal").strip().lower()
    if depth not in GUIDANCE_DEPTH:
        depth = "normal"
    goal = (user_intent or "").strip() or None
    if goal and goal not in GUIDANCE_SPREAD_GOALS:
        goal = None

    goal_phrase = _goal_phrase(goal, locale=locale)
    profile_bridge = _extract_profile_bridge(core_profile, topic=topic, lane=lane, locale=locale)
    mode_line = _learning_mode_line(learning_context, locale=locale)

    dom_name = structural.get("dominant_card_name") or ""
    dom_pos_id = structural.get("dominant_position_id") or ""
    dom_card = None
    for c in cards:
        pos = c.position
        pid = pos.id if isinstance(pos, core_models.TarotSpreadPosition) else None
        if pid == dom_pos_id:
            dom_card = c
            break
    if dom_card is None and cards:
        dom_card = cards[0]
    dom_pos_title = ""
    if dom_card:
        p = dom_card.position
        dom_pos_title = p.title if isinstance(p, core_models.TarotSpreadPosition) else str(p)

    dominant_meaning = _meaning_snippet(dom_card.meaning, 180) if dom_card else ""

    if _is_en(locale):
        summary = (
            f"The «{spread_title}» layout centers the signal in «{dom_pos_title}»: "
            f"«{dom_name}» ({dom_card.orientation if dom_card else ''}) — {dominant_meaning}"
        )
        summary = _clip(summary, 420 if depth != "quick" else 260)
        q_line = _clip(question, 160)
        structural_body = (
            f"{structural.get('conflict_note', '')} "
            f"Your question — «{q_line}» — is read as {goal_phrase}."
        )
        if today_context and today_context.strip():
            structural_body += f" Today layer note: {_clip(today_context.strip(), 140)}"
        core_insight = (
            f"The main knot sits in «{dom_pos_title}»: the spread asks you to treat that slot as the lever, "
            f"not every card as equally loud."
        )
        avoid_card = None
        for c in cards:
            pid = c.position.id if isinstance(c.position, core_models.TarotSpreadPosition) else ""
            if structural.get("tension_position_id") and pid == structural.get("tension_position_id"):
                avoid_card = c
                break
        if avoid_card is None:
            for c in cards:
                pid = (c.position.id if isinstance(c.position, core_models.TarotSpreadPosition) else "").lower()
                if any(k in pid for k in ("risk", "block", "harm", "illusion")):
                    avoid_card = c
                    break
        avoid_text = (
            _meaning_snippet(avoid_card.meaning, 140)
            if avoid_card
            else "Do not turn the spread into fortune-telling about someone else's exact move."
        )
        action_core = base_answer.get("today") or base_answer.get("decision") or ""
        action = _clip(f"{action_core} {mode_line}".strip(), 280 if depth != "quick" else 160)
        avoid = _clip(f"Do not: {avoid_text}.", 220 if depth != "quick" else 140)
        decision_block = profile_bridge or base_answer.get("decision", "")
        if mode_line and decision_block:
            decision_block = f"{decision_block} {mode_line}"
        decision_block = _clip(decision_block, 520 if depth == "deep" else 360)

        repeat_warn = question_assessment.get("weak_reading_warning")
        explanation = _clip(structural_body + (f" {repeat_warn}" if repeat_warn else ""), 720 if depth == "deep" else 520)

        why = (
            f"The main thread is «{dom_name}» in «{dom_pos_title}» — that is where the answer to your question concentrates."
        )
        continue_hint = (
            "You can draw one clarifying card, save the takeaway, or open Compatibility if this is about someone."
        )
    else:
        summary = (
            f"Расклад «{spread_title}» в целом упирается в позицию «{dom_pos_title}»: "
            f"карта «{dom_name}» ({dom_card.orientation if dom_card else ''}) — {dominant_meaning}"
        )
        summary = _clip(summary, 420 if depth != "quick" else 260)
        q_line = _clip(question, 160)
        structural_body = f"{structural.get('conflict_note', '')} Твой вопрос — «{q_line}» — читается как про: {goal_phrase}."
        if today_context and today_context.strip():
            structural_body += f" Контекст дня: {_clip(today_context.strip(), 140)}"
        core_insight = (
            f"Главный узел в позиции «{dom_pos_title}»: расклад просит считать этот слот рычагом, "
            f"а не делать все карты одинаково громкими."
        )
        avoid_card = None
        for c in cards:
            pid = c.position.id if isinstance(c.position, core_models.TarotSpreadPosition) else ""
            if structural.get("tension_position_id") and pid == structural.get("tension_position_id"):
                avoid_card = c
                break
        if avoid_card is None:
            for c in cards:
                pid = (c.position.id if isinstance(c.position, core_models.TarotSpreadPosition) else "").lower()
                if any(k in pid for k in ("risk", "block", "harm", "illusion", "nuance")):
                    avoid_card = c
                    break
        avoid_text = (
            _meaning_snippet(avoid_card.meaning, 140)
            if avoid_card
            else "не превращать разбор в предсказание чужого точного шага или даты"
        )
        action_core = base_answer.get("today") or base_answer.get("decision") or ""
        action = _clip(f"{action_core} {mode_line}".strip(), 280 if depth != "quick" else 160)
        avoid = _clip(f"Не делай: {avoid_text}.", 220 if depth != "quick" else 140)
        decision_block = profile_bridge or base_answer.get("decision", "")
        if mode_line and decision_block:
            decision_block = f"{decision_block} {mode_line}"
        decision_block = _clip(decision_block, 520 if depth == "deep" else 360)

        repeat_warn = question_assessment.get("weak_reading_warning")
        explanation = _clip(structural_body + (f" {repeat_warn}" if repeat_warn else ""), 720 if depth == "deep" else 520)

        why = (
            f"Главный акцент — карта «{dom_name}» в позиции «{dom_pos_title}»: через неё читается суть ответа на твой вопрос."
        )
        continue_hint = (
            "Можно уточнить одной картой, сохранить вывод или открыть совместимость, если вопрос про человека."
        )

    remapped = {
        "clarity": summary,
        "explanation": explanation,
        "forecast": core_insight,
        "decision": decision_block,
        "today": action,
    }

    weights_note = ""
    interpretation = {
        "summary": remapped["clarity"],
        "core_insight": remapped["forecast"],
        "profile_bridge": decision_block,
        "action": action,
        "avoid": avoid,
        "continue_hint": continue_hint,
        "why_outline": why,
        "position_weights_note": weights_note,
    }

    return remapped, interpretation


CLARIFICATION_GOALS = frozenset({"blind_spot", "next_step", "risk", "boundary"})


def clarification_goal_label(goal: str, *, locale: str | None) -> str:
    g = (goal or "next_step").strip().lower()
    if g not in CLARIFICATION_GOALS:
        g = "next_step"
    if _is_en(locale):
        labels = {
            "blind_spot": "what I do not see",
            "next_step": "the next step",
            "risk": "where the risk is",
            "boundary": "a healthy boundary",
        }
        return labels[g]
    labels = {
        "blind_spot": "что я не вижу",
        "next_step": "следующий шаг",
        "risk": "где риск",
        "boundary": "здоровая граница",
    }
    return labels[g]


def compose_guidance_clarification(
    *,
    parent_question: str,
    parent_summary: str,
    clarification_goal: str,
    spread_title: str,
    cards: list[core_models.TarotSpreadCard],
    lane: str,
    base_answer: dict[str, str],
    core_profile: dict[str, Any] | None,
    topic: str | None,
    learning_context: dict[str, Any] | None,
    locale: str | None = None,
) -> tuple[dict[str, str], dict[str, Any]]:
    """One-card add-on tied to a completed main guidance reading."""

    g = (clarification_goal or "next_step").strip().lower()
    if g not in CLARIFICATION_GOALS:
        g = "next_step"
    glabel = clarification_goal_label(g, locale=locale)
    dom_card = cards[0] if cards else None
    dom_name = dom_card.card.name if dom_card else ""
    dom_pos_title = ""
    if dom_card:
        p = dom_card.position
        dom_pos_title = p.title if isinstance(p, core_models.TarotSpreadPosition) else str(p)
    dominant_meaning = _meaning_snippet(dom_card.meaning, 200) if dom_card else ""
    profile_bridge = _extract_profile_bridge(core_profile, topic=topic, lane=lane, locale=locale)
    mode_line = _learning_mode_line(learning_context, locale=locale)
    pq = _clip(parent_question, 200)
    ps = _clip(parent_summary, 220)

    if _is_en(locale):
        summary = (
            f"Clarification draw ({glabel}): «{dom_name}» in «{dom_pos_title}» — {dominant_meaning}"
        )
        summary = _clip(summary, 380)
        explanation = (
            f"This card answers the clarification focus, not a new fortune-telling question. "
            f"Original ask: «{pq}». Previous spread line: {ps}"
        )
        goal_lines = {
            "blind_spot": "The blind spot to name is what you avoid facing while replaying the same story.",
            "next_step": "The next step is the smallest move that creates feedback without escalating drama.",
            "risk": "The risk to respect is where you trade clarity for soothing fantasy or control.",
            "boundary": "The boundary to hold is where you stop over-functioning for someone else's ambiguity.",
        }
        core_insight = goal_lines.get(g, goal_lines["next_step"])
        avoid = _clip(
            "Do not pull another card to chase a prettier answer; return to one action from the main reading.",
            200,
        )
        action_core = base_answer.get("today") or base_answer.get("decision") or ""
        action = _clip(f"{action_core} {mode_line}".strip(), 240)
        decision_block = profile_bridge or _clip(base_answer.get("decision", ""), 280)
        continue_hint = "Clarification path is complete — start a new full spread if you need another frame."
        why = (
            f"Focus card «{dom_name}» targets «{glabel}» on top of your prior layout; "
            f"it does not replace the main reading."
        )
    else:
        summary = f"Уточнение ({glabel}): «{dom_name}» в позиции «{dom_pos_title}» — {dominant_meaning}"
        summary = _clip(summary, 380)
        explanation = (
            f"Эта карта отвечает на узкий фокус уточнения, а не на новый «прогноз». "
            f"Исходный вопрос: «{pq}». Линия прошлого разбора: {ps}"
        )
        goal_lines = {
            "blind_spot": "Слепое пятно — то, что ты избегаешь замечать, пока крутишь тот же сценарий.",
            "next_step": "Следующий шаг — самый маленький ход, который даёт обратную связь без раздувания драмы.",
            "risk": "Риск — там, где ты меняешь ясность на успокоение фантазией или контролем.",
            "boundary": "Граница — где ты перестаёшь делать работу за чужую неопределённость.",
        }
        core_insight = goal_lines.get(g, goal_lines["next_step"])
        avoid = _clip(
            "Не перетягивай карты ради «лучшего» ответа — вернись к одному действию из основного разбора.",
            220,
        )
        action_core = base_answer.get("today") or base_answer.get("decision") or ""
        action = _clip(f"{action_core} {mode_line}".strip(), 240)
        decision_block = profile_bridge or _clip(base_answer.get("decision", ""), 280)
        continue_hint = "Уточнение к этому раскладу уже использовано — новый полный разбор только через новую сессию."
        why = (
            f"Карта «{dom_name}» в позиции «{dom_pos_title}» бьёт в фокус «{glabel}» поверх предыдущего расклада; "
            f"она не заменяет основной ответ."
        )

    weights_note = (
        "Clarification is one card only; weight is 100% on that slot."
        if _is_en(locale)
        else "Уточнение — одна карта; вес целиком на этой позиции."
    )

    remapped = {
        "clarity": summary,
        "explanation": _clip(explanation, 560),
        "forecast": core_insight,
        "decision": decision_block,
        "today": action,
    }
    interpretation = {
        "summary": remapped["clarity"],
        "core_insight": remapped["forecast"],
        "profile_bridge": decision_block,
        "action": action,
        "avoid": avoid,
        "continue_hint": continue_hint,
        "why_outline": why,
        "position_weights_note": weights_note,
    }
    return remapped, interpretation
