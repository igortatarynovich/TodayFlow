"""Day foundation v1 — objective day plot before personal story / literary prose.

Two primary layers (same for everyone), then essence as their synthesis:
1. Astrological context — planetary structure of the day (ingresses, stations/retro,
   sky aspects). Answers: what themes/process begin, end, or change direction.
2. Lunar context — emotional/behavioral rhythm (phase, lunar day, moon sign,
   moon aspects / guidance). Answers: how the day is lived and felt.

Personal natal activation is NOT part of this foundation — that comes later.
"""

from __future__ import annotations

import re
from typing import Any

DAY_FOUNDATION_V1 = "day_foundation_v1"
DAY_FOUNDATION_CALC_VERSION = "day-foundation-v1.0"

_MOON_TOKENS = ("moon", "луна", "лун")


def _clip(text: str, limit: int) -> str:
    t = re.sub(r"\s+", " ", str(text or "").strip())
    if len(t) <= limit:
        return t
    return t[: limit - 1].rstrip() + "…"


def _is_moonish(text: str | None) -> bool:
    low = (text or "").lower()
    return any(tok in low for tok in _MOON_TOKENS)


def _beat(
    *,
    beat_id: str,
    kind: str,
    title: str,
    story_ru: str,
    evidence_ref: str,
) -> dict[str, Any] | None:
    title_c = _clip(title, 120)
    story_c = _clip(story_ru, 280)
    if not title_c and not story_c:
        return None
    return {
        "id": beat_id,
        "kind": kind,
        "title": title_c,
        "story_ru": story_c or title_c,
        "evidence_ref": evidence_ref,
    }


