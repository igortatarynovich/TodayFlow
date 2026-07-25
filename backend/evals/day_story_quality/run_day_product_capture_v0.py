#!/usr/bin/env python3
"""Day product logic capture harness (sidecar packs).

Runs production-faithful day_story path with capture session enabled:
  interpretation → prompt → raw LLM (if configured + force_rebuild) → gates → final surfaces

Does NOT change prompts / color SoT / UI. Sidecar only.

Modes:
  --offline   No DB: interpretation + LLM/fallback for listed dates (synthetic sky/personal).
  --user-id   DB user: force_rebuild path via _build_day_story_record (needs app DB).

Usage:
  PYTHONPATH=src python evals/day_story_quality/run_day_product_capture_v0.py \\
    --offline --dates 2026-07-20,2026-07-21,2026-07-22

  PYTHONPATH=src python evals/day_story_quality/run_day_product_capture_v0.py \\
    --user-id 1 --dates 2026-07-20,2026-07-21 --force-rebuild
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / "src"))

os.environ.setdefault("LLM_HTTP_TIMEOUT_SECONDS", "120")
os.environ.setdefault("LLM_BACKGROUND_TIMEOUT_SECONDS", "180")

from todayflow_backend.services.day_story_capture_session_v0 import (  # noqa: E402
    day_story_capture_session,
)
from todayflow_backend.services.day_story_interpretation_v1 import (  # noqa: E402
    build_day_story_interpretation_v1,
)
from todayflow_backend.services.day_story_v1 import (  # noqa: E402
    DAY_STORY_PROMPT_VER,
    build_day_story_fallback_v1,
    build_day_story_llm_input,
    call_day_story_llm_v1,
    day_story_to_today_contract_v1,
)
from todayflow_backend.core.llm_openai_compatible import is_llm_chat_configured  # noqa: E402

DEFAULT_OUT = REPO / "docs" / "audits" / "day_story_capture" / "runs"


def _parse_dates(raw: str) -> list[date]:
    parts = [p.strip() for p in (raw or "").split(",") if p.strip()]
    if not parts:
        # default: last 7 calendar days ending "today" from env or 2026-07-25
        end = date.today()
        return [end - timedelta(days=i) for i in range(6, -1, -1)]
    out: list[date] = []
    for p in parts:
        out.append(date.fromisoformat(p))
    return out


def _sample_celestial(target: date) -> dict[str, Any]:
    """Deterministic-ish sky stub so offline packs are comparable across machines."""
    seed = target.toordinal()
    aspects = [
        {
            "id": "sun-square-moon",
            "title": "Солнце — квадрат — Луна",
            "story_ru": "Намерение и настроение расходятся — легко пообещать лишнее ради покоя.",
        },
        {
            "id": "venus-trine-jupiter",
            "title": "Венера — тригон — Юпитер",
            "story_ru": "Мягкое окно для тёплого жеста — без покупки одобрения.",
        },
        {
            "id": "mars-opposite-saturn",
            "title": "Марс — оппозиция — Сатурн",
            "story_ru": "Скорость упирается в рамки: качество важнее импульса.",
        },
    ]
    pick = aspects[seed % len(aspects)]
    return {
        "lunar_phase": {
            "name": "Растущая луна" if seed % 2 == 0 else "Убывающая луна",
            "guidance": "Собирай одно ясное намерение." if seed % 2 == 0 else "Отпускай лишнее.",
        },
        "sky_aspects": [pick],
        "ingresses": [
            {
                "planet": "mercury",
                "planet_ru": "Меркурий",
                "sign_ru": "Рак" if seed % 2 else "Лев",
                "story_ru": "Меняется тон разговоров — сначала смысл, потом скорость ответа.",
            }
        ],
        "daily_symbols": {
            "color": {
                "name": "Глубокий синий" if seed % 2 else "Лазурь",
                "benefit_ru": "Даёт опору, когда день просит не сорваться на суету.",
                "clothing_ru": "Один предмет одежды этого оттенка.",
                "accessory_ru": "Небольшой аксессуар.",
                "amount_ru": "Один акцент.",
                "avoid_color_ru": "Неоновый жёлтый" if seed % 2 else "Кислотно-оранжевый",
                "avoid_why_ru": "Разгоняет темп и мешает собранности.",
            },
            "stone": {"name": "Сапфир", "story_ru": "Тихий якорь."},
        },
    }


def _run_offline_day(target: date, *, out_dir: Path, redact: bool, force_llm: bool) -> Path | None:
    case_id = f"offline-{target.isoformat()}"
    ce = _sample_celestial(target)
    color_sym = (ce.get("daily_symbols") or {}).get("color") or {}
    stone_sym = (ce.get("daily_symbols") or {}).get("stone") or {}
    color = str(color_sym.get("name") or "")
    stone = str(stone_sym.get("name") or "")
    brief = {
        "anchor_summary": "День про ясный выбор вместо автоматического согласия.",
        "do_hint": "Сформулируй свою позицию до ответа.",
        "avoid_hint": "Не соглашайся сразу, чтобы сохранить гармонию.",
        "tempo_hint": "Сначала смысл, потом скорость.",
        "thread_head_topic": "relationships",
    }

    with day_story_capture_session(
        case_id=case_id,
        label="offline_synthetic",
        redact=redact,
        out_dir=out_dir,
        target_date=target.isoformat(),
        user_id="offline",
    ) as session:
        session.record_lifecycle(
            force_rebuild_used=True,
            get_calls_llm=False,
            refresh_calls_llm=True,
            mode="offline",
            llm_intentionally_skipped=not force_llm,
        )
        session.record_color(
            color_symbol=color_sym,
            color_name=color,
            preset_inputs={"source": "offline_sample_celestial.daily_symbols", "date": target.isoformat()},
        )
        interpretation = build_day_story_interpretation_v1(
            day_engine_brief=brief,
            ritual_context={"head_topic": "relationships", "mood": "calm"},
            intent_slice={"what_matters_line": "не потерять себя в чужом темпе"},
            color=color,
            stone=stone,
            celestial_events=ce,
            color_symbol=color_sym,
            stone_symbol=stone_sym,
            locale="ru",
            target_date=target,
            birth_date=date(1990, 3, 15),
        )
        session.record_interpretation_snapshot(interpretation)
        # Offline fixture: attach synthetic ritual card/number so chorus can be scored
        session._last_ritual = {
            "tarot_name_ru": "Отшельник",
            "tarot_main_id": "09",
            "numerology_value": 7,
            "head_topic": "relationships",
        }
        session.record_interpretive_chorus(
            interpretation=interpretation,
            day_foundation=interpretation.get("day_foundation")
            if isinstance(interpretation.get("day_foundation"), dict)
            else {},
            day_sky=interpretation.get("day_sky") if isinstance(interpretation.get("day_sky"), dict) else {},
            drivers=list((session.pack.get("day_spine") or {}).get("ranked_drivers") or []),
            natal_links=list((session.pack.get("day_spine") or {}).get("natal_links") or []),
            ritual_context=session._last_ritual,
        )
        llm_input = build_day_story_llm_input(
            day_engine_brief=brief,
            ritual_context={"head_topic": "relationships"},
            user_core_slim={"locale": "ru"},
            intent_slice={"what_matters_line": "не потерять себя в чужом темпе"},
            behavior_patterns=None,
            rhythm_context=None,
            color=color,
            stone=stone,
            locale="ru",
            interpretation=interpretation,
            celestial_events=ce,
            color_symbol=color_sym,
            stone_symbol=stone_sym,
            target_date=target,
            birth_date=date(1990, 3, 15),
        )
        used_fallback = True
        story: dict[str, Any] | None = None
        if force_llm and is_llm_chat_configured():
            story = call_day_story_llm_v1(llm_input, locale="ru", interpretation=interpretation)
            used_fallback = story is None
        if story is None:
            story = build_day_story_fallback_v1(
                day_engine_brief=brief,
                color=color,
                stone=stone,
                locale="ru",
                interpretation=interpretation,
                celestial_events=ce,
                color_symbol=color_sym,
                stone_symbol=stone_sym,
                target_date=target,
                birth_date=date(1990, 3, 15),
                ritual_context={"head_topic": "relationships"},
                intent_slice={"what_matters_line": "не потерять себя в чужом темпе"},
            )
        contract = day_story_to_today_contract_v1(story)
        session.record_final(story=story, contract=contract, used_fallback=used_fallback)
        try:
            from todayflow_backend.services.day_scenario_v1 import build_day_scenario_v1

            scenario = build_day_scenario_v1(
                interpretation=interpretation,
                day_events_pack=interpretation.get("day_events_pack")
                if isinstance(interpretation.get("day_events_pack"), dict)
                else None,
                day_thesis=interpretation.get("day_thesis")
                if isinstance(interpretation.get("day_thesis"), dict)
                else None,
                ritual_context=session._last_ritual,
                celestial_events=ce,
            )
            session.pack["day_scenario_v1"] = scenario
        except Exception as exc:
            session.add_defect("day_scenario_build_failed", str(exc), cls="VALIDATION")
        session.pack["generation_metadata"]["prompt_version"] = DAY_STORY_PROMPT_VER
        session.pack["generation_metadata"]["llm_configured"] = is_llm_chat_configured()
        path = session.write_pack(stem=case_id)
        return path


def _run_db_day(
    *,
    user_id: int,
    target: date,
    out_dir: Path,
    redact: bool,
    force_rebuild: bool,
) -> Path | None:
    from todayflow_backend.db.session import SessionLocal
    from todayflow_backend.db import models as db_models
    from todayflow_backend.services.day_story_wire_v1 import _build_day_story_record
    from todayflow_backend.services.day_story_v1 import day_story_to_today_contract_v1
    from todayflow_backend.api.morning_ritual import MorningRitualResponse

    case_id = f"user{user_id}-{target.isoformat()}"
    db = SessionLocal()
    try:
        user = db.query(db_models.User).filter(db_models.User.id == user_id).first()
        if user is None:
            raise SystemExit(f"user_id={user_id} not found")
        # Minimal morning shell — symbols/celestial may be empty; wire still builds interpretation.
        morning = MorningRitualResponse(
            date=target.isoformat(),
            tarot_card={"id": "capture", "name": "Capture"},
            tarot_explanation={"summary": "capture"},
            numerology_number={"value": 1},
            numerology_explanation={"summary": "capture"},
            daily_horoscope={"spine": {"best_mode": "Одна линия.", "first_move": "Шаг.", "main_risk": "Распыление."}},
            daily_recommendations={"what_to_do": "Один шаг.", "what_to_avoid": "Импульс."},
        )
        # Prefer loading celestial from morning builder if available on connection — else empty.
        from todayflow_backend.services.day_story_wire_v1 import (
            _daily_symbols_from_morning,
            _ritual_from_morning_and_connection,
        )
        from todayflow_backend.services.core_profile import CoreProfileService

        core = CoreProfileService().build_cached_or_baseline(db, user) or {}
        fusion_dump: dict[str, Any] = {"scores": {}}
        dc_row = (
            db.query(db_models.DayConnection)
            .filter(db_models.DayConnection.user_id == user_id, db_models.DayConnection.date == target)
            .first()
        )
        ritual_norm = _ritual_from_morning_and_connection(morning, dc_row)
        color, stone, color_sym, stone_sym, ce = _daily_symbols_from_morning(morning)

        with day_story_capture_session(
            case_id=case_id,
            label=f"db_user_{user_id}",
            redact=redact,
            out_dir=out_dir,
            target_date=target.isoformat(),
            user_id=user_id,
        ) as session:
            story, gen_id, used_fallback = _build_day_story_record(
                db,
                user=user,
                target_date=target,
                locale="ru",
                fusion_dump=fusion_dump,
                core_profile=core,
                ritual_norm=ritual_norm,
                color=color,
                stone=stone,
                celestial_events=ce or None,
                color_symbol=color_sym or None,
                stone_symbol=stone_sym or None,
                force_rebuild=force_rebuild,
                commit_story_state=False,
            )
            try:
                contract = day_story_to_today_contract_v1(story, generation_id=str(gen_id))
                # record_final already called inside wire when capture on; refresh contract slice if needed
                if session.pack.get("final") is None:
                    session.record_final(story=story, contract=contract, used_fallback=used_fallback)
                else:
                    final = session.pack["final"]
                    if isinstance(final, dict):
                        final["today_contract_slice"] = {
                            "primary_action": contract.get("primary_action"),
                            "domains": contract.get("domains"),
                            "generation_id": gen_id,
                        }
            except Exception as exc:
                session.add_defect("contract_projection_failed", str(exc), cls="PROJECTION")
            path = session.write_pack(stem=case_id)
            return path
    finally:
        db.close()


def _write_defect_rollup(out_dir: Path, paths: list[Path]) -> Path:
    counts: dict[str, int] = {}
    codes: dict[str, int] = {}
    for p in paths:
        data = json.loads(p.read_text(encoding="utf-8"))
        for d in data.get("defects") or []:
            cls = str(d.get("class") or "VALIDATION")
            code = str(d.get("code") or "")
            counts[cls] = counts.get(cls, 0) + 1
            codes[code] = codes.get(code, 0) + 1
    rollup = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pack_count": len(paths),
        "defect_class_counts": dict(sorted(counts.items(), key=lambda x: (-x[1], x[0]))),
        "defect_code_counts": dict(sorted(codes.items(), key=lambda x: (-x[1], x[0]))),
        "packs": [str(p.name) for p in paths],
        "editorial_note": "Fill editorial_review in each pack; this rollup is auto defects only.",
    }
    path = out_dir / "DEFECT_MAP_ROLLUP.json"
    path.write_text(json.dumps(rollup, ensure_ascii=False, indent=2), encoding="utf-8")
    md = out_dir / "DEFECT_MAP_ROLLUP.md"
    lines = [
        "# Day product capture — defect map rollup",
        "",
        f"Packs: {len(paths)}",
        "",
        "## By class",
    ]
    for k, v in rollup["defect_class_counts"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    lines.append("## By code")
    for k, v in rollup["defect_code_counts"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    md.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Day product logic capture v0")
    parser.add_argument("--offline", action="store_true", help="Synthetic path without DB")
    parser.add_argument("--user-id", type=int, default=None)
    parser.add_argument("--dates", type=str, default="", help="Comma-separated ISO dates")
    parser.add_argument("--out-dir", type=str, default=str(DEFAULT_OUT))
    parser.add_argument("--redact", action="store_true")
    parser.add_argument(
        "--force-rebuild",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="DB mode: pass force_rebuild to wire (default true)",
    )
    parser.add_argument("--no-llm", action="store_true", help="Offline: skip LLM even if configured")
    args = parser.parse_args()

    dates = _parse_dates(args.dates)
    out_dir = Path(args.out_dir)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = out_dir / f"capture_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    paths: list[Path] = []
    use_offline = args.offline or args.user_id is None
    if use_offline:
        force_llm = not args.no_llm
        for d in dates:
            p = _run_offline_day(d, out_dir=run_dir, redact=args.redact, force_llm=force_llm)
            if p:
                paths.append(p)
                print(f"wrote {p}")
    else:
        for d in dates:
            p = _run_db_day(
                user_id=int(args.user_id),
                target=d,
                out_dir=run_dir,
                redact=args.redact,
                force_rebuild=bool(args.force_rebuild),
            )
            if p:
                paths.append(p)
                print(f"wrote {p}")

    if not paths:
        raise SystemExit("No packs written. Use --offline and/or --user-id with --dates.")
    rollup = _write_defect_rollup(run_dir, paths)
    print(f"rollup {rollup}")
    print(f"llm_configured={is_llm_chat_configured()}")


if __name__ == "__main__":
    main()
