#!/usr/bin/env python3
"""Сравнение качества compatibility-текстов на разных OpenAI-моделях.

Один и тот же промпт (как в POST /compatibility/dynamics) — side-by-side выдержки.

Usage:
  cd backend && python scripts/compare_compatibility_models.py

  python scripts/compare_compatibility_models.py --models gpt-4o-mini gpt-5.5
  python scripts/compare_compatibility_models.py --locale en --format sex
  python scripts/compare_compatibility_models.py --from-sign aries --to-sign libra --save /tmp/compat
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT / "src"))

from todayflow_backend.api.compatibility import (  # noqa: E402
    _build_static_sign_report,
    _localized_element_relation,
    _localized_rhythm_relation,
)
from todayflow_backend.core.llm_openai_compatible import (  # noqa: E402
    chat_completion_text,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_max_tokens,
)
from todayflow_backend.data.astrology import lookup_sign_metadata  # noqa: E402
from todayflow_backend.i18n import localized_sign_name  # noqa: E402
from todayflow_backend.services.compatibility_llm import (  # noqa: E402
    _parse_llm_json,
    build_pair_dynamics,
    build_signals,
    context_label,
    system_prompt_for_locale,
)
from todayflow_backend.services.compatibility_scenario_tone import (  # noqa: E402
    SCENARIO_TONE_REGISTRY,
    augment_system_prompt_with_scenario,
    scenario_context_for_llm,
)
from todayflow_backend.services.sign_compatibility_product import build_sign_product_surface  # noqa: E402


def _block_excerpt(blocks: list[dict], key: str) -> str:
    row = next((b for b in blocks if b.get("key") == key), None)
    if not row:
        return "(block missing)"
    lines = [
        f"  title: {row.get('title', '')}",
        f"  takeaway: {row.get('takeaway', '')}",
        f"  detail: {row.get('detail', '')}",
        f"  risk: {row.get('risk', '')}",
        f"  action: {row.get('action', '')}",
    ]
    return "\n".join(lines)


def _format_parsed(parsed: dict) -> str:
    overview = parsed.get("overview_paragraphs") or []
    blocks = parsed.get("blocks") if isinstance(parsed.get("blocks"), list) else []
    roles = parsed.get("roles") if isinstance(parsed.get("roles"), dict) else {}
    lines = [
        f"score_tagline: {parsed.get('score_tagline', '')}",
        "",
        "overview:",
    ]
    for i, para in enumerate(overview[:3], 1):
        lines.append(f"  [{i}] {para}")
    lines.extend(["", "block — sexuality:", _block_excerpt(blocks, "sexuality"), "", "roles — you:"])
    for bullet in (roles.get("you_bullets") or [])[:3]:
        lines.append(f"  • {bullet}")
    lines.append("roles — partner:")
    for bullet in (roles.get("partner_bullets") or [])[:3]:
        lines.append(f"  • {bullet}")
    return "\n".join(lines)


def _format_template_surface(surface) -> str:
    blocks = [{"key": b.key, "title": b.title, "takeaway": b.takeaway, "detail": b.detail, "risk": b.risk, "action": b.action} for b in surface.blocks]
    parsed = {
        "score_tagline": surface.score_tagline,
        "overview_paragraphs": list(surface.overview_paragraphs),
        "blocks": blocks,
        "roles": {
            "you_bullets": list(surface.roles.you_bullets),
            "partner_bullets": list(surface.roles.partner_bullets),
        },
    }
    return _format_parsed(parsed)


def _build_fixture(
    *,
    from_sign: str,
    to_sign: str,
    relationship_context: str,
    format_id: str,
    locale: str,
) -> tuple[str, str, dict]:
    from_meta = lookup_sign_metadata(from_sign)
    to_meta = lookup_sign_metadata(to_sign)
    if not from_meta or not to_meta:
        raise SystemExit(f"Unknown signs: {from_sign!r} / {to_sign!r}")

    from_display = localized_sign_name(from_meta["id"], locale=locale)
    to_display = localized_sign_name(to_meta["id"], locale=locale)
    el_rel = _localized_element_relation(from_meta.get("element", ""), to_meta.get("element", ""), locale=locale)
    rh_rel = _localized_rhythm_relation(from_meta.get("modality", ""), to_meta.get("modality", ""), locale=locale)

    static_payload = _build_static_sign_report(
        from_sign=from_meta["id"],
        to_sign=to_meta["id"],
        from_name=from_display,
        to_name=to_display,
        from_element=from_meta.get("element", ""),
        to_element=to_meta.get("element", ""),
        from_modality=from_meta.get("modality", ""),
        to_modality=to_meta.get("modality", ""),
        locale=locale,
    )
    qr = static_payload["quick_reading"]
    template_surface = build_sign_product_surface(
        from_sign=from_meta["id"],
        to_sign=to_meta["id"],
        from_name=from_display,
        to_name=to_display,
        from_element=from_meta.get("element", ""),
        to_element=to_meta.get("element", ""),
        from_modality=from_meta.get("modality", ""),
        to_modality=to_meta.get("modality", ""),
        score=static_payload["score"],
        relationship_context=relationship_context,
        element_relation=el_rel,
        rhythm_relation=rh_rel,
        strongest=str(qr.get("strongest") or ""),
        friction=str(qr.get("friction") or ""),
        locale=locale,
    )
    pair_dynamics = build_pair_dynamics(
        user1_label="You" if locale == "en" else "Ты",
        user2_label="Partner" if locale == "en" else "Партнёр",
        from_modality=from_meta.get("modality", ""),
        to_modality=to_meta.get("modality", ""),
        from_element=from_meta.get("element", ""),
        to_element=to_meta.get("element", ""),
        locale=locale,
    )
    signals = build_signals(subscores=template_surface.subscores.model_dump(), score=static_payload["score"])
    scenario_tone = SCENARIO_TONE_REGISTRY.get(format_id)
    if scenario_tone is None:
        raise SystemExit(f"Unknown format_id: {format_id!r}. Examples: sex, living_together, love")

    loc = locale.strip().split("-")[0].lower()
    sys_prompt = augment_system_prompt_with_scenario(system_prompt_for_locale(loc), scenario_tone, locale=loc)
    payload = {
        "pair_display": f"{from_display} × {to_display}",
        "user_1": "You" if loc == "en" else "Ты",
        "user_2": "Partner" if loc == "en" else "Партнёр",
        "relationship_stage": relationship_context,
        "context_label": context_label(relationship_context, locale=loc),
        "pair_dynamics": pair_dynamics,
        "signals": signals,
        "element_relation_hint": el_rel,
        "rhythm_relation_hint": rh_rel,
        "feedback_on_blocks": [],
        "content_locale": loc,
        "scenario": scenario_context_for_llm(scenario_tone, locale=loc),
    }
    user_prompt = json.dumps(payload, ensure_ascii=False)
    return sys_prompt, user_prompt, template_surface


def _call_model(
    client,
    *,
    model: str,
    sys_prompt: str,
    user_prompt: str,
    max_tokens: int,
) -> tuple[dict | None, int, str | None]:
    started = perf_counter()
    raw = chat_completion_text(
        client,
        model=model,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.55,
        max_tokens=resolve_max_tokens(max_tokens),
        json_object=True,
    )
    elapsed_ms = int((perf_counter() - started) * 1000)
    if not raw:
        return None, elapsed_ms, "empty response"
    parsed = _parse_llm_json(raw)
    if not parsed:
        return None, elapsed_ms, f"invalid JSON: {raw[:400]}"
    return parsed, elapsed_ms, None


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare compatibility LLM models on the same prompt")
    parser.add_argument("--models", nargs="+", default=["gpt-4o-mini", "gpt-5.5"], help="OpenAI model ids")
    parser.add_argument("--from-sign", default="aries")
    parser.add_argument("--to-sign", default="libra")
    parser.add_argument("--relationship-context", default="mutual_attraction")
    parser.add_argument("--format", dest="format_id", default="sex", help="Scenario format_id")
    parser.add_argument("--locale", default="ru", choices=("ru", "en"))
    parser.add_argument("--save", type=Path, default=None, help="Directory to write full JSON per model")
    args = parser.parse_args()

    if not is_llm_chat_configured():
        print("OPENAI_API_KEY не задан (LLM_PROVIDER=openai).", file=sys.stderr)
        return 1

    client = get_openai_compatible_client()
    if client is None:
        print("Не удалось создать OpenAI-клиент.", file=sys.stderr)
        return 1

    sys_prompt, user_prompt, template_surface = _build_fixture(
        from_sign=args.from_sign,
        to_sign=args.to_sign,
        relationship_context=args.relationship_context,
        format_id=args.format_id,
        locale=args.locale,
    )

    print("=" * 72)
    print(
        f"Compatibility model compare — {args.from_sign} × {args.to_sign}, "
        f"format={args.format_id}, locale={args.locale}"
    )
    print("=" * 72)

    print("\n### TEMPLATE (без LLM, prod fallback)\n")
    print(_format_template_surface(template_surface))

    failures = 0
    for model in args.models:
        print("\n" + "=" * 72)
        print(f"### {model}\n")
        parsed, elapsed_ms, err = _call_model(
            client,
            model=model,
            sys_prompt=sys_prompt,
            user_prompt=user_prompt,
            max_tokens=2800,
        )
        if err or not parsed:
            print(f"FAILED ({elapsed_ms} ms): {err}")
            failures += 1
            continue
        print(_format_parsed(parsed))
        print(f"\n({elapsed_ms} ms)")
        if args.save:
            args.save.mkdir(parents=True, exist_ok=True)
            out_path = args.save / f"{model.replace('/', '_')}.json"
            out_path.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Full JSON → {out_path}")

    print("\n" + "=" * 72)
    print("Сравни: конкретность поведения, сценарий sex/формат, отсутствие banned-слов, длина overview.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
