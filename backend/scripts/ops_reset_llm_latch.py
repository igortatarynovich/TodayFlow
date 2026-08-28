#!/usr/bin/env python3
"""Ops helper: verify paid chat/completions works and reset the LLM spend latch.

Run this after Token Factory billing has been topped up. It makes a minimal paid
chat/completions call (not /models) and, if it succeeds, resets the local
llm_spend.json latch so the product can resume generation.

Canon: docs/LLM_QUALITY_AND_PROMPT_EVOLUTION.md (Cost Containment)
Tracker: docs/PRODUCT_EXECUTION_TRACKER.md (NOW ARCH / LLM 2026-08-25)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

import httpx


def _load_env() -> dict[str, str]:
    """Read repo-root .env as key=value pairs (no quoting expansion)."""
    repo_root = Path(__file__).resolve().parents[3]
    env_path = repo_root / ".env"
    env: dict[str, str] = {}
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def _ledger_path(env: dict[str, str]) -> Path:
    raw = env.get("LLM_SPEND_LEDGER_PATH", "").strip()
    if raw:
        return Path(raw)
    usage = env.get("LLM_USAGE_LOG_PATH", "").strip()
    if usage:
        return Path(usage).with_name("llm_spend.json")
    return Path("/tmp/todayflow_llm_spend.json")


def _chat_smoke_test(
    *,
    api_key: str,
    base_url: str,
    model: str,
) -> bool:
    """Return True iff paid chat/completions returns 200."""
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 1,
        "stream": False,
    }
    try:
        resp = httpx.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60.0,
        )
    except Exception as exc:
        print(f"FAIL: provider request threw {exc}")
        return False

    print(f"provider status: {resp.status_code}")
    if resp.status_code == 402:
        print("FAIL: billing suspended (402) — top up Token Factory before resetting latch.")
        return False
    if resp.status_code != 200:
        print(f"FAIL: unexpected status {resp.status_code}: {resp.text[:200]}")
        return False

    print("OK: paid chat/completions returned 200.")
    return True


def _reset_latch(path: Path) -> None:
    """Reset llm_spend.json to today's UTC date with tripped=false."""
    today = datetime.now(UTC).date().isoformat()
    payload = {
        "date": today,
        "spent_usd": 0.0,
        "reserved_usd": 0.0,
        "tripped": False,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"OK: reset latch at {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify paid chat/completions and reset LLM spend latch.")
    parser.add_argument("--skip-smoke", action="store_true", help="skip provider smoke test (only reset latch)")
    parser.add_argument("--model", default="moonshotai/Kimi-K2.6", help="model for smoke test")
    args = parser.parse_args()

    env = _load_env()
    api_key = env.get("NEBIUS_API_KEY") or env.get("OPENAI_API_KEY") or env.get("LLM_CHAT_API_KEY")
    base_url = env.get("NEBIUS_BASE_URL", "https://api.tokenfactory.us-central1.nebius.com/v1/")

    if not api_key:
        print("FAIL: no API key found in .env (NEBIUS_API_KEY / OPENAI_API_KEY / LLM_CHAT_API_KEY)")
        return 1

    if not args.skip_smoke:
        if not _chat_smoke_test(api_key=api_key, base_url=base_url, model=args.model):
            return 2

    ledger_path = _ledger_path(env)
    _reset_latch(ledger_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
