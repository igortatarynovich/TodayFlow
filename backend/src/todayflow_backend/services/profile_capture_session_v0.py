"""Production-faithful Profile capture session (sidecar packs).

Off by default. When enabled via context manager, records per-step
prompts / raw / parse / validation without changing user-facing results.

Never writes into generation_logs. Sidecar files are for eval/dev only.

Defect classes are architectural only (see DEFECT_CLASSES). There is no MODEL
blame class — mismatches are generation-architecture defects.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

CAPTURE_CONTRACT = "profile_production_capture_v0"

# Architectural defect classes only — no MODEL.
DEFECT_CLASSES = (
    "BLOCK_PURPOSE",
    "INSUFFICIENT_DATA",
    "INPUT",
    "PROMPT",
    "RESPONSE_SCHEMA",
    "VALIDATION",
    "GENERATION_GATE",
    "SNAPSHOT",
    "API",
    "PROJECTION",
    "UI_GATE",
)

_session_var: ContextVar["ProfileCaptureSession | None"] = ContextVar(
    "profile_capture_session_v0",
    default=None,
)


def get_profile_capture_session() -> "ProfileCaptureSession | None":
    return _session_var.get()


def profile_capture_enabled() -> bool:
    sess = _session_var.get()
    return bool(sess and sess.enabled)


class ProfileCaptureSession:
    """Mutable pack collector for one portrait publish."""

    def __init__(
        self,
        *,
        case_id: str,
        label: str = "",
        redact: bool = False,
        out_dir: Path | None = None,
    ) -> None:
        self.enabled = True
        self.case_id = case_id
        self.label = label
        self.redact = redact
        self.out_dir = out_dir
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.pack: dict[str, Any] = {
            "manifest": {
                "contract_version": CAPTURE_CONTRACT,
                "case_id": case_id,
                "label": label,
                "started_at": self.started_at,
                "production_path": True,
                "redacted": redact,
            },
            "inputs": None,
            "calculated_facts": None,
            "source_depth": None,
            "missing_fields": None,
            "allowed_claims": None,
            "block_eligibility": {
                "identity": None,
                "styles": None,
                "patterns": None,
                "spheres": None,
            },
            "steps": {
                "identity": {"attempts": []},
                "styles": {"attempts": []},
                "patterns": {"attempts": []},
                "spheres": {"attempts": []},
            },
            "final_contract_before_quality": None,
            "quality_validation": None,
            "final_contract_after_quality": None,
            "forming_fallback": None,
            "legacy_interpretation": None,
            "legacy_daily_interpretation": None,
            "snapshot_written": None,
            "core_profile_get_response": None,
            "frontend_projection": None,
            "visible_blocks": None,
            "claim_trace": [],
            "defects": [],
            "generation_metadata": {},
            "divergences": [],
        }

    def set_inputs(
        self,
        *,
        inputs: dict[str, Any],
        calculated_facts: dict[str, Any] | None = None,
        source_depth: str | None = None,
        missing_fields: list[str] | None = None,
        allowed_claims: dict[str, Any] | None = None,
    ) -> None:
        self.pack["inputs"] = self._maybe_redact(inputs)
        self.pack["calculated_facts"] = self._maybe_redact(calculated_facts or {})
        self.pack["source_depth"] = source_depth
        self.pack["missing_fields"] = list(missing_fields or [])
        self.pack["allowed_claims"] = allowed_claims
        if source_depth is not None or allowed_claims is not None:
            self._refresh_block_eligibility()

    def _refresh_block_eligibility(self) -> None:
        """Target gates from architecture — does not change production generation."""
        depth = self.pack.get("source_depth")
        allowed = self.pack.get("allowed_claims") if isinstance(self.pack.get("allowed_claims"), dict) else {}
        if allowed:
            patterns_ok = bool(allowed.get("recurring_patterns"))
        else:
            patterns_ok = depth in ("profile_plus_checkins", "longitudinal_profile")
        self.pack["block_eligibility"] = {
            "identity": {
                "may_generate": True,
                "reason": "general portrait allowed from birth/baseline",
                "min_source_depth": "birth_data_only",
                "ran": None,
            },
            "styles": {
                "may_generate": True,
                "reason": "cautious interpretation of baseline styles allowed",
                "min_source_depth": "birth_data_only",
                "ran": None,
            },
            "patterns": {
                "may_generate": patterns_ok,
                "reason": (
                    "confirmed recurring patterns require living/longitudinal evidence"
                    if not patterns_ok
                    else "living/check-in depth allows confirmed pattern claims"
                ),
                "min_source_depth": "profile_plus_checkins",
                "ran": None,
            },
            "spheres": {
                "may_generate": True,
                "reason": "spheres eligibility open until passport decides otherwise",
                "min_source_depth": "birth_data_only",
                "ran": None,
            },
        }

    def mark_step_ran(self, step: str, *, ran: bool = True) -> None:
        bucket = (self.pack.get("block_eligibility") or {}).get(step)
        if isinstance(bucket, dict):
            bucket["ran"] = ran
            may = bucket.get("may_generate")
            if ran and may is False:
                self.add_defect(
                    "generation_ran_while_ineligible",
                    f"step={step} ran but block_eligibility.may_generate=false "
                    f"(source_depth={self.pack.get('source_depth')})",
                    cls="GENERATION_GATE",
                )

    def record_step_attempt(
        self,
        step: str,
        *,
        prompt_id: str,
        prompt_version: str,
        system_prompt: str,
        user_prompt: str,
        model_request: dict[str, Any],
        raw_response: str | None,
        parsed_response: dict[str, Any] | None,
        validation_result: dict[str, Any],
        attempt_index: int,
        ms: int | None = None,
    ) -> None:
        bucket = self.pack["steps"].setdefault(step, {"attempts": []})
        bucket["attempts"].append(
            {
                "attempt_index": attempt_index,
                "prompt_id": prompt_id,
                "prompt_version": prompt_version,
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "model_request": model_request,
                "raw_response": raw_response,
                "parsed_response": parsed_response,
                "validation_result": validation_result,
                "ms": ms,
            }
        )

    def record_quality(
        self,
        *,
        before: dict[str, Any] | None,
        validation: dict[str, Any] | None,
        after: dict[str, Any] | None,
        forming_fallback: bool = False,
        generation_meta: dict[str, Any] | None = None,
    ) -> None:
        self.pack["final_contract_before_quality"] = self._maybe_redact(before)
        self.pack["quality_validation"] = validation
        self.pack["final_contract_after_quality"] = self._maybe_redact(after)
        self.pack["forming_fallback"] = forming_fallback
        if generation_meta:
            self.pack["generation_metadata"] = {
                **(self.pack.get("generation_metadata") or {}),
                **generation_meta,
            }

    def record_legacy(
        self,
        *,
        interpretation: dict[str, Any] | None,
        daily: dict[str, Any] | None,
    ) -> None:
        self.pack["legacy_interpretation"] = self._maybe_redact(interpretation)
        self.pack["legacy_daily_interpretation"] = self._maybe_redact(daily)

    def record_snapshot(self, payload: dict[str, Any] | None, *, persisted: bool = False) -> None:
        self.pack["snapshot_written"] = {
            "persisted": persisted,
            "payload": self._maybe_redact(payload),
        }

    def record_get_response(self, body: dict[str, Any] | None) -> None:
        self.pack["core_profile_get_response"] = self._maybe_redact(body)

    def record_frontend(
        self,
        *,
        projection: dict[str, Any] | None,
        visible_blocks: dict[str, Any] | None,
    ) -> None:
        self.pack["frontend_projection"] = self._maybe_redact(projection)
        self.pack["visible_blocks"] = self._maybe_redact(visible_blocks)

    def add_defect(self, code: str, detail: str, *, cls: str = "VALIDATION") -> None:
        if cls == "MODEL":
            cls = "GENERATION_GATE"
            detail = f"[reclassified from MODEL] {detail}"
        if cls not in DEFECT_CLASSES:
            detail = f"[unknown class={cls} normalized] {detail}"
            cls = "VALIDATION"
        self.pack["defects"].append({"code": code, "class": cls, "detail": detail})

    def add_divergence(
        self,
        *,
        claim: str,
        layer_from: str,
        layer_to: str,
        cls: str,
        note: str = "",
    ) -> None:
        self.pack["divergences"].append(
            {
                "claim": claim,
                "from": layer_from,
                "to": layer_to,
                "class": cls,
                "note": note,
            }
        )

    def build_claim_trace(self) -> None:
        """Heuristic claim → origin table for forensic reading."""
        rows: list[dict[str, Any]] = []
        after = self.pack.get("final_contract_after_quality") or {}
        before = self.pack.get("final_contract_before_quality") or after
        depth = self.pack.get("source_depth")

        def add(claim: str, origin: str, raw: bool, accepted: bool, **extra: Any) -> None:
            rows.append(
                {
                    "claim": claim[:200],
                    "origin": origin,
                    "raw": raw,
                    "accepted": accepted,
                    "snapshot": bool(after.get("identity_core") if "identity" in origin else True),
                    "source_depth": depth,
                    **extra,
                }
            )

        identity = str((before or {}).get("identity_core") or "").strip()
        if identity:
            add(identity, "identity LLM", True, True)

        for style_key in ("decision_style", "relationship_style", "money_style"):
            text = str((before or {}).get(style_key) or "").strip()
            if text:
                add(text[:160], f"styles LLM:{style_key}", True, True)

        patterns = (before or {}).get("recurring_patterns")
        if isinstance(patterns, list):
            for p in patterns:
                text = str(p or "").strip()
                if not text:
                    continue
                questionable = depth in (None, "birth_data_only", "onboarding_answers")
                add(
                    text,
                    "patterns LLM",
                    True,
                    not questionable,
                    questionable=questionable,
                    note="confirmed patterns require longitudinal evidence"
                    if questionable
                    else "",
                )
                if questionable:
                    self.add_defect(
                        "patterns_without_longitudinal_evidence",
                        f"recurring_pattern present at source_depth={depth}: {text[:120]} "
                        "(architecture: generation should not have run / schema should not require fill)",
                        cls="GENERATION_GATE",
                    )

        self.pack["claim_trace"] = rows

        steps = self.pack.get("steps") or {}
        for name in ("identity", "styles", "patterns", "spheres"):
            attempts = (steps.get(name) or {}).get("attempts") or []
            if attempts:
                self.mark_step_ran(name, ran=True)

        if depth == "birth_data_only" and isinstance(patterns, list) and any(
            str(p or "").strip() for p in patterns
        ):
            self.add_defect(
                "invariant_birth_only_confirmed_patterns",
                "source_depth=birth_data_only but recurring_patterns non-empty after quality — "
                "defect is GENERATION_GATE/RESPONSE_SCHEMA, not model invention",
                cls="GENERATION_GATE",
            )

    def write(self) -> Path | None:
        self.pack["manifest"]["finished_at"] = datetime.now(timezone.utc).isoformat()
        self.build_claim_trace()
        if self.out_dir is None:
            return None
        self.out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = self.out_dir / f"capture_{self.case_id}_{stamp}.json"
        path.write_text(json.dumps(self.pack, ensure_ascii=False, indent=2), encoding="utf-8")
        # compact sha for integrity
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        self.pack["manifest"]["pack_sha256_16"] = digest
        path.write_text(json.dumps(self.pack, ensure_ascii=False, indent=2), encoding="utf-8")
        md = self.out_dir / f"capture_{self.case_id}_{stamp}.md"
        md.write_text(self._markdown_summary(), encoding="utf-8")
        return path

    def _markdown_summary(self) -> str:
        m = self.pack.get("manifest") or {}
        defects = self.pack.get("defects") or []
        steps = self.pack.get("steps") or {}
        lines = [
            f"# Capture {m.get('case_id')}",
            "",
            f"- label: {m.get('label')}",
            f"- source_depth: {self.pack.get('source_depth')}",
            f"- forming_fallback: {self.pack.get('forming_fallback')}",
            f"- redacted: {m.get('redacted')}",
            "",
            "## Eligibility vs ran",
        ]
        elig = self.pack.get("block_eligibility") or {}
        for name in ("identity", "styles", "patterns", "spheres"):
            row = elig.get(name) or {}
            lines.append(
                f"- **{name}**: may_generate={row.get('may_generate')} ran={row.get('ran')} "
                f"— {row.get('reason')}"
            )
        lines.append("")
        lines.append("## Steps")
        for name in ("identity", "styles", "patterns", "spheres"):
            attempts = (steps.get(name) or {}).get("attempts") or []
            ok = any((a.get("validation_result") or {}).get("ok") for a in attempts)
            lines.append(f"- **{name}**: attempts={len(attempts)} ok={ok}")
        lines.append("")
        lines.append("## Defects (architectural classes only)")
        if not defects:
            lines.append("- (none recorded)")
        for d in defects:
            lines.append(f"- `{d.get('class')}` `{d.get('code')}`: {d.get('detail')}")
        lines.append("")
        lines.append("## Claim trace (abbrev)")
        for row in (self.pack.get("claim_trace") or [])[:12]:
            lines.append(
                f"- [{row.get('origin')}] accepted={row.get('accepted')} :: {row.get('claim')}"
            )
        return "\n".join(lines) + "\n"

    def _maybe_redact(self, value: Any) -> Any:
        if not self.redact:
            return copy.deepcopy(value)
        return _redact_value(value)


def _redact_value(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            lk = str(k).lower()
            if lk in {"first_name", "last_name", "display_name", "full_name"}:
                out[k] = "[redacted]"
            elif lk in {"birth_date", "location_name", "latitude", "longitude"}:
                out[k] = "[redacted]"
            else:
                out[k] = _redact_value(v)
        return out
    if isinstance(value, list):
        return [_redact_value(v) for v in value]
    if isinstance(value, str):
        # crude date scrub
        return re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "[date]", value)
    return value


@contextmanager
def profile_capture_session(
    *,
    case_id: str,
    label: str = "",
    redact: bool = False,
    out_dir: Path | str | None = None,
) -> Iterator[ProfileCaptureSession]:
    """Enable capture for the current context. No-op impact when not entered."""
    session = ProfileCaptureSession(
        case_id=case_id,
        label=label,
        redact=redact,
        out_dir=Path(out_dir) if out_dir else None,
    )
    token = _session_var.set(session)
    try:
        yield session
    finally:
        _session_var.reset(token)
