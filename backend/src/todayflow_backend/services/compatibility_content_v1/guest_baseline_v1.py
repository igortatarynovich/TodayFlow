"""Finished guest content — pair-specific, not a truncated registered surface."""

from __future__ import annotations

from typing import Any

from todayflow_backend.data.astrology import lookup_sign_metadata
from todayflow_backend.i18n import localized_sign_name
from todayflow_backend.services.compatibility_content_v1.contracts import GuestContentV1
from todayflow_backend.services.compatibility_content_v1.source_depth import (
    depth_honesty_line,
    resolve_source_depth,
)
from todayflow_backend.services.sign_compatibility_product import normalize_relationship_context

_ELEMENT_ATTRACTION: dict[frozenset[str], str] = {
    frozenset({"fire", "air"}): (
        "Вас тянет скорость: один разгоняет, другой подхватывает идею — вместе легко "
        "затеять вечер или поездку без долгого планирования."
    ),
    frozenset({"earth", "water"}): (
        "Притяжение через заботу и тело: ужин, дом, тишина рядом — без громких жестов, "
        "но с ощущением «здесь можно выдохнуть»."
    ),
    frozenset({"fire", "water"}): (
        "Сильный контраст: вспышка и глубина. Когда получается — почти электричество; "
        "когда нет — оба чувствуют, что «не попали»."
    ),
    frozenset({"earth", "air"}): (
        "Один тянет к делу и опоре, другой — к разговору и вариантам. Притяжение часто "
        "через «докажи / удиви» — и через спор, который не отпускает."
    ),
    frozenset({"fire", "earth"}): (
        "Один жмёт на газ, другой проверяет почву. Притяжение — в том, что вместе вы "
        "можете и рискнуть, и не развалиться на полпути."
    ),
    frozenset({"air", "water"}): (
        "Слова и чувства встречаются: один проговаривает, другой проживает. Тянет "
        "тот разговор, после которого становится чуть теплее — или чуть больнее."
    ),
}

_SAME_ELEMENT: dict[str, str] = {
    "fire": "Оба быстро загораетесь — притяжение в общем темпе и желании «сделать сейчас».",
    "earth": "Опора и предсказуемость: вас тянет к тому, что можно потрогать и проверить.",
    "air": "Разговор как кислород: притяжение через идеи, шутки и «давай ещё пять минут».",
    "water": "Тихая глубина: вас тянет близость без спектакля — взгляд, пауза, общий угол.",
}

_MODALITY_RISK: dict[frozenset[str], str] = {
    frozenset({"cardinal", "fixed"}): (
        "Риск — гонка: один уже решил, второй ещё «держит». В быту это выглядит как "
        "«почему ты опять тянешь» против «почему ты давишь»."
    ),
    frozenset({"fixed", "mutable"}): (
        "Риск — жёсткость против гибкости: один стоит на своём, второй уходит в варианты "
        "и кажется ненадёжным, хотя просто ищет выход."
    ),
    frozenset({"cardinal", "mutable"}): (
        "Риск — старт без добивания: энергия есть, финиша нет. Обещания и планы "
        "рассыпаются, если не зафиксировать следующий шаг."
    ),
}

_SAME_MODALITY_RISK: dict[str, str] = {
    "cardinal": "Оба хотите вести — спор «кто первый» легко съедает вечер.",
    "fixed": "Оба упираетесь — молчание и принцип вместо маленькой уступки.",
    "mutable": "Оба уходите в варианты — решение откладывается, напряжение копится.",
}

_CTX_ADVICE: dict[str, str] = {
    "just_met": "На ближайшую неделю договоритесь о одном простом следующем шаге — без проверки «насколько всё серьёзно».",
    "mutual_attraction": "Назовите вслух, чего хотите от ближайших двух встреч — темп часто важнее красивых слов.",
    "in_relationship": "Раз в неделю коротко сверяйтесь: что сейчас перегружает, что поддерживает — без разбора «всё сразу».",
    "unclear": "Сначала проясните статус одним честным разговором на 15 минут — не в переписке между делами.",
    "conflict_distance": "Не чините всё за раз: выберите один конкретный срыв и разберите только его.",
    "split_but_pull": "Если тянет обратно — сначала границы и темп, потом близость. Иначе старый сценарий повторится.",
    "unspecified": "Выберите один бытовой момент на этой неделе, где вы сознательно замедлитесь и услышите друг друга.",
}


def _pair_score(fe: str, te: str, fm: str, tm: str, same_sign: bool) -> int:
    base = 62
    if fe == te:
        base += 6
    elif {fe, te} in ({"fire", "air"}, {"earth", "water"}):
        base += 8
    elif {fe, te} == {"fire", "water"}:
        base += 4
    else:
        base += 2
    if fm == tm:
        base += 3 if fm != "fixed" else -1
    else:
        base -= 2
    if same_sign:
        base += 2
    return max(48, min(88, base))


