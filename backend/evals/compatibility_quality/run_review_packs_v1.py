#!/usr/bin/env python3
"""Build human review packs for Compatibility content v1 (C2).

Each pack: inputs · full prompts · raw model · final product · tech meta.
No secrets / user technical IDs.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from todayflow_backend.core.config import settings  # noqa: E402
from todayflow_backend.core.llm_openai_compatible import (  # noqa: E402
    chat_completion_text,
    get_openai_compatible_client,
    resolve_default_chat_model,
    resolve_max_tokens,
)
from todayflow_backend.services.compatibility_content_v1.generate_v1 import (  # noqa: E402
    _extract_json,
    build_generation_input,
)
from todayflow_backend.services.compatibility_content_v1.prompts_v1 import (  # noqa: E402
    PROMPT_VERSION,
    build_user_prompt_v1,
    system_prompt_guest_v1,
    system_prompt_premium_v1,
    system_prompt_registered_v1,
)
from todayflow_backend.services.compatibility_content_v1.publish_gate import (  # noqa: E402
    evaluate_publish,
)
from todayflow_backend.services.compatibility_content_v1.quality_checks import (  # noqa: E402
    run_quality_suite,
)
from todayflow_backend.services.compatibility_content_v1.source_depth import (  # noqa: E402
    depth_honesty_line,
)
from todayflow_backend.services.compatibility_content_v1.surface_adapter import (  # noqa: E402
    guest_to_product_surface,
    registered_to_product_surface,
)

# First human-review batch (10 cases) — curated from scenarios_v1.json
FIRST_BATCH: list[dict[str, str]] = [
    {"id": "cq-001", "tier": "registered", "label": "Registered / same signs (Aries×Aries)"},
    {"id": "cq-005", "tier": "registered", "label": "Registered / hard pair (Aries×Cancer)"},
    {"id": "cq-010", "tier": "registered", "label": "Registered / zodiac diverse"},
    {"id": "cq-021", "tier": "registered", "label": "Registered / birth dates + question (stored, not answered as premium)"},
    {"id": "cq-025", "tier": "registered", "label": "Registered / birth dates"},
    {"id": "cq-042", "tier": "registered", "label": "Registered / one profile"},
    {"id": "cq-061", "tier": "registered", "label": "Registered / two profiles"},
    {"id": "cq-041", "tier": "premium", "label": "Premium / question + missing goals"},
    {"id": "cq-063", "tier": "premium", "label": "Premium / two profiles + continue?"},
    {"id": "cq-064", "tier": "registered", "label": "Complex incomplete / missing partner closeness"},
]

CALC_LABEL = {
    "zodiac_only": "знаки",
    "birth_dates": "даты",
    "profile_enriched": "один профиль",
    "two_profiles": "два профиля",
}


def _system_for(tier: str, depth: str, locale: str) -> str:
    if tier == "guest":
        return system_prompt_guest_v1(source_depth=depth, locale=locale)
    if tier == "registered":
        return system_prompt_registered_v1(source_depth=depth, locale=locale)
    return system_prompt_premium_v1(source_depth=depth, locale=locale)


def _expected_schema(tier: str) -> dict[str, Any]:
    base = {
        "contract_version": "compatibility_content_v1",
        "tier": tier,
        "source_depth": "zodiac_only|birth_dates|profile_enriched|two_profiles",
        "locale": "ru",
        "confidence": "low|medium|high",
    }
    if tier == "guest":
        base.update(
            {
                "headline": "string",
                "score": "20-95",
                "summary": "string",
                "attraction": "string",
                "main_risk": "string",
                "practical_advice": "string",
                "locked_preview": ["string", "..."],
            }
        )
    elif tier == "registered":
        base.update(
            {
                "headline": "string",
                "score": "20-95",
                "summary": "string",
                "attraction": "string",
                "emotions": "string",
                "communication": "string",
                "conflict": "string",
                "strengths": "string",
                "vulnerable_spot": "string",
                "what_helps": "string",
                "main_risk": "string",
                "practical_advice": "string",
            }
        )
    else:
        base.update(
            {
                "verdict": "да|скорее да|зависит|скорее нет|нет",
                "verdict_reason": "string",
                "do": "string",
                "avoid": "string",
                "how": "string",
                "what_to_say": "string",
                "focus_now": "string",
                "next_step": "string",
                "direct_answer": "string|null",
            }
        )
    return base


def _locked_for_tier(tier: str) -> list[str]:
    if tier == "guest":
        return ["emotions", "communication", "conflict", "vulnerable_spot", "what_helps", "premium_pack"]
    if tier == "registered":
        return ["verdict", "do", "avoid", "how", "what_to_say", "direct_answer"]
    return []


def _user_facing(tier: str, content: dict[str, Any] | None, honesty: str) -> dict[str, Any]:
    if not content:
        return {"error": "no_parsed_content", "honesty_line": honesty}
    if tier == "premium":
        return {
            "honesty_line": honesty,
            "verdict": content.get("verdict"),
            "verdict_reason": content.get("verdict_reason"),
            "do": content.get("do"),
            "avoid": content.get("avoid"),
            "how": content.get("how"),
            "what_to_say": content.get("what_to_say"),
            "focus_now": content.get("focus_now"),
            "next_step": content.get("next_step"),
            "direct_answer": content.get("direct_answer"),
        }
    if tier == "guest":
        surface = guest_to_product_surface(
            __import__(
                "todayflow_backend.services.compatibility_content_v1.contracts",
                fromlist=["GuestContentV1"],
            ).GuestContentV1.model_validate(content)
        )
        return {
            "honesty_line": honesty,
            "headline": content.get("headline"),
            "score": content.get("score"),
            "summary": content.get("summary"),
            "attraction": content.get("attraction"),
            "main_risk": content.get("main_risk"),
            "practical_advice": content.get("practical_advice"),
            "locked_preview": content.get("locked_preview"),
            "product_surface_score_tagline": surface.score_tagline,
            "overview_paragraphs": surface.overview_paragraphs,
        }
    # registered
    try:
        from todayflow_backend.services.compatibility_content_v1.contracts import RegisteredContentV1

        surface = registered_to_product_surface(RegisteredContentV1.model_validate(content))
        overview = surface.overview_paragraphs
        blocks = [
            {"key": b.key, "title": b.title, "takeaway": b.takeaway, "detail": b.detail}
            for b in surface.blocks
        ]
    except Exception as exc:  # noqa: BLE001
        overview = [content.get("summary")]
        blocks = []
        surface_err = str(exc)
    else:
        surface_err = None
    return {
        "honesty_line": honesty,
        "headline": content.get("headline"),
        "score": content.get("score"),
        "summary": content.get("summary"),
        "blocks": {
            "attraction": content.get("attraction"),
            "emotions": content.get("emotions"),
            "communication": content.get("communication"),
            "conflict": content.get("conflict"),
            "strengths": content.get("strengths"),
            "vulnerable_spot": content.get("vulnerable_spot"),
            "what_helps": content.get("what_helps"),
            "main_risk": content.get("main_risk"),
            "practical_advice": content.get("practical_advice"),
        },
        "product_surface": {"overview": overview, "blocks": blocks, "adapter_error": surface_err},
    }


def build_inputs_section(sc: dict[str, Any], tier: str) -> dict[str, Any]:
    depth = sc.get("source_depth") or "zodiac_only"
    missing = list(sc.get("missing_fields") or [])
    hidden = []
    if not sc.get("birth_date_1"):
        hidden.append("birth_date_1")
    if not sc.get("birth_date_2"):
        hidden.append("birth_date_2")
    if not sc.get("profile_a"):
        hidden.append("profile_a")
    if not sc.get("profile_b"):
        hidden.append("profile_b")
    return {
        "access_tier": tier,
        "calculation_mode": CALC_LABEL.get(depth, depth),
        "source_depth": depth,
        "locale": sc.get("locale") or "ru",
        "relationship_context": sc.get("relationship_context"),
        "person_1": {
            "sign": sc.get("from_sign"),
            "birth_date": sc.get("birth_date_1"),
            "profile": sc.get("profile_a"),
        },
        "person_2": {
            "sign": sc.get("to_sign"),
            "birth_date": sc.get("birth_date_2"),
            "profile": sc.get("profile_b"),
        },
        "user_question": sc.get("user_question"),
        "missing_or_hidden_fields": sorted(set(missing + hidden)),
        "scenario_tags": sc.get("tags") or [],
        "honesty_line_expected": depth_honesty_line(depth, locale=sc.get("locale") or "ru"),  # type: ignore[arg-type]
    }


def run_one(sc: dict[str, Any], tier: str, label: str, case_no: int) -> dict[str, Any]:
    locale = sc.get("locale") or "ru"
    payload = build_generation_input(
        from_sign=sc["from_sign"],
        to_sign=sc["to_sign"],
        locale=locale,
        relationship_context=sc.get("relationship_context"),
        birth_date_1=sc.get("birth_date_1"),
        birth_date_2=sc.get("birth_date_2"),
        profile_a=sc.get("profile_a"),
        profile_b=sc.get("profile_b"),
        user_question=sc.get("user_question"),
    )
    depth = str(payload["source_depth"])
    system = _system_for(tier, depth, locale)
    user = build_user_prompt_v1(payload)
    model = resolve_default_chat_model()
    temperature = 0.55
    max_tokens = resolve_max_tokens(2200 if tier != "guest" else 900)
    client = get_openai_compatible_client(operation="background")
    tech: dict[str, Any] = {
        "prompt_id": PROMPT_VERSION,
        "prompt_version": PROMPT_VERSION,
        "contract_version": "compatibility_content_v1",
        "model": model,
        "provider": settings.llm_provider,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "json_object": True,
        "latency_ms": None,
        "retry": False,
        "fallback": False,
        "validation_errors": [],
        "quality_ok": None,
    }
    raw = None
    parsed = None
    t0 = time.perf_counter()
    if client is None:
        tech["fallback"] = True
        tech["error"] = "llm_client_unavailable"
    else:
        try:
            raw = chat_completion_text(
                client,
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                json_object=True,
            )
        except Exception as exc:  # noqa: BLE001
            tech["error"] = str(exc)[:500]
            tech["fallback"] = True
    tech["latency_ms"] = int((time.perf_counter() - t0) * 1000)
    if raw:
        parsed = _extract_json(raw)
    if parsed:
        parsed.setdefault("contract_version", "compatibility_content_v1")
        parsed.setdefault("tier", tier)
        parsed.setdefault("source_depth", depth)
        parsed.setdefault("locale", locale)
        known: set[str] = set()
        if payload.get("profile_a"):
            known.add("profile_a")
        if payload.get("profile_b"):
            known.add("profile_b")
        quality = run_quality_suite(tier=tier, content=parsed, known_facts=known)
        tech["validation_errors"] = quality.get("errors") or []
        tech["quality_ok"] = quality.get("ok")
        tech["fingerprint"] = quality.get("fingerprint")
    else:
        tech["validation_errors"] = ["parse:invalid_json"]
        tech["quality_ok"] = False
        if raw is None:
            tech["fallback"] = True

    honesty = depth_honesty_line(depth, locale=locale)  # type: ignore[arg-type]
    known_facts: set[str] = set()
    if payload.get("profile_a"):
        known_facts.add("profile_a")
    if payload.get("profile_b"):
        known_facts.add("profile_b")

    if parsed and tier == "premium" and "score" in parsed:
        # Premium UI does not show score (v1.1).
        parsed = {k: v for k, v in parsed.items() if k != "score"}
        quality = run_quality_suite(tier=tier, content=parsed, known_facts=known_facts)
        tech["validation_errors"] = quality.get("errors") or []
        tech["quality_ok"] = quality.get("ok")
        tech["fingerprint"] = quality.get("fingerprint")
        tech["postprocess"] = ["stripped_premium_score"]

    gate = evaluate_publish(tier=tier, content=parsed, known_facts=known_facts)
    tech["publish_allowed"] = gate["publish_allowed"]
    tech["publish_decision"] = gate["decision"]

    postprocess_notes: list[str] = []
    if parsed and tech["validation_errors"]:
        postprocess_notes.append("validators_flagged")
    if not gate["publish_allowed"]:
        postprocess_notes.append(
            "production_gate:invalid_not_shown — keep baseline / enrichment_failed or retry"
        )
    if not parsed:
        postprocess_notes.append("no_parse_ui_would_fallback_to_baseline")

    # Review packs still include parsed text for human scoring, but mark production gate.
    user_facing = (
        _user_facing(tier, parsed, honesty)
        if parsed
        else {"error": "no_parsed_content", "honesty_line": honesty}
    )
    if not gate["publish_allowed"]:
        user_facing = {
            "production_publish_allowed": False,
            "production_decision": gate["decision"],
            "production_user_facing": None,
            "review_only_parsed_preview": user_facing,
            "errors": gate.get("errors"),
        }

    pack = {
        "case_no": case_no,
        "case_title": f"Case {case_no:02d} — {label}",
        "scenario_id": sc["id"],
        "label": label,
        "inputs": build_inputs_section(sc, tier),
        "prompt": {
            "system_prompt": system,
            "developer_prompt": None,
            "user_prompt": user,
            "substituted_context": payload,
            "prompt_id": PROMPT_VERSION,
            "prompt_version": PROMPT_VERSION,
            "model": model,
            "generation_params": {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "response_format": "json_object",
            },
            "expected_json_schema": _expected_schema(tier),
        },
        "raw_model_response": raw,
        "final_product": {
            "parsed_contract": parsed,
            "validation": {
                "ok": tech["quality_ok"],
                "errors": tech["validation_errors"],
            },
            "publish_allowed": gate["publish_allowed"],
            "publish_decision": gate["decision"],
            "user_facing": user_facing,
            "locked_by_tier": _locked_for_tier(tier),
            "postprocess_changes": postprocess_notes,
            "retry": tech["retry"],
            "fallback": tech["fallback"] or (not gate["publish_allowed"]),
        },
        "tech": tech,
        "human_review_template": {
            "liked": "",
            "sounds_bad": "",
            "repeats": "",
            "feels_invented": "",
            "missing": "",
            "shippable": "да | после правок | нет",
            "score_1_to_10": None,
            "scores": {
                "naturalness": None,
                "personalization": None,
                "practical_value": None,
                "honesty": None,
                "todayflow_voice": None,
                "memorability": None,
                "consistency": None,
            },
            "voice_exemplar_to_canon": "",
            "voice_canon_ref": "docs/content/TODAYFLOW_VOICE_CANON.md",
        },
    }
    return pack


def pack_to_markdown(pack: dict[str, Any]) -> str:
    inp = pack["inputs"]
    fin = pack["final_product"]
    tech = pack["tech"]
    lines = [
        f"# {pack['case_title']}",
        "",
        f"**scenario_id:** `{pack['scenario_id']}`",
        "",
        "## 1. Входные данные",
        "",
        "```json",
        json.dumps(inp, ensure_ascii=False, indent=2),
        "```",
        "",
        "## 2. Фактический запрос модели",
        "",
        f"- prompt_id / version: `{pack['prompt']['prompt_id']}`",
        f"- model: `{pack['prompt']['model']}`",
        f"- params: `{json.dumps(pack['prompt']['generation_params'], ensure_ascii=False)}`",
        "",
        "### System prompt",
        "",
        "```",
        pack["prompt"]["system_prompt"],
        "```",
        "",
        "### User prompt",
        "",
        "```json",
        pack["prompt"]["user_prompt"],
        "```",
        "",
        "### Expected JSON schema",
        "",
        "```json",
        json.dumps(pack["prompt"]["expected_json_schema"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## 3. Сырой ответ модели",
        "",
        "```",
        pack.get("raw_model_response") or "(empty)",
        "```",
        "",
        "## 4. Итоговый ответ продукта",
        "",
        "```json",
        json.dumps(fin, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Техническая информация",
        "",
        "```json",
        json.dumps(tech, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Ваша оценка",
        "",
        "* Что понравилось:",
        "* Что звучит плохо:",
        "* Что повторяется:",
        "* Что выглядит выдуманным:",
        "* Чего не хватает:",
        "* Можно ли показывать пользователю: да / после правок / нет",
        "* Оценка: 1–10",
        "",
        "### Voice (TodayFlow)",
        "",
        "* Naturalness: /10",
        "* Personalization: /10",
        "* Practical value: /10",
        "* Honesty: /10",
        "* TodayFlow Voice: /10",
        "* Memorability: /10",
        "* Consistency: /10 (без логотипа — один продукт с другими кейсами/модулями?)",
        "* Удачная фраза/структура → перенести принцип в `docs/content/TODAYFLOW_VOICE_CANON.md`:",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", choices=["first10", "all_ids"], default="first10")
    ap.add_argument("--ids", nargs="*", default=[])
    args = ap.parse_args()

    scenarios_path = Path(__file__).parent / "scenarios_v1.json"
    doc = json.loads(scenarios_path.read_text(encoding="utf-8"))
    by_id = {s["id"]: s for s in doc["scenarios"]}

    if args.batch == "first10":
        plan = FIRST_BATCH
    else:
        plan = [{"id": i, "tier": "registered", "label": i} for i in args.ids]

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(__file__).parent / "runs" / f"review_packs_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    index: list[dict[str, Any]] = []
    for i, item in enumerate(plan, start=1):
        sc = by_id.get(item["id"])
        if not sc:
            print("MISSING", item["id"])
            continue
        print(f"[{i}/{len(plan)}] {item['id']} {item['tier']} …", flush=True)
        pack = run_one(sc, item["tier"], item["label"], i)
        json_path = out_dir / f"case_{i:02d}_{sc['id']}_{item['tier']}.json"
        md_path = out_dir / f"case_{i:02d}_{sc['id']}_{item['tier']}.md"
        json_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
        md_path.write_text(pack_to_markdown(pack), encoding="utf-8")
        index.append(
            {
                "case_no": i,
                "scenario_id": sc["id"],
                "tier": item["tier"],
                "label": item["label"],
                "quality_ok": pack["tech"].get("quality_ok"),
                "latency_ms": pack["tech"].get("latency_ms"),
                "errors": pack["tech"].get("validation_errors"),
                "json": str(json_path.name),
                "md": str(md_path.name),
                "headline": (pack["final_product"].get("parsed_contract") or {}).get("headline")
                or (pack["final_product"].get("parsed_contract") or {}).get("verdict"),
            }
        )
        print(
            f"  ok={pack['tech'].get('quality_ok')} latency={pack['tech'].get('latency_ms')}ms "
            f"errs={pack['tech'].get('validation_errors')}",
            flush=True,
        )

    (out_dir / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print("DONE", out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
