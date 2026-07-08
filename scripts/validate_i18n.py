#!/usr/bin/env python3
"""Validate TodayFlow i18n files against structural and style rules."""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
I18N_DIR = REPO_ROOT / "CONTENT" / "i18n"
EN_FILE = I18N_DIR / "en.json"
APP_EN_FILE = I18N_DIR / "app.en.json"

VARIANT_KEY_PATTERN = re.compile(r"^(?P<paragraph>.+)\.(?P<variant>v\d+)$")
WORD_PATTERN = re.compile(r"\w+", flags=re.UNICODE)

RECOMMENDED_MIN = 180
RECOMMENDED_MAX = 320
ALLOWED_MIN = int(RECOMMENDED_MIN * 0.8)  # ±20%
ALLOWED_MAX = int(RECOMMENDED_MAX * 1.2)

BANNED_PATTERNS = [
    re.compile(r"\byou\s+need\s+to\b", re.IGNORECASE),
    re.compile(r"\bmust\b", re.IGNORECASE),
    re.compile(r"\bshould\b", re.IGNORECASE),
    re.compile(r"\bhave\s+to\b", re.IGNORECASE),
    re.compile(r"\balways\b", re.IGNORECASE),
    re.compile(r"\bnever\b", re.IGNORECASE),
    re.compile(r"\bdisorder\b", re.IGNORECASE),
    re.compile(r"\btrauma\b", re.IGNORECASE),
    re.compile(r"\bpathology\b", re.IGNORECASE),
    re.compile(r"\bdestiny\b", re.IGNORECASE),
    re.compile(r"\bfate\b", re.IGNORECASE),
    re.compile(r"\bkarma\b", re.IGNORECASE),
    re.compile(r"\bmeant\s+to\b", re.IGNORECASE),
]


@dataclass
class LocaleIssues:
    locale: str
    errors: List[str]

    def extend(self, messages: Iterable[str]) -> None:
        self.errors.extend(messages)

    def report(self) -> str:
        header = f"[{self.locale}] {len(self.errors)} issue(s)"
        details = "\n".join(f"  - {msg}" for msg in self.errors)
        return f"{header}\n{details}"


def load_locale(path: Path) -> Dict[str, str]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Failed to parse {path}: {exc}") from exc


def parse_variant_key(key: str) -> Tuple[str, str]:
    match = VARIANT_KEY_PATTERN.match(key)
    if not match:
        raise ValueError(f"Invalid variant key format: {key}")
    return match.group("paragraph"), match.group("variant")


