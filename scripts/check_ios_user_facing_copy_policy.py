#!/usr/bin/env python3
"""Fail if iOS user-facing copy contains prohibited framing."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
IOS_ROOT = REPO_ROOT / "ios" / "TodayFlow" / "TodayFlow"

# Keep scope focused on user-visible copy sources.
SCAN_DIRS = [
    IOS_ROOT / "Views",
    IOS_ROOT / "App",
    IOS_ROOT / "Models",
]

ALLOWED_EXTENSIONS = {".swift"}

FORBIDDEN_PATTERNS = [
    re.compile(r"\bAI\b", re.IGNORECASE),
    re.compile(r"\bLLM\b", re.IGNORECASE),
    re.compile(r"model-based", re.IGNORECASE),
    re.compile(r"iskusstvenn(?:yy|ogo)?\s+intellekt", re.IGNORECASE),
    re.compile(r"искусственн(?:ый|ого)\s+интеллект", re.IGNORECASE),
    re.compile(r"нейросет", re.IGNORECASE),
    re.compile(r"генератив", re.IGNORECASE),
    re.compile(r"\bпродукт\w*\b", re.IGNORECASE),
    re.compile(r"как\s+это\s+работает", re.IGNORECASE),
    re.compile(r"как\s+устроен", re.IGNORECASE),
    re.compile(r"как\s+считается", re.IGNORECASE),
    re.compile(r"внутренн\w+\s+расчет", re.IGNORECASE),
    re.compile(r"\bформул(а|ы|у|ой|е)\b", re.IGNORECASE),
]

PRESSURE_FEAR_PATTERNS = [
    re.compile(r"\bсрочно\b", re.IGNORECASE),
    re.compile(r"если\s+не\s+.+(потеря|хуже|проблем|опасн)", re.IGNORECASE),
    re.compile(r"\bиначе\s+будет\b", re.IGNORECASE),
    re.compile(r"\bиначе\s+ты\s+(потеря|упуст|останешь)", re.IGNORECASE),
    re.compile(r"\bдолжен\b\s+прямо\s+сейчас", re.IGNORECASE),
]


def iter_files() -> list[Path]:
    files: list[Path] = []
    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for path in scan_dir.rglob("*"):
            if path.is_file() and path.suffix in ALLOWED_EXTENSIONS:
                files.append(path)
    return sorted(files)


def main() -> None:
    files = iter_files()
    if not files:
        raise SystemExit("No iOS files found for copy policy scan.")

    violations: list[str] = []

    for path in files:
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for pattern in [*FORBIDDEN_PATTERNS, *PRESSURE_FEAR_PATTERNS]:
                match = pattern.search(line)
                if not match:
                    continue
                relative = path.relative_to(REPO_ROOT)
                violations.append(f"{relative}:{line_number}: {match.group(0)}")

    if violations:
        print("iOS copy policy check failed. Prohibited terms found:\n")
        for violation in violations:
            print(f"- {violation}")
        raise SystemExit(1)

    print(f"iOS copy policy check passed ({len(files)} files scanned).")


if __name__ == "__main__":
    main()