def _attraction_line(fe: str, te: str) -> str:
    if fe and te and fe == te:
        return _SAME_ELEMENT.get(fe, "Вас тянет похожий темп и знакомое ощущение «мы на одной волне».")
    key = frozenset({fe, te})
    return _ELEMENT_ATTRACTION.get(
        key,
        "Притяжение есть, но оно держится на контрасте характеров — и легко срывается без договорённостей.",
    )


def _risk_line(fm: str, tm: str) -> str:
    if fm and tm and fm == tm:
        return _SAME_MODALITY_RISK.get(
            fm,
            "Риск — застревать в одном сценарии: спор или уход, без третьего пути.",
        )
    return _MODALITY_RISK.get(
        frozenset({fm, tm}),
        "Риск — разные скорости реакции: один уже в теме, второй ещё внутри. Без паузы оба остаются обижены.",
    )


def _headline(from_name: str, to_name: str, fe: str, te: str, same_sign: bool) -> str:
    if same_sign:
        return f"{from_name} и {to_name}: зеркало — тепло и слепые зоны рядом"
    if fe == te:
        return f"{from_name} × {to_name}: общий язык стихии, свой ритм спора"
    if {fe, te} == {"fire", "water"}:
        return f"{from_name} × {to_name}: сильный ток — и быстрый перегрев"
    return f"{from_name} × {to_name}: притяжение есть, темп решает всё"


def build_guest_content_v1(
    *,
    from_sign: str,
    to_sign: str,
    relationship_context: str | None = None,
    locale: str = "ru",
    source_depth: str | None = None,
    has_birth_dates: bool = False,
    score: int | None = None,
) -> GuestContentV1:
    """Deterministic finished guest contract for zodiac / birth-date depth."""
    from_meta = lookup_sign_metadata(from_sign) or {}
    to_meta = lookup_sign_metadata(to_sign) or {}
    fe = str(from_meta.get("element") or "").lower()
    te = str(to_meta.get("element") or "").lower()
    fm = str(from_meta.get("modality") or "").lower()
    tm = str(to_meta.get("modality") or "").lower()
    from_name = localized_sign_name(from_sign, locale=locale)
    to_name = localized_sign_name(to_sign, locale=locale)
    same_sign = (from_sign or "").strip().lower() == (to_sign or "").strip().lower()
    ctx = normalize_relationship_context(relationship_context)
    depth = source_depth or resolve_source_depth(
        has_birth_dates=has_birth_dates,
        has_signs=True,
    )
    honesty = depth_honesty_line(depth, locale=locale)  # type: ignore[arg-type]
    sc = int(score) if score is not None else _pair_score(fe, te, fm, tm, same_sign)
    attraction = _attraction_line(fe, te)
    risk = _risk_line(fm, tm)
    advice = _CTX_ADVICE.get(ctx, _CTX_ADVICE["unspecified"])
    headline = _headline(from_name, to_name, fe, te, same_sign)

    if same_sign:
        summary = (
            f"Одинаковые знаки дают узнаваемость: вы быстрее понимаете жесты друг друга и так же "
            f"быстрее задеваете слепые зоны. {honesty} "
            f"В быту это видно, когда оба молчат по одной причине или оба ускоряются в споре. "
            f"Сильная сторона — общее чувство «нас поняли без перевода»; слабая — некому "
            f"принести другой взгляд, если вы застряли."
        )
    else:
        summary = (
            f"Между {from_name} и {to_name} читается своя динамика темпа и тепла. {honesty} "
            f"На практике важнее не «подходят / не подходят», а кто обычно ускоряет разговор, "
            f"кто уходит в себя и что происходит после ссоры на следующий день. "
            f"Если поймать эти роли рано, притяжение работает на вас; если нет — одни и те же "
            f"сцены повторяются уже через пару недель."
        )

    return GuestContentV1(
        source_depth=depth,  # type: ignore[arg-type]
        locale=locale if locale.startswith("ru") else "ru",
        headline=headline,
        score=sc,
        summary=summary,
        attraction=attraction,
        main_risk=risk,
        practical_advice=advice,
        locked_preview=[
            "Эмоциональная динамика и общение",
            "Конфликты и уязвимое место пары",
            "Что помогает отношениям работать",
        ],
        confidence="low" if depth == "zodiac_only" else "medium",
    )


def guest_content_to_legacy_surface_bits(content: GuestContentV1) -> dict[str, Any]:
    """Map guest contract into fields the current UI already understands."""
    return {
        "score_tagline": content.headline,
        "overview_paragraphs": [content.summary, content.attraction],
        "teaser": {
            "attraction": content.attraction,
            "main_risk": content.main_risk,
            "practical_advice": content.practical_advice,
        },
        "locked_preview": list(content.locked_preview),
        "content_v1": content.model_dump(),
        "source_depth": content.source_depth,
        "confidence": content.confidence,
        "honesty_line": depth_honesty_line(content.source_depth, locale=content.locale),
    }
