#!/usr/bin/env python3
"""C3 — Profile review packs: allowed input → prompts → raw → final.

Uses the *current* production funnel (profile_disclosure_funnel_v0) so the
first human scorecard baselines today's quality, not a future prompt.
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
    chat_completion_plain,
    get_openai_compatible_client,
    is_llm_chat_configured,
    resolve_default_chat_model,
)
from todayflow_backend.prompts.registry_v1 import get_prompt  # noqa: E402
from todayflow_backend.services.llm_quality_policy_v1 import (  # noqa: E402
    funnel_step_max_tokens,
    user_json_char_budget,
)
from todayflow_backend.services.profile_content_v1.architecture import (  # noqa: E402
    LLM_ON_READ_RISK_CALLERS,
    SAFE_SNAPSHOT_CALLERS,
    classify_allowed_claims,
)
from todayflow_backend.services.profile_content_v1.banned_phrases import (  # noqa: E402
    find_banned_hits,
    find_depth_overclaims,
)
from todayflow_backend.services.profile_content_v1.source_depth import (  # noqa: E402
    depth_from_scenario,
    depth_honesty_line,
)
from todayflow_backend.services.profile_disclosure_funnel_v0 import (  # noqa: E402
    SPHERE_FIELDS,
    SPHERE_IDS,
    _identity_ok,
    _patterns_ok,
    _spheres_ok,
    _styles_ok,
    build_shared_profile_input,
)

FIRST_BATCH = [
    "pq-001",
    "pq-002",
    "pq-003",
    "pq-004",
    "pq-005",
    "pq-006",
    "pq-007",
    "pq-008",
    "pq-009",
    "pq-010",
]

STEPS = (
    ("identity", "profile.identity.v1", "normal", _identity_ok),
    ("styles", "profile.styles.v1", "normal", _styles_ok),
    ("patterns", "profile.patterns.v1", "deep", _patterns_ok),
    ("spheres", "profile.spheres.v1", "deep", _spheres_ok),
)


def _scenario_to_user_json(sc: dict[str, Any]) -> dict[str, Any]:
    living = sc.get("living")
    # Attach onboarding into living so current funnel can see self-descriptions
    # (production gap: onboarding often not in portrait pack — we surface it explicitly).
    if sc.get("onboarding"):
        living = dict(living or {})
        living["onboarding"] = sc["onboarding"]
        living.setdefault("summary", living.get("summary") or "Есть ответы онбординга.")
    return {
        "person": sc.get("person") or {},
        "astro": sc.get("astro") or {},
        "numerology": sc.get("numerology") or {},
        "baseline": sc.get("baseline") or {},
        "living": living,
        "locale": sc.get("locale") or "ru",
        "profile_hash": f"eval-{sc['id']}",
        "birth_date": sc.get("birth_date"),
    }


def _call_raw(system: str, user: str, *, max_tokens: int, temperature: float = 0.48) -> tuple[str | None, int]:
    t0 = time.perf_counter()
    client = get_openai_compatible_client(operation="background")
    if client is None:
        return None, 0
    raw = chat_completion_plain(
        client,
        model=resolve_default_chat_model(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return raw, int((time.perf_counter() - t0) * 1000)


def _parse(raw: str | None) -> dict[str, Any] | None:
    if not raw:
        return None
    text = raw.strip()
    if text.startswith("```"):
        import re

        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None


def run_funnel_captured(user_json: dict[str, Any], *, locale: str) -> dict[str, Any]:
    shared = build_shared_profile_input(user_json)
    steps_out: list[dict[str, Any]] = []
    identity = styles = patterns = spheres = None
    total_ms = 0
    retry_count = 0

    for step_name, prompt_id, depth_level, ok_fn in STEPS:
        system, ver = get_prompt(prompt_id, locale=locale)
        payload: dict[str, Any] = {"shared": shared, "step": step_name}
        if identity:
            payload["identity"] = identity
        if styles:
            payload["styles"] = styles
        if patterns:
            payload["patterns"] = patterns
        user = json.dumps(payload, ensure_ascii=False)[: user_json_char_budget()]
        max_tokens = funnel_step_max_tokens(depth_level)
        step: dict[str, Any] = {
            "step": step_name,
            "prompt_id": prompt_id,
            "prompt_version": ver,
            "system_prompt": system,
            "user_prompt": user,
            "model": resolve_default_chat_model(),
            "temperature": 0.48,
            "max_tokens": max_tokens,
            "attempts": 0,
            "raw_responses": [],
            "parsed": None,
            "ok": False,
            "latency_ms": 0,
        }
        parsed = None
        step_ms = 0
        # Audit packs: 1 attempt only (retries × Nebius timeouts blew past 45+ min).
        step["attempts"] = 1
        raw, ms = _call_raw(system, user, max_tokens=max_tokens)
        step_ms += ms
        step["raw_responses"].append(raw)
        parsed = _parse(raw)
        if ok_fn(parsed):
            step["ok"] = True
        else:
            parsed = None
        step["parsed"] = parsed
        step["latency_ms"] = step_ms
        total_ms += step_ms
        steps_out.append(step)
        if not parsed:
            break
        if step_name == "identity":
            identity = parsed
        elif step_name == "styles":
            styles = parsed
        elif step_name == "patterns":
            patterns = parsed
        elif step_name == "spheres":
            spheres = parsed
        # Stop after patterns for audit speed — spheres is the timeout sink.
        if step_name == "patterns":
            break

    merged: dict[str, Any] = {}
    if identity:
        merged.update(
            {
                "identity_core": identity.get("identity_core"),
                "strengths": identity.get("strengths"),
                "growth_zones": identity.get("growth_zones"),
            }
        )
    if styles:
        merged.update(
            {
                "relationship_style": styles.get("relationship_style"),
                "money_style": styles.get("money_style"),
                "decision_style": styles.get("decision_style"),
            }
        )
    if patterns:
        merged.update(
            {
                "recurring_patterns": patterns.get("recurring_patterns"),
                "living_changes": patterns.get("living_changes"),
                "life_mission": patterns.get("life_mission"),
                "helps": patterns.get("helps"),
            }
        )
    if spheres:
        merged["life_spheres"] = spheres.get("life_spheres")

    return {
        "steps": steps_out,
        "merged_contract": merged,
        "completed_steps": [s["step"] for s in steps_out if s["ok"]],
        "total_latency_ms": total_ms,
        "retry_count": retry_count,
        "fallback": len([s for s in steps_out if s["ok"]]) < 4,
    }


def _map_user_facing(merged: dict[str, Any], *, honesty: str, depth: str) -> dict[str, Any]:
    """Approximate Profile V2 surface from current contract fields."""
    return {
        "honesty_line": honesty,
        "source_depth": depth,
        "headline": (merged.get("identity_core") or "")[:120],
        "core_summary": merged.get("identity_core"),
        "strengths": merged.get("strengths"),
        "growth_zones": merged.get("growth_zones"),
        "emotional_style": merged.get("relationship_style"),
        "communication_style": merged.get("relationship_style"),
        "decision_style": merged.get("decision_style"),
        "energy_sources": (merged.get("helps") or [None])[0] if merged.get("helps") else None,
        "energy_drains": (merged.get("growth_zones") or [None])[0] if merged.get("growth_zones") else None,
        "under_pressure": merged.get("living_changes"),
        "inner_tension": (merged.get("recurring_patterns") or [None])[0]
        if merged.get("recurring_patterns")
        else None,
        "practical_takeaway": (merged.get("helps") or [None])[-1] if merged.get("helps") else None,
        "life_mission": merged.get("life_mission"),
        "life_spheres_keys": list((merged.get("life_spheres") or {}).keys())
        if isinstance(merged.get("life_spheres"), dict)
        else [],
        "mapping_note": "Mapped from current profile_contract_v1 fields — C3 target contract differs (see canon).",
    }


def _validate_pack(merged: dict[str, Any], depth: str) -> list[str]:
    errs: list[str] = []
    blob = json.dumps(merged, ensure_ascii=False)
    errs.extend(f"banned:{h}" for h in find_banned_hits(blob))
    errs.extend(find_depth_overclaims(blob, source_depth=depth))
    if depth == "birth_data_only" and merged.get("recurring_patterns"):
        # Soft: current funnel often invents patterns without living — flag for humans.
        errs.append("audit:recurring_patterns_without_longitudinal_data")
    if not merged.get("identity_core"):
        errs.append("missing:identity_core")
    # spheres completeness if present
    spheres = merged.get("life_spheres")
    if isinstance(spheres, dict):
        for sid in SPHERE_IDS:
            row = spheres.get(sid)
            if not isinstance(row, dict):
                errs.append(f"sphere_missing:{sid}")
                continue
            for f in SPHERE_FIELDS:
                if len(str(row.get(f) or "").strip()) < 8:
                    errs.append(f"sphere_thin:{sid}.{f}")
    return errs


def run_one(sc: dict[str, Any], case_no: int) -> dict[str, Any]:
    locale = sc.get("locale") or "ru"
    depth = depth_from_scenario(sc)
    honesty = depth_honesty_line(depth, locale=locale)
    user_json = _scenario_to_user_json(sc)
    claims = classify_allowed_claims(depth)

    tech: dict[str, Any] = {
        "model": resolve_default_chat_model() if is_llm_chat_configured() else None,
        "provider": settings.llm_provider,
        "llm_configured": is_llm_chat_configured(),
        "funnel": "profile_disclosure_funnel_v0",
        "architecture_note": {
            "llm_on_read_risk_callers": list(LLM_ON_READ_RISK_CALLERS),
            "safe_snapshot_callers": list(SAFE_SNAPSHOT_CALLERS),
        },
    }

    if not is_llm_chat_configured():
        return {
            "case_no": case_no,
            "case_title": f"Case {case_no:02d} — {sc.get('label')}",
            "scenario_id": sc["id"],
            "inputs": {
                "access_tier": sc.get("tier"),
                "source_depth": depth,
                "honesty_line": honesty,
                "allowed_claims": claims,
                "person": sc.get("person"),
                "birth_date": sc.get("birth_date"),
                "astro": sc.get("astro"),
                "numerology": sc.get("numerology"),
                "baseline": sc.get("baseline"),
                "onboarding": sc.get("onboarding"),
                "living": sc.get("living"),
                "user_question": sc.get("user_question"),
                "missing_or_hidden": sc.get("missing_or_hidden"),
                "locale": locale,
            },
            "prompt": None,
            "raw_model_response": None,
            "final_product": {"error": "llm_not_configured"},
            "tech": tech,
            "human_review_template": {
                "liked": "",
                "sounds_bad": "",
                "repeats": "",
                "feels_invented": "",
                "missing": "",
                "shippable": "да | после правок | нет",
                "score_1_to_10": None,
            },
        }

    funnel = run_funnel_captured(user_json, locale=locale)
    merged = funnel["merged_contract"]
    validation_errors = _validate_pack(merged, depth)
    tech.update(
        {
            "latency_ms": funnel["total_latency_ms"],
            "retry_count": funnel["retry_count"],
            "fallback": funnel["fallback"],
            "completed_steps": funnel["completed_steps"],
            "validation_errors": validation_errors,
            "quality_ok": not validation_errors and len(funnel["completed_steps"]) >= 3,
        }
    )

    # Premium question: append a lightweight application step (current product has no dedicated premium profile pack).
    premium_block = None
    if sc.get("tier") == "premium" and sc.get("user_question"):
        system = (
            "Ты — premium-слой профиля TodayFlow. Дай практический пакет на русском. "
            "Без диагнозов и без «он(а)». JSON: direct_answer, do, avoid, how, what_to_say, next_step."
        )
        user = json.dumps(
            {"question": sc["user_question"], "portrait": merged, "source_depth": depth},
            ensure_ascii=False,
        )[:8000]
        raw, ms = _call_raw(system, user, max_tokens=1200)
        tech["latency_ms"] = int(tech["latency_ms"]) + ms
        premium_block = {
            "system_prompt": system,
            "user_prompt": user,
            "raw": raw,
            "parsed": _parse(raw),
        }

    pack = {
        "case_no": case_no,
        "case_title": f"Case {case_no:02d} — {sc.get('label')}",
        "scenario_id": sc["id"],
        "label": sc.get("label"),
        "inputs": {
            "access_tier": sc.get("tier"),
            "source_depth": depth,
            "honesty_line": honesty,
            "allowed_claims": claims,
            "person": sc.get("person"),
            "birth_date": sc.get("birth_date"),
            "astro": sc.get("astro"),
            "numerology": sc.get("numerology"),
            "baseline": sc.get("baseline"),
            "onboarding": sc.get("onboarding"),
            "living": sc.get("living"),
            "user_question": sc.get("user_question"),
            "missing_or_hidden": sc.get("missing_or_hidden"),
            "locale": locale,
            "data_classes": {
                "facts": ["birth_date", "person"],
                "calculated": ["astro", "numerology", "baseline"],
                "self_descriptions": ["onboarding"],
                "system_inferences": ["portrait_llm"],
                "hypotheses_forbidden_as_fact": True,
            },
        },
        "prompt": {
            "funnel_steps": [
                {
                    "step": s["step"],
                    "prompt_id": s["prompt_id"],
                    "prompt_version": s["prompt_version"],
                    "system_prompt": s["system_prompt"],
                    "user_prompt": s["user_prompt"],
                    "generation_params": {
                        "model": s["model"],
                        "temperature": s["temperature"],
                        "max_tokens": s["max_tokens"],
                    },
                }
                for s in funnel["steps"]
            ],
            "premium_step": {
                "system_prompt": premium_block["system_prompt"],
                "user_prompt": premium_block["user_prompt"],
            }
            if premium_block
            else None,
        },
        "raw_model_response": {
            "steps": [{"step": s["step"], "raw": s["raw_responses"]} for s in funnel["steps"]],
            "premium_raw": premium_block["raw"] if premium_block else None,
        },
        "final_product": {
            "parsed_contract_current": merged,
            "premium_parsed": premium_block["parsed"] if premium_block else None,
            "validation": {"errors": validation_errors, "ok": tech.get("quality_ok")},
            "user_facing": _map_user_facing(merged, honesty=honesty, depth=depth),
            "postprocess_changes": [
                "merged_4_step_funnel",
                "onboarding_injected_into_living_for_eval",
            ],
            "retry": funnel["retry_count"] > 0,
            "fallback": funnel["fallback"],
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
        },
    }
    return pack


def pack_to_markdown(pack: dict[str, Any]) -> str:
    lines = [
        f"# {pack['case_title']}",
        "",
        f"**scenario_id:** `{pack['scenario_id']}`",
        "",
        "## 1. Входные данные (разрешённый контекст)",
        "",
        "```json",
        json.dumps(pack["inputs"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## 2. Фактический запрос модели",
        "",
    ]
    prompt = pack.get("prompt") or {}
    for step in prompt.get("funnel_steps") or []:
        lines += [
            f"### Step `{step['step']}` — {step['prompt_id']} @ {step['prompt_version']}",
            "",
            f"params: `{json.dumps(step['generation_params'], ensure_ascii=False)}`",
            "",
            "#### System",
            "```",
            step["system_prompt"],
            "```",
            "",
            "#### User",
            "```json",
            step["user_prompt"],
            "```",
            "",
        ]
    if prompt.get("premium_step"):
        lines += [
            "### Premium application step",
            "```",
            prompt["premium_step"]["system_prompt"],
            "```",
            "```json",
            prompt["premium_step"]["user_prompt"],
            "```",
            "",
        ]
    lines += [
        "## 3. Сырой ответ модели",
        "",
        "```json",
        json.dumps(pack.get("raw_model_response"), ensure_ascii=False, indent=2)[:120000],
        "```",
        "",
        "## 4. Итоговый ответ продукта",
        "",
        "```json",
        json.dumps(pack.get("final_product"), ensure_ascii=False, indent=2),
        "```",
        "",
        "## Техническая информация",
        "",
        "```json",
        json.dumps(pack.get("tech"), ensure_ascii=False, indent=2),
        "```",
        "",
        "## Ваша оценка",
        "",
        "* Что понравилось:",
        "* Что звучит плохо:",
        "* Что повторяется:",
        "* Что выглядит выдуманным:",
        "* Чего не хватает:",
        "* Можно ли показывать: да / после правок / нет",
        "* Оценка: 1–10",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", default="first10")
    args = ap.parse_args()
    doc = json.loads((Path(__file__).parent / "scenarios_v1.json").read_text(encoding="utf-8"))
    by_id = {s["id"]: s for s in doc["scenarios"]}
    ids = FIRST_BATCH if args.batch == "first10" else FIRST_BATCH
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(__file__).parent / "runs" / f"review_packs_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    index = []
    for i, sid in enumerate(ids, start=1):
        sc = by_id[sid]
        print(f"[{i}/10] {sid} …", flush=True)
        pack = run_one(sc, i)
        stem = f"case_{i:02d}_{sid}_{sc.get('tier')}"
        (out_dir / f"{stem}.json").write_text(
            json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (out_dir / f"{stem}.md").write_text(pack_to_markdown(pack), encoding="utf-8")
        index.append(
            {
                "case_no": i,
                "scenario_id": sid,
                "tier": sc.get("tier"),
                "source_depth": pack["inputs"]["source_depth"],
                "quality_ok": (pack.get("tech") or {}).get("quality_ok"),
                "latency_ms": (pack.get("tech") or {}).get("latency_ms"),
                "errors": (pack.get("tech") or {}).get("validation_errors"),
                "completed_steps": (pack.get("tech") or {}).get("completed_steps"),
                "json": f"{stem}.json",
                "md": f"{stem}.md",
            }
        )
        print(
            f"  ok={index[-1]['quality_ok']} ms={index[-1]['latency_ms']} "
            f"steps={index[-1]['completed_steps']} errs={index[-1]['errors']}",
            flush=True,
        )
    (out_dir / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "ARCHITECTURE_NOTE.md").write_text(
        "\n".join(
            [
                "# Architecture note (from packs)",
                "",
                "LLM-on-read risk callers:",
                *[f"- {x}" for x in LLM_ON_READ_RISK_CALLERS],
                "",
                "Safe snapshot callers:",
                *[f"- {x}" for x in SAFE_SNAPSHOT_CALLERS],
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("DONE", out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
