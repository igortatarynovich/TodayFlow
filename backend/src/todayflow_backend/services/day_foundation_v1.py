"""Day Foundation — synthesis of registered Day Sources (L1/L2).

Architecture (docs/DAY_SOURCES_CANON.md):
  Day Sources → Day Foundation → Day Story

Foundation does not own school logic. It reads SourceResult payloads from the
Day Source Registry and builds a shared day plot + essence.

`day_foundation_v1` remains the wire contract name for Today; calculation_version
tracks the sources-backed synthesizer.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from todayflow_backend.services.day_sources import DaySourceInputs, collect_foundation_sources
from todayflow_backend.services.day_sources.registry import get_default_registry

DAY_FOUNDATION_V1 = "day_foundation_v1"
DAY_FOUNDATION_CALC_VERSION = "day-foundation-v1.1-sources"


def _clip(text: str, limit: int) -> str:
    t = re.sub(r"\s+", " ", str(text or "").strip())
    if len(t) <= limit:
        return t
    return t[: limit - 1].rstrip() + "…"


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


def _beats_from_ingresses(ingresses: list[Any], *, evidence_family: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
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
            evidence_ref=f"source.{evidence_family}.ingresses",
        )
        if beat:
            out.append(beat)
    return out


def _beats_from_aspects(aspects: list[Any], *, evidence_family: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for idx, row in enumerate(aspects or []):
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
            evidence_ref=f"source.{evidence_family}.aspects",
        )
        if beat:
            out.append(beat)
    return out


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
        "Сегодня в небе складывается смена процессов. " + " ".join(parts),
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


def _numerology_summary(payload: dict[str, Any] | None) -> str:
    if not isinstance(payload, dict):
        return ""
    n = payload.get("universal_day")
    if n is None:
        return ""
    return _clip(f"Универсальное число дня — {n}.", 120)


def _weekday_summary(payload: dict[str, Any] | None) -> str:
    if not isinstance(payload, dict):
        return ""
    ruler = payload.get("ruler_planet_ru") or payload.get("ruler_planet")
    if not ruler:
        return ""
    return _clip(f"Управитель дня недели — {ruler}.", 120)


def _essence_from_layers(
    *,
    astro_summary: str,
    lunar_summary: str,
    astro_beats: list[dict[str, Any]],
    lunar_beats: list[dict[str, Any]],
    numerology_summary: str = "",
    weekday_summary: str = "",
) -> dict[str, Any]:
    """Суть дня — вывод из foundation-слоёв, не пересказ транзитов."""
    evidence_ids = [b["id"] for b in astro_beats[:3]] + [b["id"] for b in lunar_beats[:3]]
    if astro_summary:
        evidence_ids.append("astro.summary")
    if lunar_summary:
        evidence_ids.append("lunar.summary")
    if numerology_summary:
        evidence_ids.append("numerology.universal_day")
    if weekday_summary:
        evidence_ids.append("weekday.ruler")

    if not astro_summary and not lunar_summary:
        # Shared calendar layers alone do not form a literary essence yet.
        return {
            "theme": "",
            "story_ru": "",
            "evidence_ids": [],
        }

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
        if not astro_summary or lunar_summary[:48].lower() not in astro_summary.lower():
            paragraphs.append(lunar_summary)

    soft = " ".join(x for x in (weekday_summary, numerology_summary) if x)
    if soft:
        paragraphs.append(soft)

    if astro_summary and lunar_summary:
        paragraphs.append(
            "Суть дня рождается на стыке этих слоёв: "
            "небо задаёт, какие процессы меняют направление, "
            "а Луна — как это проживается и куда легче направить внимание."
        )

    return {
        "theme": theme,
        "story_ru": _clip(" ".join(paragraphs), 720),
        "evidence_ids": evidence_ids[:12],
    }


def _ok_payload(bundle: dict[str, Any], family_id: str) -> dict[str, Any] | None:
    sources = bundle.get("sources") if isinstance(bundle.get("sources"), dict) else {}
    row = sources.get(family_id)
    if not isinstance(row, dict) or row.get("status") != "ok":
        return None
    payload = row.get("payload")
    return payload if isinstance(payload, dict) else None


def build_day_foundation_from_sources(
    source_bundle: dict[str, Any] | None,
) -> dict[str, Any]:
    """Synthesize Day Foundation from a Registry bundle (no school logic here)."""
    bundle = source_bundle if isinstance(source_bundle, dict) else {}
    west = _ok_payload(bundle, "western_astrology") or {}
    moon = _ok_payload(bundle, "moon") or {}
    numerology = _ok_payload(bundle, "numerology")
    weekday = _ok_payload(bundle, "weekday_ruler")

    astro_beats: list[dict[str, Any]] = []
    lunar_beats: list[dict[str, Any]] = []

    astro_beats.extend(_beats_from_ingresses(west.get("ingresses") or [], evidence_family="western_astrology"))
    for row in (west.get("retrogrades") or [])[:4]:
        if not isinstance(row, dict):
            continue
        planet_ru = str(row.get("planet_ru") or row.get("planet") or "")
        beat = _beat(
            beat_id=f"retro.{row.get('planet') or planet_ru}",
            kind="retrograde",
            title=f"{planet_ru} ретрограден" if planet_ru else "Ретроградность",
            story_ru=str(row.get("story_ru") or ""),
            evidence_ref="source.western_astrology.retrogrades",
        )
        if beat:
            astro_beats.append(beat)
    astro_beats.extend(
        _beats_from_aspects((west.get("sky_aspects") or [])[:3], evidence_family="western_astrology")
    )

    lunar_beats.extend(_beats_from_ingresses(moon.get("ingresses") or [], evidence_family="moon"))
    lunar_beats.extend(
        _beats_from_aspects((moon.get("lunar_aspects") or [])[:3], evidence_family="moon")
    )
    for row in (moon.get("timed_lunar_aspects") or [])[:3]:
        if not isinstance(row, dict):
            continue
        title = str(row.get("title") or "")
        exact = str(row.get("exact_time") or "")
        story = f"{title} · {exact}" if title and exact else title or exact
        beat = _beat(
            beat_id=f"timed.{row.get('id') or exact}",
            kind="timed_aspect",
            title=title or "Лунный аспект",
            story_ru=story,
            evidence_ref="source.moon.timed_lunar_aspects",
        )
        if beat:
            lunar_beats.append(beat)

    phase = moon.get("lunar_phase") if isinstance(moon.get("lunar_phase"), dict) else None
    moon_sign = moon.get("moon_sign") if isinstance(moon.get("moon_sign"), dict) else None
    voc = moon.get("void_of_course") if isinstance(moon.get("void_of_course"), dict) else None
    if not moon_sign:
        for b in lunar_beats:
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
                "evidence_ref": "source.moon.phase",
            },
        )

    if isinstance(voc, dict) and voc.get("status") == "ok" and voc.get("in_void_of_course"):
        lunar_beats.append(
            {
                "id": "lunar.void_of_course",
                "kind": "void_of_course",
                "title": "Луна без курса",
                "story_ru": _clip(
                    "Луна без курса: после последнего мажорного аспекта до смены знака "
                    "лучше не форсировать новые старты — дождаться ясного перехода.",
                    240,
                ),
                "evidence_ref": "source.moon.void_of_course",
            }
        )

    astro_beats = astro_beats[:6]
    lunar_beats = [b for b in lunar_beats if b.get("story_ru") or b.get("title")][:6]

    astro_summary = _astro_summary(astro_beats)
    lunar_summary = _lunar_summary(phase=phase, moon_sign=moon_sign, beats=lunar_beats)
    numerology_summary = _numerology_summary(numerology)
    weekday_summary = _weekday_summary(weekday)
    essence = _essence_from_layers(
        astro_summary=astro_summary,
        lunar_summary=lunar_summary,
        astro_beats=astro_beats,
        lunar_beats=lunar_beats,
        numerology_summary=numerology_summary,
        weekday_summary=weekday_summary,
    )

    ok_ids = list(bundle.get("ok_family_ids") or [])
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
            "void_of_course": voc,
            "beats": lunar_beats,
            "summary_ru": lunar_summary,
        },
        "numerology": {
            "universal_day": numerology.get("universal_day") if numerology else None,
            "summary_ru": numerology_summary,
            # Personal numbers stay in source payload / Personal layer — not Foundation plot.
            "personal_day": numerology.get("personal_day") if numerology else None,
        }
        if numerology
        else None,
        "weekday": {
            "weekday": weekday.get("weekday") if weekday else None,
            "ruler_planet": weekday.get("ruler_planet") if weekday else None,
            "ruler_planet_ru": weekday.get("ruler_planet_ru") if weekday else None,
            "summary_ru": weekday_summary,
        }
        if weekday
        else None,
        "essence": essence,
        "source_inputs": {
            "has_astro": bool(astro_beats),
            "has_lunar": bool(lunar_summary or lunar_beats),
            "has_numerology": bool(numerology),
            "has_weekday": bool(weekday),
            "has_essence": bool(essence.get("story_ru")),
            "ok_family_ids": ok_ids,
        },
        "source_bundle": {
            "contract_version": bundle.get("contract_version"),
            "ok_family_ids": ok_ids,
        },
    }


def build_day_foundation_v1(
    celestial_events: dict[str, Any] | None,
    *,
    target_date: date | None = None,
    birth_date: date | None = None,
    timezone: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    locale: str = "ru",
) -> dict[str, Any]:
    """Compatibility entry: celestial_events → Registry → Foundation.

    Prefer calling collect_foundation_sources + build_day_foundation_from_sources
    when wiring new pipelines.
    """
    ce = celestial_events if isinstance(celestial_events, dict) else {}
    inputs = DaySourceInputs(
        target_date=target_date or date.today(),
        timezone=timezone,
        lat=lat,
        lon=lon,
        birth_date=birth_date,
        celestial_events=ce or None,
        locale=locale,
    )
    # Empty ce: still run date-only families (numerology, weekday).
    if not ce:
        # Registry western/moon need celestial_events; date families still resolve.
        bundle = collect_foundation_sources(inputs, registry=get_default_registry())
        return build_day_foundation_from_sources(bundle)

    bundle = collect_foundation_sources(inputs, registry=get_default_registry())
    return build_day_foundation_from_sources(bundle)


def foundation_to_interpretation_claims(foundation: dict[str, Any]) -> list[dict[str, Any]]:
    """Map foundation into day_story interpretation claim rows (kind sky/support)."""
    claims: list[dict[str, Any]] = []
    if not isinstance(foundation, dict):
        return claims

    astro = foundation.get("astro") if isinstance(foundation.get("astro"), dict) else {}
    lunar = foundation.get("lunar") if isinstance(foundation.get("lunar"), dict) else {}
    essence = foundation.get("essence") if isinstance(foundation.get("essence"), dict) else {}
    numerology = (
        foundation.get("numerology") if isinstance(foundation.get("numerology"), dict) else {}
    )
    weekday = foundation.get("weekday") if isinstance(foundation.get("weekday"), dict) else {}

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

    num_line = _clip(str(numerology.get("summary_ru") or ""), 160)
    if num_line:
        claims.append(
            {
                "id": "claim.foundation.numerology",
                "kind": "support",
                "text": num_line,
                "evidence_ids": ["source.numerology.universal_day"],
                "domain": None,
                "layer": "numerology",
            }
        )

    wd_line = _clip(str(weekday.get("summary_ru") or ""), 160)
    if wd_line:
        claims.append(
            {
                "id": "claim.foundation.weekday",
                "kind": "support",
                "text": wd_line,
                "evidence_ids": ["source.weekday_ruler"],
                "domain": None,
                "layer": "weekday",
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