def group_by_paragraph(entries: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    grouped: Dict[str, Dict[str, str]] = defaultdict(dict)
    for key, value in entries.items():
        paragraph_id, variant_id = parse_variant_key(key)
        grouped[paragraph_id][variant_id] = value
    return grouped


def structural_checks(
    locale_entries: Dict[str, str],
    en_keys: set[str],
    en_variants: Dict[str, set[str]],
) -> List[str]:
    locale_keys = set(locale_entries.keys())
    issues: List[str] = []

    missing = sorted(en_keys - locale_keys)
    extra = sorted(locale_keys - en_keys)

    if missing:
        issues.append(f"Missing keys: {', '.join(missing[:5])}" + (" ..." if len(missing) > 5 else ""))
    if extra:
        issues.append(f"Extra keys: {', '.join(extra[:5])}" + (" ..." if len(extra) > 5 else ""))

    grouped = group_by_paragraph(locale_entries)
    for paragraph_id, expected_variants in en_variants.items():
        locale_variants = set(grouped.get(paragraph_id, {}).keys())
        if locale_variants != expected_variants:
            issues.append(
                f"{paragraph_id} variant mismatch "
                f"(expected {sorted(expected_variants)}, got {sorted(locale_variants)})"
            )

    for key, value in locale_entries.items():
        if not value.strip():
            issues.append(f"{key} has an empty translation.")

    return issues


def length_check(text: str) -> bool:
    length = len(text)
    return ALLOWED_MIN <= length <= ALLOWED_MAX


def variant_diversity(paragraph_variants: Dict[str, str]) -> bool:
    normalized = set()
    for text in paragraph_variants.values():
        words = WORD_PATTERN.findall(text.lower())
        prefix = " ".join(words[:6])
        normalized.add(prefix)
    return len(normalized) > 1


def style_checks(locale_entries: Dict[str, str], locale_code: str) -> List[str]:
    grouped = group_by_paragraph(locale_entries)
    issues: List[str] = []

    for key, text in locale_entries.items():
        for pattern in BANNED_PATTERNS:
            if pattern.search(text):
                issues.append(f"{key} contains banned phrase: '{pattern.pattern}'")
                break

        if not length_check(text):
            issues.append(f"{key} length {len(text)} chars is outside {ALLOWED_MIN}-{ALLOWED_MAX}.")

    for paragraph_id, variants in grouped.items():
        if len(variants) < 2:
            continue
        if not variant_diversity(variants):
            issues.append(f"{paragraph_id} variants start with the same first words.")

    # Placeholder for language-specific hooks
    locale_specific_rules(locale_code, locale_entries, issues)
    return issues


def locale_specific_rules(locale_code: str, entries: Dict[str, str], issues: List[str]) -> None:
    """Hook for future per-locale rules per Section 5 of the i18n spec."""
    _ = locale_code, entries  # currently unused
    # When new requirements emerge (e.g., tone constraints for SV/NO/DA),
    # implement them here to keep the validator centralized.


def validate_app_catalogs() -> List[LocaleIssues]:
    """Ensure non-paragraph app catalogs (app.en.json) stay in sync across locales."""
    if not APP_EN_FILE.exists():
        return []

    base_entries = load_locale(APP_EN_FILE)
    base_keys = set(base_entries.keys())
    issues: List[LocaleIssues] = []

    for locale_path in sorted(I18N_DIR.glob("app.*.json")):
        if locale_path == APP_EN_FILE:
            continue
        locale_code = locale_path.stem.split(".", 1)[-1]
        locale_entries = load_locale(locale_path)
        locale_keys = set(locale_entries.keys())

        missing = sorted(base_keys - locale_keys)
        extra = sorted(locale_keys - base_keys)
        empty = sorted(key for key, value in locale_entries.items() if not str(value).strip())

        locale_issues = LocaleIssues(locale=f"app.{locale_code}", errors=[])
        if missing:
            locale_issues.errors.append(
                f"Missing keys: {', '.join(missing[:5])}" + (" ..." if len(missing) > 5 else "")
            )
        if extra:
            locale_issues.errors.append(
                f"Extra keys: {', '.join(extra[:5])}" + (" ..." if len(extra) > 5 else "")
            )
        if empty:
            locale_issues.errors.append(
                f"Empty values: {', '.join(empty[:5])}" + (" ..." if len(empty) > 5 else "")
            )
        if locale_issues.errors:
            issues.append(locale_issues)
    return issues


def main() -> None:
    if not EN_FILE.exists():
        raise SystemExit(f"Source file not found: {EN_FILE}")

    en_entries = load_locale(EN_FILE)
    en_keys = set(en_entries.keys())
    en_variants = {pid: set(variants.keys()) for pid, variants in group_by_paragraph(en_entries).items()}

    locale_files = sorted(
        path for path in I18N_DIR.glob("*.json") if path.name not in {"en.json"} and not path.name.startswith("app.")
    )
    if not locale_files:
        print("No locale files found. Nothing to validate.")
        return

    issues_found: List[LocaleIssues] = []

    for locale_file in locale_files:
        locale_code = locale_file.stem
        locale_entries = load_locale(locale_file)

        locale_issues = LocaleIssues(locale=locale_code, errors=[])
        locale_issues.extend(structural_checks(locale_entries, en_keys, en_variants))
        locale_issues.extend(style_checks(locale_entries, locale_code))

        if locale_issues.errors:
            issues_found.append(locale_issues)

    if issues_found:
        summary = "\n\n".join(issue.report() for issue in issues_found)
        print(summary)
        raise SystemExit(1)

    app_issues = validate_app_catalogs()
    if app_issues:
        issues_found.extend(app_issues)

    if issues_found:
        summary = "\n\n".join(issue.report() for issue in issues_found)
        print(summary)
        raise SystemExit(1)

    print("All locales passed i18n validation.")


if __name__ == "__main__":
    main()
