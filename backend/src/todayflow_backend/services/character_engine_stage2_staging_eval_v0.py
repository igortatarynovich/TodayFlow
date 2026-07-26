"""Stage 2 Identity Core staging evaluation — fixed Stage 0–1 fixtures + live LLM.

Run (requires LLM configured):
  PYTHONPATH=src .venv/bin/python -m todayflow_backend.services.character_engine_stage2_staging_eval_v0

Structural gates do not score literary quality. Voice/exit notes are diagnostics for humans.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from todayflow_backend.services.character_engine_identity_thesis_registry_v0 import (
    normalize_identity_thesis_key,
)
from todayflow_backend.services.character_engine_stage01_shadow_v0 import (
    run_character_engine_stage01_shadow_v0,
)
from todayflow_backend.services.character_engine_stage2_identity_v0 import (
    build_character_engine_identity_core_v0,
)

FIXTURE_PATH = (
    Path(__file__).resolve().parents[3]
    / "tests"
    / "fixtures"
    / "character_engine_stage01_staging_profiles_v0.json"
)
_REPO_FIXTURE = (
    Path(__file__).resolve().parents[4]
    / "backend/tests/fixtures/character_engine_stage01_staging_profiles_v0.json"
)

_CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
_SYSTEMISH_RE = re.compile(
    r"(?i)\b(llm|prompt|json|snapshot|character engine|stage\s*[012]|system|модель|промпт)\b"
)
_TRAIT_LIST_RE = re.compile(r"(?i)(;|,).+(;|,).+")
_FORMAL_VY_RE = re.compile(r"(?i)(?:^|[^\w])(вы|вам|вас|ваш|ваша|ваше|ваши)(?:[^\w]|$)")


def _load_profiles() -> list[dict[str, Any]]:
    path = FIXTURE_PATH if FIXTURE_PATH.is_file() else _REPO_FIXTURE
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("profiles") or [])


def _surface_diagnostics(surface: str | None, *, locale: str) -> dict[str, Any]:
    text = (surface or "").strip()
    if not text:
        return {
            "has_surface": False,
            "cyrillic": False,
            "systemish": False,
            "looks_like_trait_list": False,
            "formal_vy": False,
            "char_len": 0,
        }
    return {
        "has_surface": True,
        "cyrillic": bool(_CYRILLIC_RE.search(text)),
        "systemish": bool(_SYSTEMISH_RE.search(text)),
        "looks_like_trait_list": bool(_TRAIT_LIST_RE.search(text)) and text.count(",") >= 2,
        "formal_vy": bool(_FORMAL_VY_RE.search(text)),
        "char_len": len(text),
    }


def _summarize_case(profile: dict[str, Any], stage01: dict[str, Any], stage2: dict[str, Any]) -> dict[str, Any]:
    claims = (stage01.get("stage1") or {}).get("claims") or []
    stage1_theses = [c.get("thesis_key") for c in claims if isinstance(c, dict)]
    core = stage2.get("identity_core") if isinstance(stage2.get("identity_core"), dict) else None
    surface = (core or {}).get("surface_text")
    diag = stage2.get("diagnostics") if isinstance(stage2.get("diagnostics"), dict) else {}
    validation = stage2.get("validation") if isinstance(stage2.get("validation"), dict) else {}
    status = str(stage2.get("status") or "")
    primary_thesis = None
    identity_thesis = None
    if core:
        # After validation, thesis_key is normalized identity thesis.
        identity_thesis = core.get("thesis_key")
        primary_id = core.get("primary_claim_id")
        for c in claims:
            if isinstance(c, dict) and c.get("claim_id") == primary_id:
                primary_thesis = c.get("thesis_key")
                break
    return {
        "id": profile.get("id"),
        "label": profile.get("label"),
        "stage1_claim_count": len(claims),
        "stage1_thesis_keys": stage1_theses,
        "status": status,
        "primary_stage1_thesis": primary_thesis,
        "identity_thesis": identity_thesis,
        "identity_thesis_mapped": bool(
            primary_thesis and normalize_identity_thesis_key(str(primary_thesis))
        )
        if primary_thesis
        else (status == "insufficient_identity_core"),
        "surface_text": (surface or "")[:320] or None,
        "selection_rationale": (diag.get("selection_rationale") or "")[:280] or None,
        "contract_errors": diag.get("contract_errors") or [],
        "validation": validation,
        "voice": _surface_diagnostics(surface, locale="ru"),
        "prompt_version": diag.get("prompt_version"),
    }


def evaluate_stage2_staging_v0(*, locale: str = "ru") -> dict[str, Any]:
    profiles = _load_profiles()
    cases: list[dict[str, Any]] = []
    for profile in profiles:
        stage01 = run_character_engine_stage01_shadow_v0(
            profile_fingerprint=str(profile["profile_fingerprint"]),
            swiss_chart=profile.get("swiss_chart"),
            numerology=profile.get("numerology"),
            natal_facts_bridge=profile.get("natal_facts_bridge"),
            capability=profile.get("capability"),
            birth_date=profile.get("birth_date"),
            input_fingerprint=str(profile["profile_fingerprint"]),
        )
        facts = stage01.get("stage0") or {}
        evidence = stage01.get("stage1") or {}
        try:
            stage2 = build_character_engine_identity_core_v0(
                facts_pack=facts,
                evidence=evidence,
                locale=locale,
            )
        except Exception as exc:  # noqa: BLE001
            stage2 = {
                "status": "insufficient_identity_core",
                "identity_core": None,
                "diagnostics": {
                    "selection_rationale": f"stage2_exception:{type(exc).__name__}",
                    "contract_errors": [{"code": "stage2_exception", "exc": type(exc).__name__}],
                    "prompt_version": "error",
                },
                "validation": {},
            }
        cases.append(_summarize_case(profile, stage01, stage2))

    status_freq = Counter(str(c.get("status")) for c in cases)
    identity_freq = Counter(
        str(c.get("identity_thesis"))
        for c in cases
        if c.get("status") == "grounded" and c.get("identity_thesis")
    )
    grounded = [c for c in cases if c.get("status") == "grounded"]
    insufficient = [c for c in cases if c.get("status") == "insufficient_identity_core"]
    n = max(len(cases), 1)

    empty_stage1_ids = {c["id"] for c in cases if not (c.get("stage1_thesis_keys") or [])}
    empty_stage1_ok = all(
        c.get("status") == "insufficient_identity_core"
        for c in cases
        if c.get("id") in empty_stage1_ids
    )

    gates = {
        "all_statuses_known": all(
            c.get("status") in {"grounded", "insufficient_identity_core"} for c in cases
        ),
        "empty_stage1_becomes_insufficient": empty_stage1_ok,
        "leo_negative_insufficient": any(
            c.get("id") == "date_only" and c.get("status") == "insufficient_identity_core" for c in cases
        ),
        "no_contract_errors_on_grounded": all(
            not (c.get("contract_errors") or []) for c in grounded
        ),
        "grounded_have_surface": all((c.get("voice") or {}).get("has_surface") for c in grounded),
        "grounded_thesis_mapped": all(c.get("identity_thesis_mapped") for c in grounded),
        "grounded_validation_ok": all(
            bool((c.get("validation") or {}).get("refs_resolve"))
            and bool((c.get("validation") or {}).get("no_invented_claims"))
            for c in grounded
        ),
        "no_systemish_surface": all(not (c.get("voice") or {}).get("systemish") for c in grounded),
        "no_formal_vy_surface": all(not (c.get("voice") or {}).get("formal_vy") for c in grounded),
        "ru_locale_prefers_cyrillic": (
            all((c.get("voice") or {}).get("cyrillic") for c in grounded) if locale.startswith("ru") else True
        ),
        "identity_thesis_not_majority": all(
            (cnt / max(len(grounded), 1)) <= 0.5 for cnt in identity_freq.values()
        )
        if grounded
        else True,
        "at_least_half_nonempty_stage1_grounded": (
            (len(grounded) / max(len(cases) - len(empty_stage1_ids), 1)) >= 0.5
        ),
    }

    return {
        "eval_version": "character_engine_stage2_staging_eval_v0",
        "locale": locale,
        "profile_count": len(cases),
        "status_frequency": dict(status_freq),
        "grounded_count": len(grounded),
        "insufficient_count": len(insufficient),
        "identity_thesis_frequency": dict(identity_freq),
        "cases": cases,
        "gates": gates,
        "gate_pass": all(gates.values()),
        "exit_criterion_notes": [
            {
                "id": c["id"],
                "probe": "This is a manifestation of the Identity Core because…",
                "identity_thesis": c.get("identity_thesis"),
                "surface_text": c.get("surface_text"),
                "rationale": c.get("selection_rationale"),
            }
            for c in grounded
        ],
        "publish_semantics_unchanged": True,
        "note": (
            "Diagnostics-only. Literary quality / exit-criterion feel are human-reviewed "
            "via exit_criterion_notes — not hard quality heuristics in code."
        ),
        "grounded_share_of_all": round(len(grounded) / n, 3),
    }


def main() -> int:
    report = evaluate_stage2_staging_v0(locale="ru")
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "eval_version",
                    "locale",
                    "profile_count",
                    "status_frequency",
                    "grounded_count",
                    "insufficient_count",
                    "identity_thesis_frequency",
                    "grounded_share_of_all",
                    "gates",
                    "gate_pass",
                )
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    for case in report["cases"]:
        surface = (case.get("surface_text") or "")[:90]
        print(
            f"- {case['id']}: status={case['status']} s1={case['stage1_thesis_keys']} "
            f"id_thesis={case.get('identity_thesis')} err={case.get('contract_errors')} "
            f"surface={surface!r}"
        )
    return 0 if report["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