def _split_aspects(sky_aspects: list[Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Moon-involved aspects → lunar; the rest → astro."""
    astro: list[dict[str, Any]] = []
    lunar: list[dict[str, Any]] = []
    for idx, row in enumerate(sky_aspects or []):
        if not isinstance(row, dict):
            continue
        title = str(row.get("title") or "")
        story = str(row.get("story_ru") or "")
        aid = str(row.get("id") or f"aspect-{idx}")
        beat = _beat(
            beat_id=f"aspect.{aid}",
            kind="aspect",
            title=title,
            story_ru=story,
            evidence_ref=f"celestial_events.sky_aspects.{aid}",
        )
        if not beat:
            continue
        if _is_moonish(title) or _is_moonish(story):
            lunar.append(beat)
        else:
            astro.append(beat)
    return astro, lunar


def _split_ingresses(ingresses: list[Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    astro: list[dict[str, Any]] = []
    lunar: list[dict[str, Any]] = []
    for row in ingresses or []:
        if not isinstance(row, dict):
            continue
        planet = str(row.get("planet") or "")
        planet_ru = str(row.get("planet_ru") or planet)
        sign_ru = str(row.get("sign_ru") or row.get("sign") or "")
        story = str(row.get("story_ru") or "")
        title = (
            f"{planet_ru} → {sign_ru}" if planet_ru and sign_ru else planet_ru or story[:80]
        )
        beat = _beat(
            beat_id=f"ingress.{planet or planet_ru}",
            kind="ingress",
            title=title,
            story_ru=story,
            evidence_ref="celestial_events.ingresses",
        )
        if not beat:
            continue
        if _is_moonish(planet) or _is_moonish(planet_ru):
            lunar.append(beat)
        else:
            astro.append(beat)
    return astro, lunar


def _astro_summary(beats: list[dict[str, Any]]) -> str:
    if not beats:
        return ""
    leads = [b for b in beats if b.get("kind") in ("ingress", "retrograde", "station")][:2]
    if not leads:
        leads = beats[:2]
    parts: list[str] = []
    for b in leads:
        story = _clip(str(b.get("story_ru") or ""), 160)
        if story:
            parts.append(story)
    if len(beats) > len(leads):
        rest = beats[len(leads) : len(leads) + 1]
        for b in rest:
            title = _clip(str(b.get("title") or ""), 80)
            if title:
                parts.append(f"Также в картине дня: {title}.")
    if not parts:
        return ""
    if len(parts) == 1:
        return _clip(
            f"Астрологический каркас дня задаёт одно главное движение. {parts[0]}",
            420,
        )
    return _clip(
        "Сегодня в небе складывается смена процессов. "
        + " ".join(parts),
        480,
    )


def _lunar_summary(
    *,
    phase: dict[str, Any] | None,
    moon_sign: dict[str, Any] | None,
    beats: list[dict[str, Any]],
) -> str:
    bits: list[str] = []
    if isinstance(phase, dict):
        name = _clip(str(phase.get("name") or ""), 80)
        guidance = _clip(str(phase.get("guidance") or phase.get("themes") or ""), 160)
        if name and guidance:
            bits.append(f"Луна сейчас — {name}: {guidance}")
        elif name:
            bits.append(f"Луна сейчас — {name}.")
        cycle = phase.get("cycle_day")
        if isinstance(cycle, (int, float)) and cycle > 0:
            bits.append(f"Лунный день цикла — около {int(round(float(cycle)))}.")
        nxt = phase.get("next_phase") if isinstance(phase.get("next_phase"), dict) else None
        if nxt and nxt.get("name") is not None and nxt.get("in_days") is not None:
            try:
                days = float(nxt["in_days"])
            except (TypeError, ValueError):
                days = None
            if days is not None and days >= 0:
                if days < 1:
                    bits.append(f"Ближайший переход фазы — {nxt['name']}, уже сегодня.")
                else:
                    bits.append(f"Ближайший переход фазы — {nxt['name']}, через {int(days)} дн.")
    if isinstance(moon_sign, dict):
        sign_ru = _clip(str(moon_sign.get("sign_ru") or moon_sign.get("sign") or ""), 40)
        if sign_ru:
            bits.append(f"Луна в знаке {sign_ru} задаёт тон восприятия.")
    for b in beats[:2]:
        story = _clip(str(b.get("story_ru") or ""), 140)
        if story and story not in bits:
            bits.append(story)
    if not bits:
        return ""
    return _clip(" ".join(bits), 480)


def _essence_from_layers(
    *,
    astro_summary: str,
    lunar_summary: str,
    astro_beats: list[dict[str, Any]],
    lunar_beats: list[dict[str, Any]],
) -> dict[str, Any]:
    """Суть дня — вывод из двух слоёв, не пересказ транзитов."""
    evidence_ids = [b["id"] for b in astro_beats[:3]] + [b["id"] for b in lunar_beats[:3]]
    if isinstance(astro_summary, str) and astro_summary:
        evidence_ids.append("astro.summary")
    if isinstance(lunar_summary, str) and lunar_summary:
        evidence_ids.append("lunar.summary")

    if not astro_summary and not lunar_summary:
        return {
            "theme": "",
            "story_ru": "",
            "evidence_ids": [],
        }

    # Theme: prefer structural change from astro, else lunar rhythm.
    theme = ""
    for b in astro_beats:
        if b.get("kind") in ("ingress", "retrograde", "station"):
            title = _clip(str(b.get("title") or ""), 100)
            if title:
                theme = f"Смена перспективы: {title}"
                break
    if not theme and astro_beats:
        theme = _clip(str(astro_beats[0].get("title") or "Структура дня"), 120)
    if not theme and lunar_summary:
        theme = "Ритм дня задаёт Луна"
    theme = _clip(theme, 160)

    paragraphs: list[str] = []
    if astro_summary:
        paragraphs.append(astro_summary)
    if lunar_summary:
        # Avoid near-duplicate of astro moon ingress already told.
        if not astro_summary or lunar_summary[:48].lower() not in astro_summary.lower():
            paragraphs.append(lunar_summary)

    if astro_summary and lunar_summary:
        bridge = (
            "Суть дня рождается на стыке этих двух слоёв: "
            "небо задаёт, какие процессы меняют направление, "
            "а Луна — как это проживается и куда легче направить внимание."
        )
        paragraphs.append(bridge)

    return {
        "theme": theme,
        "story_ru": _clip(" ".join(paragraphs), 720),
        "evidence_ids": evidence_ids[:12],
    }


def build_day_foundation_v1(celestial_events: dict[str, Any] | None) -> dict[str, Any]:
    """Deterministic foundation from morning celestial_events only (no natal, no LLM)."""
    ce = celestial_events if isinstance(celestial_events, dict) else {}

    astro_beats: list[dict[str, Any]] = []
    lunar_beats: list[dict[str, Any]] = []

    ing_astro, ing_lunar = _split_ingresses(ce.get("ingresses") or [])
    astro_beats.extend(ing_astro)
    lunar_beats.extend(ing_lunar)

    for row in (ce.get("retrogrades") or [])[:4]:
        if not isinstance(row, dict):
            continue
        planet_ru = str(row.get("planet_ru") or row.get("planet") or "")
        beat = _beat(
            beat_id=f"retro.{row.get('planet') or planet_ru}",
            kind="retrograde",
            title=f"{planet_ru} ретрограден" if planet_ru else "Ретроградность",
            story_ru=str(row.get("story_ru") or ""),
            evidence_ref="celestial_events.retrogrades",
        )
        if beat:
            astro_beats.append(beat)

    asp_astro, asp_lunar = _split_aspects(ce.get("sky_aspects") or [])
    astro_beats.extend(asp_astro[:3])
    lunar_beats.extend(asp_lunar[:3])

    phase = ce.get("lunar_phase") if isinstance(ce.get("lunar_phase"), dict) else None
    moon_sign = ce.get("moon_sign") if isinstance(ce.get("moon_sign"), dict) else None
    # Prefer moon sign from lunar ingress if moon_sign missing.
    if not moon_sign:
        for b in ing_lunar:
            # title like "Луна → Стрелец"
            m = re.search(r"→\s*([А-ЯЁA-Za-z]+)", str(b.get("title") or ""))
            if m:
                moon_sign = {"sign_ru": m.group(1), "source": "ingress"}
                break

    if phase:
        lunar_beats.insert(
            0,
            {
                "id": "lunar.phase",
                "kind": "phase",
                "title": _clip(str(phase.get("name") or "Лунная фаза"), 80),
                "story_ru": _clip(
                    str(phase.get("guidance") or phase.get("themes") or phase.get("name") or ""),
                    240,
                ),
                "evidence_ref": "celestial_events.lunar_phase",
            },
        )

    # Cap beats for UI/LLM slimness
    astro_beats = astro_beats[:6]
    lunar_beats = [b for b in lunar_beats if b.get("story_ru") or b.get("title")][:6]

    astro_summary = _astro_summary(astro_beats)
    lunar_summary = _lunar_summary(phase=phase, moon_sign=moon_sign, beats=lunar_beats)
    essence = _essence_from_layers(
        astro_summary=astro_summary,
        lunar_summary=lunar_summary,
        astro_beats=astro_beats,
        lunar_beats=lunar_beats,
    )

    return {
        "contract_version": DAY_FOUNDATION_V1,
        "calculation_version": DAY_FOUNDATION_CALC_VERSION,
        "astro": {
            "beats": astro_beats,
            "summary_ru": astro_summary,
        },
        "lunar": {
            "phase": {
                "id": phase.get("id") if phase else None,
                "name": phase.get("name") if phase else None,
                "cycle_day": phase.get("cycle_day") if phase else None,
                "themes": phase.get("themes") if phase else None,
                "guidance": phase.get("guidance") if phase else None,
                "next_phase": phase.get("next_phase") if phase else None,
            }
            if phase
            else None,
            "moon_sign": moon_sign,
            "beats": lunar_beats,
            "summary_ru": lunar_summary,
        },
        "essence": essence,
        "source_inputs": {
            "has_astro": bool(astro_beats),
            "has_lunar": bool(lunar_summary or lunar_beats),
            "has_essence": bool(essence.get("story_ru")),
        },
    }


def foundation_to_interpretation_claims(foundation: dict[str, Any]) -> list[dict[str, Any]]:
    """Map foundation into day_story interpretation claim rows (kind sky/support)."""
    claims: list[dict[str, Any]] = []
    if not isinstance(foundation, dict):
        return claims

    astro = foundation.get("astro") if isinstance(foundation.get("astro"), dict) else {}
    lunar = foundation.get("lunar") if isinstance(foundation.get("lunar"), dict) else {}
    essence = foundation.get("essence") if isinstance(foundation.get("essence"), dict) else {}

    for b in (astro.get("beats") or [])[:4]:
        if not isinstance(b, dict):
            continue
        text = _clip(str(b.get("story_ru") or b.get("title") or ""), 280)
        if not text:
            continue
        claims.append(
            {
                "id": f"claim.foundation.astro.{b.get('id')}",
                "kind": "sky",
                "text": text,
                "evidence_ids": [str(b.get("evidence_ref") or b.get("id"))],
                "domain": None,
                "layer": "astro",
            }
        )

    for b in (lunar.get("beats") or [])[:4]:
        if not isinstance(b, dict):
            continue
        text = _clip(str(b.get("story_ru") or b.get("title") or ""), 280)
        if not text:
            continue
        claims.append(
            {
                "id": f"claim.foundation.lunar.{b.get('id')}",
                "kind": "sky",
                "text": text,
                "evidence_ids": [str(b.get("evidence_ref") or b.get("id"))],
                "domain": None,
                "layer": "lunar",
            }
        )

    theme = _clip(str(essence.get("theme") or ""), 160)
    story = _clip(str(essence.get("story_ru") or ""), 280)
    if theme or story:
        claims.append(
            {
                "id": "claim.foundation.essence",
                "kind": "axis",
                "text": story or theme,
                "evidence_ids": list(essence.get("evidence_ids") or [])[:8],
                "domain": None,
                "layer": "essence",
            }
        )
    return claims
