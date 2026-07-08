#!/usr/bin/env python3
"""Parity check between meta templates and i18n/en.json."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

REPO_ROOT = Path(__file__).resolve().parents[1]
META_FILE = REPO_ROOT / "CONTENT" / "paragraph_templates_v1.meta.jsonl"
EN_FILE = REPO_ROOT / "CONTENT" / "i18n" / "en.json"
VERSION_FILE = REPO_ROOT / "CONTENT" / "version.json"


@dataclass(frozen=True)
class MetaVariant:
    paragraph_id: str
    variant_id: str

    @property
    def key(self) -> str:
        return f"{self.paragraph_id}.{self.variant_id}"


def load_meta_variants(path: Path) -> tuple[list[MetaVariant], set[str]]:
    variants: list[MetaVariant] = []
    full_only: set[str] = set()

    with path.open(encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"Failed to parse meta line {line_number}: {exc}") from exc

            paragraph_id = record["paragraph_id"]
            if not record.get("lite_allowed", False):
                full_only.add(paragraph_id)

            for variant in record.get("variants", []):
                variants.append(MetaVariant(paragraph_id=paragraph_id, variant_id=variant["variant_id"]))

    if not variants:
        raise SystemExit(f"No variants found in {path}")
    return variants, full_only


def load_en_strings(path: Path) -> set[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Failed to parse {path}: {exc}") from exc
    return set(data.keys())


def load_versions(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Failed to parse {path}: {exc}") from exc


def report(title: str, items: Iterator[str]) -> None:
    items = list(items)
    if not items:
        return
    print(f"\n{title} ({len(items)}):")
    for item in items:
        print(f"  - {item}")


def main() -> None:
    if not META_FILE.exists():
        raise SystemExit(f"Meta file not found: {META_FILE}")
    if not EN_FILE.exists():
        raise SystemExit(f"i18n file not found: {EN_FILE}")

    meta_variants, full_only = load_meta_variants(META_FILE)
    expected_keys = {mv.key for mv in meta_variants}
    en_keys = load_en_strings(EN_FILE)

    missing = sorted(expected_keys - en_keys)
    extra = sorted(en_keys - expected_keys)

    versions = load_versions(VERSION_FILE)
    content_version = versions.get("content_version")
    i18n_version = versions.get("i18n_version")

    print("=== Parity Check ===")
    print(f"Meta entries: {len(meta_variants)} variants")
    print(f"EN strings: {len(en_keys)} keys")
    print(f"Content version: {content_version} · i18n version: {i18n_version}")

    report("Missing i18n keys", missing)
    report("Orphan i18n keys", extra)
    report("Full-only paragraphs (lite disabled)", sorted(full_only))

    errors = len(missing) + len(extra)
    status = "PASS" if errors == 0 else "FAIL"
    print(f"\nStatus: {status}")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
