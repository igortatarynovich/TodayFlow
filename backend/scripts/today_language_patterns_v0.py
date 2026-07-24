#!/usr/bin/env python3
"""TL-0C.1 / TL-0C.2 — pattern mining on api_live phrases (generation_log only).

Does NOT assign quality scores. Surfaces recurring anti-patterns and strong-pattern
candidates for editorial review before manual 30+30 calibration.

Usage:
  PYTHONPATH=backend/src python backend/scripts/today_language_patterns_v0.py
  PYTHONPATH=backend/src python backend/scripts/today_language_patterns_v0.py \\
    --corpus docs/datasets/TODAY_LANGUAGE_CORPUS_V0.json \\
    --out docs/datasets/TODAY_LANGUAGE_PATTERNS_V0.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = _REPO_ROOT / "backend" / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from today_language_corpus_v0 import auto_tag  # noqa: E402

# --- TL-0C.1 anti-pattern heuristics (hypothesis templates, not gate) ---------------

_ANTI_A_PSEUDO = (
    r"станет понятн",
    r"многое станет",
    r"проясн",
    r"осознан(?:ие|ия)",
    r"возможны.*осознан",
    r"начн[ёе]т проясня",
    r"появится понимание",
    r"день предлагает возможность",
    r"сегодняшний день предлагает",
    r"важно сосредоточиться",
    r"сосредоточиться на том, чтобы",
    r"может потребовать внимания",
    r"лучше понять свои потребност",
)

_ANTI_B_WISDOM = (
    r"^вас ждут",
    r"^тебя ждут",
    r"^довер(ь|я)тесь",
    r"^доверься",
    r"^отпуст(ите|и)",
    r"^отпусти",
    r"^не бойтесь",
    r"^не бойся",
    r"не всё требует",
    r"просто подожд",
    r"сво[ёе] время",
    r"каждая ситуация",
    r"работа(й|йте) над собой",
    r"этот день не требует",
    r"важно быть",
    r"приглашаю.*подвести итоги",
    r"когда мы делимся своими чувствами",
)

_ANTI_D_FAKE = (
    r"неожиданн.*изменит",
    r"^сегодня возможен разговор\.?$",
    r"^сегодня может состояться разговор\.?$",
    r"важный разговор",
    r"откровенный разговор",
    r"сделай шаг к .*разговор",
    r"предлагает возможность сосредоточ",
    r"неожиданный разговор",
    r"случайн.*фраз",
)

_STAKES_MARKERS = (
    r"откладыва",
    r"давно",
    r"боял",
    r"бояла",
    r"опасен",
    r"опасени",
    r"если не",
    r"перестал.*думать",
    r"перестали.*думать",
    r"ждали ответ",
    r"уже решили",
    r"не первую неделю",
    r"снова.*тем",
    r"закрыт",
    r"единственн",
    r"последн",
    r"риск",
    r"на кон",
    r"устали объясня",
    r"месяц назад",
    r"окончательн",
)

_SKIP_PREFIX = re.compile(
    r"^(pattern_hint:|card_|module_|Igor[,:]|Игорь[,:]|«[А-ЯA-Z])",
    re.IGNORECASE,
)

_NOISE_PATTERNS = (
    r"асцендент",
    r"числом пути",
    r"карта собирается",
    r"aquarius",
    r"по расчёту дня \(",
    r"источники в основном согласованы",
)

_OPENING_RE = re.compile(
    r"^(?:сегодня|сегодняшний день|этот день|добрый вечер[^.]*\.|"
    r"приглашаю тебя|смотри(?:те)? на|используй(?:те)?|"
    r"в любви|в работе|в финансах|реально сработает)\s*",
    re.IGNORECASE,
)


def _has_any(text: str, patterns: tuple[str, ...]) -> bool:
    low = text.lower()
    return any(re.search(p, low) for p in patterns)


def _is_narrative_api_live(text: str) -> bool:
    t = (text or "").strip()
    if len(t) < 20 or not re.search(r"[А-Яа-яЁё]", t):
        return False
    if _SKIP_PREFIX.match(t):
        return False
    if t.startswith("pattern_hint:"):
        return False
    if _has_any(t, _NOISE_PATTERNS):
        return False
    return True


def _skeleton(text: str) -> str:
    """Normalize phrase to a recurring template for frequency clustering."""
    s = text.lower().strip()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\d+", "#", s)
    s = re.sub(r"[«»\"']", "", s)
    s = _OPENING_RE.sub("", s)
    s = re.sub(r"\b(igor|игорь|сегодня|сегодняшний день|этот день)\b", "…", s)
    s = re.sub(r"\s+", " ", s).strip(" .…")
    # collapse near-duplicate verb stems
    for stem in (
        "сосредоточ",
        "возможност",
        "разговор",
        "практическ",
        "аналитическ",
        "финансов",
        "партнер",
        "чувств",
        "задач",
    ):
        s = re.sub(rf"{stem}\w*", f"[{stem}]", s)
    if len(s) > 96:
        s = s[:96] + "…"
    return s or text.lower()[:80]


def _classify_anti(text: str, tags: dict[str, bool]) -> list[str]:
    types: list[str] = []
    if _has_any(text, _ANTI_A_PSEUDO):
        types.append("A_pseudo_concreteness")
    if _has_any(text, _ANTI_B_WISDOM):
        types.append("B_universal_wisdom")
    if tags.get("emotional_hook") and (tags.get("no_scene") or not tags.get("has_trigger")):
        types.append("C_emotion_without_scene")
    if _has_any(text, _ANTI_D_FAKE):
        types.append("D_fake_concreteness")
    # Residual weak bucket: heuristic bad without typed pattern
    if not types and (tags.get("no_scene") or tags.get("too_generic") or tags.get("abstract")):
        types.append("Z_untyped_weak")
    return types


def _stakes_score(text: str) -> int:
    return sum(1 for p in _STAKES_MARKERS if re.search(p, text.lower()))


def _strong_score(text: str, tags: dict[str, bool]) -> int:
    score = 0
    if tags.get("has_scene"):
        score += 2
    if tags.get("has_trigger"):
        score += 2
    if tags.get("emotional_hook"):
        score += 2
    if not tags.get("too_generic"):
        score += 1
    if not tags.get("abstract"):
        score += 1
    score += _stakes_score(text) * 3
    if tags.get("likely_good"):
        score += 2
    # Penalize known weak templates that fool TL-0B heuristics
    if _has_any(text, _ANTI_D_FAKE):
        score -= 5
    if _has_any(text, _ANTI_B_WISDOM):
        score -= 4
    if _has_any(text, _ANTI_A_PSEUDO):
        score -= 3
    if re.match(r"^в любви (сделай|постарайся|важно|старайся)", text.lower()):
        score -= 4
    return score


def _why_strong(text: str, tags: dict[str, bool]) -> list[str]:
    reasons: list[str] = []
    if tags.get("has_trigger"):
        reasons.append("trigger_event")
    if tags.get("emotional_hook"):
        reasons.append("emotional_hook")
    if tags.get("has_scene"):
        reasons.append("recognizable_scene")
    if _stakes_score(text) >= 1:
        reasons.append("stakes_hypothesis")
    if re.search(r"ожидан|ждали|перестал.*думать|не первую неделю", text.lower()):
        reasons.append("anticipation_arc")
    if re.search(r"логика говорит|поймать себя|снова.*тем", text.lower()):
        reasons.append("inner_dialogue_or_return")
    return reasons


def _pick_examples(items: list[dict[str, Any]], n: int = 4) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for item in items:
        key = item["text"].lower()[:80]
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "id": item["id"],
                "text": item["text"],
                "surface": item.get("surface"),
                "module": item.get("module"),
            }
        )
        if len(out) >= n:
            break
    return out


def mine_patterns(corpus: dict[str, Any]) -> dict[str, Any]:
    entries = [
        e
        for e in corpus.get("entries", [])
        if "generation_log" in (e.get("sources") or [])
        and _is_narrative_api_live(e.get("text", ""))
    ]

    typed: dict[str, list[dict[str, Any]]] = defaultdict(list)
    skeleton_bad: Counter[str] = Counter()
    skeleton_bad_examples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    strong_candidates: list[dict[str, Any]] = []

    for e in entries:
        text = e["text"]
        tags = e.get("tags") or auto_tag(text)
        anti_types = _classify_anti(text, tags)
        sk = _skeleton(text)

        record = {**e, "tags": tags, "anti_types": anti_types, "skeleton": sk}

        for t in anti_types:
            typed[t].append(record)

        if anti_types or tags.get("no_scene") or tags.get("too_generic"):
            skeleton_bad[sk] += 1
            if len(skeleton_bad_examples[sk]) < 6:
                skeleton_bad_examples[sk].append(record)

        s_score = _strong_score(text, tags)
        if s_score >= 6:
            strong_candidates.append(
                {
                    **record,
                    "strong_score": s_score,
                    "stakes_markers": _stakes_score(text),
                    "why_hypothesis": _why_strong(text, tags),
                }
            )

    anti_labels = {
        "A_pseudo_concreteness": "Псевдоконкретика — сцена вроде есть, человек ничего не видит",
        "B_universal_wisdom": "Универсальная мудрость — подходит любому человеку",
        "C_emotion_without_scene": "Подмена конкретики эмоцией — эмоция есть, сцены нет",
        "D_fake_concreteness": "Фальшивая конкретика — «разговор/сообщение», но всё ещё универсально",
        "Z_untyped_weak": "Слабое без явного шаблона (no_scene / too_generic)",
    }

    anti_pattern_report = []
    for type_id, label in anti_labels.items():
        bucket = typed.get(type_id, [])
        anti_pattern_report.append(
            {
                "type_id": type_id,
                "label": label,
                "count": len(bucket),
                "share_of_api_live": round(len(bucket) / max(len(entries), 1), 4),
                "examples": _pick_examples(bucket, 5),
            }
        )
    anti_pattern_report.sort(key=lambda x: x["count"], reverse=True)

    top_bad_skeletons = []
    for sk, count in skeleton_bad.most_common(20):
        ex = skeleton_bad_examples.get(sk, [])
        top_bad_skeletons.append(
            {
                "skeleton": sk,
                "count": count,
                "anti_types_seen": sorted({t for e in ex for t in e.get("anti_types", [])}),
                "examples": _pick_examples(ex, 3),
            }
        )

    strong_candidates.sort(
        key=lambda x: (x["strong_score"], x["stakes_markers"]),
        reverse=True,
    )
    top_strong = []
    for item in strong_candidates[:20]:
        top_strong.append(
            {
                "id": item["id"],
                "text": item["text"],
                "strong_score": item["strong_score"],
                "stakes_markers": item["stakes_markers"],
                "why_hypothesis": item["why_hypothesis"],
                "tags": item["tags"],
                "surface": item.get("surface"),
                "module": item.get("module"),
            }
        )

    stakes_rich = sorted(
        [e for e in entries if _stakes_score(e["text"]) >= 2],
        key=lambda e: _stakes_score(e["text"]),
        reverse=True,
    )[:20]

    return {
        "schema_version": "0.1",
        "dataset_id": "TODAY_LANGUAGE_PATTERNS_V0",
        "status": "TL-0C.1_0C.2_MACHINE_DRAFT",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "canon_ref": "docs/today-language/TODAY_LANGUAGE_V1.md",
        "calibration_ref": "docs/today-language/TODAY_LANGUAGE_CALIBRATION_V0.md",
        "method": {
            "scope": "generation_log phrases only (api_live)",
            "narrative_filter": "excludes pattern_hint, tarot card lines, bare personalization",
            "not_scores": "anti/strong clusters are heuristics for editorial review, not TL-1 gate",
            "next_step": "TL-0C.1 editorial: validate 10-20 anti-patterns; TL-0C.2: why-it-works notes",
        },
        "stats": {
            "corpus_generation_log_total": sum(
                1
                for e in corpus.get("entries", [])
                if "generation_log" in (e.get("sources") or [])
            ),
            "api_live_narrative_phrases": len(entries),
            "typed_anti_hits": sum(len(v) for v in typed.values()),
            "unique_bad_skeletons": len(skeleton_bad),
            "strong_candidates_ge_6": len(strong_candidates),
            "stakes_ge_2": len([e for e in entries if _stakes_score(e["text"]) >= 2]),
        },
        "tl_0c_1_anti_patterns_by_type": anti_pattern_report,
        "tl_0c_1_top_20_bad_skeletons": top_bad_skeletons,
        "tl_0c_2_top_20_strong_candidates": top_strong,
        "tl_0c_2_stakes_rich_sample": _pick_examples(
            [{**e, "id": e["id"], "stakes": _stakes_score(e["text"])} for e in stakes_rich],
            20,
        ),
        "rule_hypotheses": [
            {
                "rule_id": "RULE_004",
                "status": "CALIBRATION_HYPOTHESIS",
                "name": "Ставка",
                "definition": "В хорошей фразе что-то поставлено на кон — причина, напряжение, интерес.",
                "weak_example": "Сегодня возможен разговор.",
                "strong_example": (
                    "Сегодня может состояться разговор, который вы давно откладывали "
                    "из-за опасения услышать ответ."
                ),
                "evidence_in_corpus": {
                    "phrases_with_stakes_markers_ge_2": len(
                        [e for e in entries if _stakes_score(e["text"]) >= 2]
                    ),
                    "likely_good_with_stakes": len(
                        [
                            e
                            for e in entries
                            if (e.get("tags") or auto_tag(e["text"])).get("likely_good")
                            and _stakes_score(e["text"]) >= 1
                        ]
                    ),
                },
            }
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="TL-0C.1/0C.2 pattern mining (api_live)")
    parser.add_argument(
        "--corpus",
        type=Path,
        default=_REPO_ROOT / "docs" / "datasets" / "TODAY_LANGUAGE_CORPUS_V0.json",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=_REPO_ROOT / "docs" / "datasets" / "TODAY_LANGUAGE_PATTERNS_V0.json",
    )
    args = parser.parse_args()

    corpus = json.loads(args.corpus.read_text(encoding="utf-8"))
    report = mine_patterns(corpus)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    stats = report["stats"]
    print(f"Wrote pattern report → {args.out}", file=sys.stderr)
    print(f"  api_live narrative phrases: {stats['api_live_narrative_phrases']}", file=sys.stderr)
    print("  anti-pattern counts by type:", file=sys.stderr)
    for row in report["tl_0c_1_anti_patterns_by_type"][:5]:
        print(f"    {row['type_id']}: {row['count']}", file=sys.stderr)
    print(f"  strong candidates (score≥6): {stats['strong_candidates_ge_6']}", file=sys.stderr)
    print(f"  stakes-rich (≥2 markers): {stats['stakes_ge_2']}", file=sys.stderr)


if __name__ == "__main__":
    main()
