#!/usr/bin/env python3
"""TL-0A/TL-0B — extract RU Today phrase candidates from repo + auto-tag heuristics.

Usage (from repo root):
  PYTHONPATH=backend/src python backend/scripts/today_language_corpus_v0.py

Optional:
  --logs-dir PATH   merge JSON lines/files with generation log payloads (export from DB)
  --out PATH        output JSON (default: docs/datasets/TODAY_LANGUAGE_CORPUS_V0.json)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "backend" / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "backend" / "src"))

_CODE_MARKERS = (
    "function ",
    "=>",
    "import ",
    "export ",
    "const ",
    "return ",
    ".trim(",
    "parseInt",
    "reduce(",
    "typeof ",
    "undefined",
    "null;",
    "&&",
    "||",
    "{",
    "}",
    "();",
    "`",
    "${",
    "className",
)

_TS_RU_PROP_RE = re.compile(
    r'^\s+[A-Za-z_][A-Za-z0-9_]*:\s*"((?:[^"\\]|\\.)*[А-Яа-яЁё](?:[^"\\]|\\.)*)"',
    re.MULTILINE,
)

_CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
_RU_STRING_RE = re.compile(r'"(?:[^"\\]|\\.)*[А-Яа-яЁё](?:[^"\\]|\\.)*"', re.UNICODE)
_RU_STRING_SINGLE_RE = re.compile(r"'(?:[^'\\]|\\.)*[А-Яа-яЁё](?:[^'\\]|\\.)*'", re.UNICODE)

# --- Auto-tag heuristics (TL-0B); not production gate ---------------------------------

_SCENE_MARKERS = (
    r"поймать себя",
    r"возвращает",
    r"возвраща",
    r"разговор",
    r"сообщени",
    r"звонок",
    r"человек",
    r"кто-то",
    r"устал",
    r"устала",
    r"обещан",
    r"откладыва",
    r"не первую неделю",
    r"месяц назад",
    r"тему, которую",
    r"объясня",
    r"ждали ответ",
    r"переписыва",
    r"договорённост",
    r"план",
    r"задач",
    r"коллег",
    r"близк",
    r"партн",
    r"семь",
    r"дом",
    r"работ",
    r"деньг",
    r"покуп",
    r"клиент",
    r"проект",
    r"предложени",
    r"неожидан",
    r"случайн",
    r"логика говорит",
    r"внутренн",
    r"ощущени.*тян",
    r"топчет",
    r"пересмотр",
)

_TRIGGER_MARKERS = (
    r"сообщени",
    r"звонок",
    r"разговор",
    r"конфликт",
    r"предложени",
    r"ответ",
    r"встреч",
    r"человек",
    r"кто-то",
    r"напомнит",
    r"поднимет тему",
    r"фраз",
    r"письм",
    r"решен",
    r"выбор",
    r"импульс",
)

_EMOTION_MARKERS = (
    r"надеж",
    r"может появ",
    r"возможност",
    r"не удивля",
    r"неожидан",
    r"облегч",
    r"проще замет",
    r"ждали",
    r"перестал.*думать",
    r"узна",
    r"снова",
    r"опять",
    r"интерес",
    r"любопыт",
    r"вдохнов",
    r"освобод",
    r"следующ",
    r"шаг",
    r"спокой",
    r"тревог",
    r"радост",
)

_GENERIC_PATTERNS = (
    r"^вас ждут",
    r"^тебя ждут",
    r"^вас ждёт",
    r"^ожидаются",
    r"^довер(ь|я)тесь",
    r"^доверься",
    r"^отпустите",
    r"^отпусти",
    r"^не бойтесь",
    r"^не бойся",
    r"^работайте над собой",
    r"^работай над собой",
    r"^вселенная (будет|направ|подскаж|подталк)",
    r"^пришло время отпустить",
    r"^большие перемены\.?$",
    r"^перемены ждут",
    r"^сегодня важно быть",
    r"^день про ",
    r"^тема дня",
    r"^смысл дня",
    r"^проживать день через",
    r"^ожидается трансформация",
)

_ABSTRACT_PATTERNS = (
    r"трансформац",
    r"внутренн(?:его|ее) состояни",
    r"энерги(?:я|и) и смысл",
    r"ресурс отношений",
    r"тон близости",
    r"пространство и контакт",
    r"формат и устойчив",
    r"смысл и коммуникац",
    r"старый способ.*больше не работает",
    r"ощущение, что",
    r"внутренняя ось",
    r"спокойная ясность",
    r"живой фокус",
)

_ABSURD_SCENE = (
    r"холодильник",
    r"открыть холодильник",
)


def _has_any(text: str, patterns: tuple[str, ...]) -> bool:
    low = text.lower()
    return any(re.search(p, low) for p in patterns)


def auto_tag(text: str) -> dict[str, bool]:
    t = (text or "").strip()
    low = t.lower()
    word_count = len(re.findall(r"[A-Za-zА-Яа-яЁё0-9-]+", t, re.UNICODE))

    has_scene = bool(_has_any(t, _SCENE_MARKERS)) or (
        word_count >= 12
        and bool(re.search(r"(?:можете|можешь|может|если вы|если ты|сегодня)", low))
    )
    has_trigger = bool(_has_any(t, _TRIGGER_MARKERS))
    emotional = bool(_has_any(t, _EMOTION_MARKERS))
    too_generic = bool(_has_any(t, _GENERIC_PATTERNS)) or (
        word_count <= 6 and not has_trigger and not bool(_has_any(t, _SCENE_MARKERS))
    )
    abstract = bool(_has_any(t, _ABSTRACT_PATTERNS)) and not has_trigger

    no_scene = not has_scene or (word_count <= 4 and not has_trigger)

    if _has_any(t, _ABSURD_SCENE):
        has_scene = True
        no_scene = False
        too_generic = True
        emotional = False

    likely_good = bool(
        has_scene
        and has_trigger
        and emotional
        and not too_generic
        and not abstract
        and not _has_any(t, _ABSURD_SCENE)
        and word_count >= 8
    )

    return {
        "no_scene": bool(no_scene),
        "too_generic": bool(too_generic),
        "abstract": bool(abstract),
        "has_scene": bool(has_scene),
        "has_trigger": bool(has_trigger),
        "emotional_hook": bool(emotional),
        "likely_good": likely_good,
    }


def _normalize_phrase(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _is_candidate_phrase(text: str, *, min_chars: int = 18, min_words: int = 3) -> bool:
    t = _normalize_phrase(text)
    if not t or not _CYRILLIC_RE.search(t):
        return False
    if len(t) < min_chars:
        return False
    words = re.findall(r"[A-Za-zА-Яа-яЁё0-9-]+", t, re.UNICODE)
    if len(words) < min_words:
        return False
    # skip obvious code / paths / slugs
    if re.fullmatch(r"[a-z0-9_.-]+", t):
        return False
    if "http://" in t or "https://" in t:
        return False
    return True


def _is_narrative_ru(text: str) -> bool:
    """Stricter filter: human-facing RU copy, not code fragments."""
    t = _normalize_phrase(text)
    if not _is_candidate_phrase(t):
        return False
    if len(t) > 420:
        return False
    if any(m in t for m in _CODE_MARKERS):
        return False
    cyrillic = len(re.findall(r"[А-Яа-яЁё]", t))
    if cyrillic < 8:
        return False
    latin_words = len(re.findall(r"[A-Za-z]{3,}", t))
    if latin_words > 3:
        return False
    if re.search(r"[A-Za-z]{5,}", t) and cyrillic < latin_words * 4:
        return False
    return True


def _accept_phrase(text: str, *, strict: bool = True) -> bool:
    return _is_narrative_ru(text) if strict else _is_candidate_phrase(text)


def _walk_json_strings(obj: Any, path: str = "") -> Iterator[tuple[str, str]]:
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            child = f"{path}.{k}" if path else str(k)
            yield from _walk_json_strings(v, child)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk_json_strings(v, f"{path}[{i}]")


def _extract_from_json_file(path: Path, source: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return out
    for field_path, text in _walk_json_strings(data):
        if _accept_phrase(text):
            out.append(
                {
                    "text": _normalize_phrase(text),
                    "source": source,
                    "source_path": str(path.relative_to(_REPO_ROOT)),
                    "source_field": field_path,
                }
            )
    return out


def _unquote_string(raw: str) -> str:
    q = raw[0]
    if raw[-1] != q or len(raw) < 2:
        return raw
    inner = raw[1:-1]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return inner.replace("\\n", "\n").replace('\\"', '"').replace("\\'", "'").replace("\\\\", "\\")


def _extract_from_text_file(path: Path, source: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return out

    if path.suffix in (".ts", ".tsx"):
        for match in _TS_RU_PROP_RE.finditer(raw):
            text = _unquote_string('"' + match.group(1) + '"')
            if _accept_phrase(text):
                out.append(
                    {
                        "text": _normalize_phrase(text),
                        "source": source,
                        "source_path": str(path.relative_to(_REPO_ROOT)),
                        "source_field": None,
                    }
                )
        return out

    for match in _RU_STRING_RE.finditer(raw):
        text = _unquote_string(match.group(0))
        if _accept_phrase(text):
            out.append(
                {
                    "text": _normalize_phrase(text),
                    "source": source,
                    "source_path": str(path.relative_to(_REPO_ROOT)),
                    "source_field": None,
                }
            )
    for match in _RU_STRING_SINGLE_RE.finditer(raw):
        text = _unquote_string(match.group(0))
        if _accept_phrase(text):
            out.append(
                {
                    "text": _normalize_phrase(text),
                    "source": source,
                    "source_path": str(path.relative_to(_REPO_ROOT)),
                    "source_field": None,
                }
            )
    return out


def _extract_fallbacks() -> list[dict[str, Any]]:
    from todayflow_backend.services.today_contract_fallbacks_v1 import DOMAIN_FALLBACKS_V1

    out: list[dict[str, Any]] = []
    for domain, slots in DOMAIN_FALLBACKS_V1.items():
        for slot, text in slots.items():
            if _accept_phrase(text):
                out.append(
                    {
                        "text": _normalize_phrase(text),
                        "source": "fallback.contract_v1",
                        "source_path": "backend/src/todayflow_backend/services/today_contract_fallbacks_v1.py",
                        "source_field": f"{domain}.{slot}",
                    }
                )
    return out


def _extract_assembled_contracts() -> list[dict[str, Any]]:
    from todayflow_backend.services.today_contract_assembler_v1 import assemble_today_contract_v1

    fixtures_dir = _REPO_ROOT / "backend" / "tests" / "fixtures" / "today_contract_v1"
    out: list[dict[str, Any]] = []
    if not fixtures_dir.is_dir():
        return out
    for path in sorted(fixtures_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        try:
            contract = assemble_today_contract_v1(
                spheres=data.get("spheres"),
                narrative=data.get("narrative"),
                morning_ritual=data.get("morning_ritual"),
                fusion=data.get("fusion"),
                fallback_context=data.get("fallback_context"),
            )
        except Exception:
            continue
        for field_path, text in _walk_json_strings(contract):
            if _accept_phrase(text):
                out.append(
                    {
                        "text": _normalize_phrase(text),
                        "source": "contract_fixture.assembled",
                        "source_path": str(path.relative_to(_REPO_ROOT)),
                        "source_field": field_path,
                    }
                )
    return out


def _extract_narrative_fallbacks() -> list[dict[str, Any]]:
    from todayflow_backend.services.today_narrative import _fallback_guide

    out: list[dict[str, Any]] = []
    payload = _fallback_guide(foundation={"spine": {}}, fusion={"scores": {"energy": 55, "focus": 50}}, core_profile=None, locale="ru")
    for field_path, text in _walk_json_strings(payload):
        if isinstance(text, str) and _accept_phrase(text):
            out.append(
                {
                    "text": _normalize_phrase(text),
                    "source": "fallback.narrative_guide",
                    "source_path": "backend/src/todayflow_backend/services/today_narrative.py",
                    "source_field": field_path,
                }
            )
    return out


def _extract_dead_patterns() -> list[dict[str, Any]]:
    from todayflow_backend.core.text_quality import DEAD_PATTERNS

    out: list[dict[str, Any]] = []
    for p in DEAD_PATTERNS:
        if _CYRILLIC_RE.search(p):
            out.append(
                {
                    "text": p,
                    "source": "reference.dead_patterns",
                    "source_path": "backend/src/todayflow_backend/core/text_quality.py",
                    "source_field": "DEAD_PATTERNS",
                }
            )
    return out


def _extract_banned_narrative() -> list[dict[str, Any]]:
    from todayflow_backend.services.today_narrative import _RU_NARRATIVE_BANNED_SUBSTRINGS

    out: list[dict[str, Any]] = []
    for p in _RU_NARRATIVE_BANNED_SUBSTRINGS:
        out.append(
            {
                "text": p,
                "source": "reference.banned_substrings",
                "source_path": "backend/src/todayflow_backend/services/today_narrative.py",
                "source_field": "_RU_NARRATIVE_BANNED_SUBSTRINGS",
            }
        )
    return out


def _generation_log_payload_blobs(rec: dict[str, Any]) -> list[tuple[str, Any]]:
    """Collect JSON/text blobs from a generation_log export row."""
    pairs: list[tuple[str, Any]] = []
    for key in (
        "output_payload",
        "normalized_response",
        "input_payload",
        "response_payload",
        "payload",
        "final_text",
        "narrative",
        "guide",
        "output_text",
        "response_text",
    ):
        blob = rec.get(key)
        if blob is not None:
            pairs.append((key, blob))
    raw = rec.get("raw_response")
    if isinstance(raw, str) and _CYRILLIC_RE.search(raw):
        pairs.append(("raw_response", raw))
    return pairs


def _extract_generation_logs(logs_dir: Path | None) -> list[dict[str, Any]]:
    if logs_dir is None:
        return []
    logs_dir = logs_dir.resolve()
    if not logs_dir.is_dir():
        return []
    repo_root = _REPO_ROOT.resolve()
    out: list[dict[str, Any]] = []
    for path in sorted(logs_dir.rglob("*")):
        if path.suffix not in (".json", ".jsonl"):
            continue
        try:
            if path.suffix == ".jsonl":
                lines = path.read_text(encoding="utf-8").splitlines()
                records = [json.loads(line) for line in lines if line.strip()]
            else:
                data = json.loads(path.read_text(encoding="utf-8"))
                records = data if isinstance(data, list) else [data]
        except (json.JSONDecodeError, OSError):
            continue
        for rec in records:
            if not isinstance(rec, dict):
                continue
            log_id = rec.get("id")
            log_module = rec.get("module")
            log_surface = rec.get("surface")
            for key, blob in _generation_log_payload_blobs(rec):
                if isinstance(blob, str):
                    if _accept_phrase(blob):
                        out.append(
                            {
                                "text": _normalize_phrase(blob),
                                "source": "generation_log",
                                "source_path": str(path.resolve().relative_to(repo_root)),
                                "source_field": key,
                                "generation_log_id": log_id,
                                "module": log_module,
                                "surface": log_surface,
                            }
                        )
                    continue
                for field_path, text in _walk_json_strings(blob):
                    if _accept_phrase(text):
                        out.append(
                            {
                                "text": _normalize_phrase(text),
                                "source": "generation_log",
                                "source_path": str(path.resolve().relative_to(repo_root)),
                                "source_field": f"{key}.{field_path}",
                                "generation_log_id": log_id,
                                "module": log_module,
                                "surface": log_surface,
                            }
                        )
    return out


def _dedupe_entries(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for item in raw:
        key = item["text"].lower()
        if key not in seen:
            seen[key] = {**item, "source_occurrences": 1, "sources": [item["source"]]}
        else:
            seen[key]["source_occurrences"] += 1
            if item["source"] not in seen[key]["sources"]:
                seen[key]["sources"].append(item["source"])
    return list(seen.values())


def build_corpus(*, logs_dir: Path | None = None) -> dict[str, Any]:
    raw: list[dict[str, Any]] = []

    raw.extend(_extract_fallbacks())
    raw.extend(_extract_assembled_contracts())
    raw.extend(_extract_narrative_fallbacks())
    raw.extend(_extract_dead_patterns())
    raw.extend(_extract_banned_narrative())
    raw.extend(_extract_generation_logs(logs_dir))

    json_paths = [
        (_REPO_ROOT / "backend" / "tests" / "fixtures" / "today_contract_v1", "contract_fixture.raw"),
        (_REPO_ROOT / "CONTENT" / "forecasts" / "daily_forecasts.json", "content.daily_forecasts"),
    ]
    for base, source in json_paths:
        if base.is_file():
            raw.extend(_extract_from_json_file(base, source))
        elif base.is_dir():
            for p in sorted(base.glob("*.json")):
                raw.extend(_extract_from_json_file(p, source))

    py_test_globs = [
        _REPO_ROOT / "backend" / "tests" / "test_today_narrative_contract.py",
        _REPO_ROOT / "backend" / "tests" / "test_today_contract_text_quality_v1.py",
        _REPO_ROOT / "backend" / "tests" / "test_today_contract_assembler_v1.py",
        _REPO_ROOT / "backend" / "tests" / "test_text_quality.py",
        _REPO_ROOT / "backend" / "tests" / "test_ritual_cue_sanitize.py",
    ]
    for p in py_test_globs:
        if p.is_file():
            raw.extend(_extract_from_text_file(p, "test.expected"))

    ts_paths = [
        _REPO_ROOT / "frontend" / "src" / "components" / "today" / "todayRitualCopy.ts",
        _REPO_ROOT / "frontend" / "src" / "lib" / "todayUnifiedSynthesis.ts",
        _REPO_ROOT / "frontend" / "src" / "lib" / "todayNarrativeFromContract.ts",
    ]
    for p in ts_paths:
        if p.is_file():
            raw.extend(_extract_from_text_file(p, "hardcoded.ru"))

    deduped = _dedupe_entries(raw)

    entries: list[dict[str, Any]] = []
    for i, item in enumerate(sorted(deduped, key=lambda x: x["text"]), start=1):
        tags = auto_tag(item["text"])
        entries.append(
            {
                "id": f"corp-{i:04d}",
                "text": item["text"],
                "source": item["source"],
                "sources": item.get("sources", [item["source"]]),
                "source_occurrences": item.get("source_occurrences", 1),
                "source_path": item.get("source_path"),
                "source_field": item.get("source_field"),
                "tags": tags,
                "manual_review": None,
                "score": None,
            }
        )

    tag_counts = Counter()
    for e in entries:
        for k, v in e["tags"].items():
            if v:
                tag_counts[k] += 1

    source_counts = Counter(e["source"] for e in entries)

    return {
        "schema_version": "0.1",
        "dataset_id": "TODAY_LANGUAGE_CORPUS_V0",
        "phase": "TL-0B",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "canon_ref": "docs/TODAY_LANGUAGE_V1.md",
        "calibration_ref": "docs/TODAY_LANGUAGE_CALIBRATION_V0.md",
        "generation_logs_note": (
            "No generation_logs in repo by default. Export from DB "
            "(generation_logs.output_payload) and pass --logs-dir to merge."
        ),
        "stats": {
            "total_unique_phrases": len(entries),
            "tag_counts": dict(tag_counts),
            "source_counts": dict(source_counts),
            "likely_good": tag_counts["likely_good"],
            "likely_bad_no_scene_or_generic": sum(
                1 for e in entries if e["tags"]["no_scene"] or e["tags"]["too_generic"]
            ),
            "manual_review_queue": {
                "worst_20": "lowest heuristic: no_scene + too_generic + abstract",
                "best_20": "likely_good=true",
                "borderline_20": "has_scene xor emotional_hook; not likely_good",
            },
        },
        "entries": entries,
    }


def _review_slices(corpus: dict[str, Any]) -> dict[str, list[str]]:
    entries = corpus["entries"]

    def bad_score(e: dict[str, Any]) -> int:
        t = e.get("tags") or {}
        return (
            int(bool(t.get("no_scene"))) * 3
            + int(bool(t.get("too_generic"))) * 3
            + int(bool(t.get("abstract"))) * 2
            - int(bool(t.get("likely_good"))) * 5
        )

    def good_score(e: dict[str, Any]) -> int:
        t = e.get("tags") or {}
        return (
            int(bool(t.get("likely_good"))) * 5
            + int(bool(t.get("has_scene")))
            + int(bool(t.get("has_trigger")))
            + int(bool(t.get("emotional_hook")))
        )

    def border_score(e: dict[str, Any]) -> int:
        t = e.get("tags") or {}
        if t.get("likely_good"):
            return -999
        s = int(bool(t.get("has_scene"))) + int(bool(t.get("emotional_hook")))
        return s if 1 <= s <= 2 else -999

    worst = sorted(entries, key=bad_score, reverse=True)[:20]
    best = sorted(entries, key=good_score, reverse=True)[:20]
    border = sorted([e for e in entries if border_score(e) >= 0], key=border_score, reverse=True)[:20]

    return {
        "worst_20_ids": [e["id"] for e in worst],
        "best_20_ids": [e["id"] for e in best],
        "borderline_20_ids": [e["id"] for e in border],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="TL-0A/TL-0B Today language corpus extractor")
    parser.add_argument(
        "--out",
        type=Path,
        default=_REPO_ROOT / "docs" / "datasets" / "TODAY_LANGUAGE_CORPUS_V0.json",
    )
    parser.add_argument("--logs-dir", type=Path, default=None, help="Optional exported generation_logs JSON/JSONL")
    args = parser.parse_args()

    corpus = build_corpus(logs_dir=args.logs_dir)
    corpus["review_slices"] = _review_slices(corpus)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)

    stats = corpus["stats"]
    gen_log = stats.get("source_counts", {}).get("generation_log", 0)
    print(f"Wrote {stats['total_unique_phrases']} unique phrases → {args.out}", file=sys.stderr)
    print(f"  generation_log phrases: {gen_log}", file=sys.stderr)
    print(f"  likely_good: {stats['likely_good']}", file=sys.stderr)
    print(f"  no_scene|too_generic: {stats['likely_bad_no_scene_or_generic']}", file=sys.stderr)
    print(f"  sources: {stats['source_counts']}", file=sys.stderr)


if __name__ == "__main__":
    main()
