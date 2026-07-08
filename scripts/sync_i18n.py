#!/usr/bin/env python3
"""Sync EN i18n data and meta records from the canonical paragraph templates."""

from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_PATH = REPO_ROOT / "CONTENT" / "paragraph_templates_v1.jsonl"
META_PATH = REPO_ROOT / "CONTENT" / "paragraph_templates_v1.meta.jsonl"
I18N_DIR = REPO_ROOT / "CONTENT" / "i18n"
EN_PATH = I18N_DIR / "en.json"


def load_templates(path: Path) -> List[dict]:
    templates: List[dict] = []
    with path.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            templates.append(json.loads(line))
    return templates


def build_meta_and_en_entries(templates: Iterable[dict]) -> Tuple[List[dict], Dict[str, str]]:
    meta_records: List[dict] = []
    en_entries: Dict[str, str] = OrderedDict()

    for template in templates:
        paragraph_id = template["paragraph_id"]
        variants = template.get("variants", [])
        if not variants:
            raise ValueError(f"{paragraph_id} is missing variants.")

        meta_record = {key: value for key, value in template.items() if key != "variants"}
        meta_record["variants"] = [{"variant_id": variant["variant_id"]} for variant in variants]
        meta_records.append(meta_record)

        for variant in variants:
            key = f"{paragraph_id}.{variant['variant_id']}"
            text = variant["text"]
            if not text:
                raise ValueError(f"{key} has an empty text value.")
            if key in en_entries:
                raise ValueError(f"Duplicate variant key detected: {key}")
            en_entries[key] = text

    return meta_records, en_entries


def write_meta_file(path: Path, records: Iterable[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False))
            handle.write("\n")


def write_en_file(path: Path, entries: Dict[str, str]) -> None:
    formatted = json.dumps(entries, ensure_ascii=False, indent=2)
    path.write_text(formatted + "\n", encoding="utf-8")


def validate_translations(en_entries: Dict[str, str], directory: Path) -> None:
    """Validate paragraph template translations only (skip app.*.json files)"""
    en_keys = set(en_entries.keys())
    
    # Only validate paragraph template files (not app.*.json)
    for locale_file in sorted(directory.glob("*.json")):
        if locale_file.name == "en.json" or locale_file.name.startswith("app."):
            continue

        try:
            data = json.loads(locale_file.read_text(encoding="utf-8"))
            locale_keys = set(data.keys())

            # Only check paragraph template keys (format: "XX-XXX-XXX.v1")
            paragraph_keys_en = {k for k in en_keys if "." in k and k.split(".")[0].startswith(("EP-", "RL-", "CAR-", "FIN-", "MS-", "LT-", "CR-"))}
            paragraph_keys_locale = {k for k in locale_keys if "." in k and k.split(".")[0].startswith(("EP-", "RL-", "CAR-", "FIN-", "MS-", "LT-", "CR-"))}

            # If locale file is empty, it's OK - will use EN fallback
            if len(paragraph_keys_locale) == 0:
                continue

            missing = sorted(paragraph_keys_en - paragraph_keys_locale)
            extra = sorted(paragraph_keys_locale - paragraph_keys_en)
            empty = sorted(key for key, value in data.items() if key in paragraph_keys_locale and not value.strip())

            if missing or extra or empty:
                raise SystemExit(
                    f"i18n structural validation failed for {locale_file.name}.\n"
                    f"Missing paragraph keys: {len(missing)} (showing first 10: {missing[:10]})\n"
                    f"Extra paragraph keys: {len(extra)} (showing first 10: {extra[:10]})\n"
                    f"Empty paragraph values: {len(empty)} (showing first 10: {empty[:10]})"
                )
        except json.JSONDecodeError:
            print(f"Warning: Skipping invalid JSON file {locale_file.name}")
            continue


def main() -> None:
    templates = load_templates(TEMPLATES_PATH)
    meta_records, en_entries = build_meta_and_en_entries(templates)

    write_meta_file(META_PATH, meta_records)
    write_en_file(EN_PATH, en_entries)
    validate_translations(en_entries, I18N_DIR)


if __name__ == "__main__":
    main()
