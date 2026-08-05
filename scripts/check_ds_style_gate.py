#!/usr/bin/env python3
"""
Design-system style gate for frontend CSS modules (DS Task 1 + 2.6 + 2.7).

Canon: docs/TODAYFLOW_FOUNDATION_UI.md §5 / §6 / §7 / §15 / §17c —
product CSS must use Ds* primitives + --tf-* / --day-* tokens; no ad-hoc
CTA/card classes; no raw hex / rgba / color-mix paints; no private font-size
or max-width column scales.

Modes:
  (default)     Fail on violations not listed in the baseline file.
  --warn-only   Report all violations as warnings; always exit 0.
  --write-baseline  Rewrite the baseline from the current tree; exit 0.

Whitelist (same or previous line):
  /* ds-gate: allow — <ticket-or-reason> */
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_ROOT / "frontend" / "src"
DEFAULT_BASELINE = REPO_ROOT / "scripts" / "ds_style_gate_baseline.json"

# product CSS modules only; design-system owns primitives/tokens
SCAN_GLOB = "**/*.module.css"
EXEMPT_DIR_PARTS = ("design-system",)

HEX_RE = re.compile(
    r"(?<![\w-])#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b"
)
# Selectors that look like ad-hoc CTA / card shells (prefix match per Task 1)
ADHOC_CLASS_RE = re.compile(
    r"(?<![\w-])\.("
    r"(?:cta|card|actionButton|primaryCta|secondaryCta|submitButton)\w*"
    r")\b"
)
# New custom-property *definitions* for banned namespaces (not var(--orbit-*) reads)
LEGACY_DEF_RE = re.compile(
    r"(--(?:orbit|todayflow|tdp|product)-[a-zA-Z0-9-]+)\s*:"
)
ALLOW_RE = re.compile(r"ds-gate:\s*allow\b", re.IGNORECASE)

# Task 2.6 — hardcoded channel paints (gate was blind to these)
RGBA_RE = re.compile(r"\b(?:rgba?|hsla?)\s*\(", re.IGNORECASE)
COLOR_MIX_RE = re.compile(r"\bcolor-mix\s*\(", re.IGNORECASE)

# Task 2.6b — private type scales
FONT_SIZE_PROP_RE = re.compile(r"font-size\s*:\s*([^;}+]+)", re.IGNORECASE)
FONT_SIZE_OK_RE = re.compile(
    r"^(?:"
    r"var\(\s*--tf-type-[a-z0-9-]+"
    r"|var\(\s*--tf-ds-[a-z0-9-]+"
    r"|inherit|unset|initial|revert|revert-layer"
    r"|0|0px|0rem|0em"
    r"|smaller|larger|xx-small|x-small|small|medium|large|x-large|xx-large|xxx-large"
    r")",
    re.IGNORECASE,
)

# Task 2.7 — column width literals
MAX_WIDTH_PROP_RE = re.compile(r"max-width\s*:\s*([^;}+]+)", re.IGNORECASE)
MAX_WIDTH_OK_RE = re.compile(
    r"^(?:"
    r"var\(\s*--tf-shell-(?:max|readable|gutter|gap)"
    r"|var\(\s*--tf-ds-(?:page-max|mobile-max|main-max(?:-wide)?)"
    r"|var\(\s*--tf-hero-[a-z0-9-]+"
    r"|var\(\s*--pe-max"  # profile editorial alias → shell-max
    r"|100%|none|0|0px|0rem|min-content|max-content|fit-content|inherit|unset|initial"
    r"|min\s*\("
    r")",
    re.IGNORECASE,
)
# @media (max-width: …) is a breakpoint, not a content column
MEDIA_MAX_WIDTH_RE = re.compile(r"@media[^{]*max-width", re.IGNORECASE)

# Selectors we never flag even without allow comment (structural BEM from DS consumers
# that are not inventing a parallel button/card system). Kept empty — baseline covers legacy.
ALWAYS_ALLOW_CLASSES: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Violation:
    rule: str
    path: str  # posix relative to repo root
    line: int
    detail: str

    @property
    def key(self) -> str:
        # Stable identity for baseline: path + rule + detail (not line — lines drift)
        return f"{self.path}|{self.rule}|{self.detail}"


def rel_posix(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def is_exempt(path: Path) -> bool:
    parts = set(path.parts)
    return any(p in parts for p in EXEMPT_DIR_PARTS)


def line_allowed(lines: list[str], idx: int) -> bool:
    cur = lines[idx]
    if ALLOW_RE.search(cur):
        return True
    if idx > 0 and ALLOW_RE.search(lines[idx - 1]):
        return True
    return False


def normalize_css_value(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip().rstrip(";").strip())


def scan_file(path: Path) -> list[Violation]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    rel = rel_posix(path)
    out: list[Violation] = []

    for i, line in enumerate(lines):
        if line_allowed(lines, i):
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("/*") and "*/" in stripped and stripped.endswith("*/"):
            if stripped.startswith("/*") and stripped.endswith("*/"):
                continue

        # Breakpoint lines are not content-column debt
        if MEDIA_MAX_WIDTH_RE.search(line):
            # Still scan hex/rgba/font on the same line if present, but skip max-width rule
            pass
        else:
            for m in MAX_WIDTH_PROP_RE.finditer(line):
                value = normalize_css_value(m.group(1))
                if MAX_WIDTH_OK_RE.match(value):
                    continue
                # Ignore pure breakpoint-looking values only when on @media — already skipped
                out.append(
                    Violation(
                        rule="max-width-literal",
                        path=rel,
                        line=i + 1,
                        detail=value[:80],
                    )
                )

        for m in HEX_RE.finditer(line):
            out.append(
                Violation(
                    rule="hex-literal",
                    path=rel,
                    line=i + 1,
                    detail=m.group(0).lower(),
                )
            )

        for m in RGBA_RE.finditer(line):
            # Capture a short snippet for stable baseline identity
            snippet = normalize_css_value(line[m.start() : m.start() + 48])
            out.append(
                Violation(
                    rule="rgba-literal",
                    path=rel,
                    line=i + 1,
                    detail=snippet[:80],
                )
            )

        for m in COLOR_MIX_RE.finditer(line):
            snippet = normalize_css_value(line[m.start() : m.start() + 48])
            out.append(
                Violation(
                    rule="color-mix-literal",
                    path=rel,
                    line=i + 1,
                    detail=snippet[:80],
                )
            )

        for m in FONT_SIZE_PROP_RE.finditer(line):
            value = normalize_css_value(m.group(1))
            if FONT_SIZE_OK_RE.match(value):
                continue
            out.append(
                Violation(
                    rule="font-size-literal",
                    path=rel,
                    line=i + 1,
                    detail=value[:80],
                )
            )

        for m in ADHOC_CLASS_RE.finditer(line):
            cls = m.group(1)
            if cls in ALWAYS_ALLOW_CLASSES:
                continue
            before = line[: m.start()]
            if re.search(r'["\']', before[max(0, len(before) - 2) :]):
                continue
            out.append(
                Violation(
                    rule="adhoc-class",
                    path=rel,
                    line=i + 1,
                    detail=f".{cls}",
                )
            )

        for m in LEGACY_DEF_RE.finditer(line):
            out.append(
                Violation(
                    rule="legacy-token-def",
                    path=rel,
                    line=i + 1,
                    detail=m.group(1),
                )
            )

    # Dedupe identical keys on same line noise
    seen: set[tuple[str, int, str]] = set()
    unique: list[Violation] = []
    for v in out:
        k = (v.key, v.line, v.detail)
        if k in seen:
            continue
        seen.add(k)
        unique.append(v)
    return unique


def iter_module_css(root: Path) -> list[Path]:
    files = sorted(root.glob(SCAN_GLOB))
    return [p for p in files if p.is_file() and not is_exempt(p)]


def load_baseline(path: Path) -> set[str]:
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    keys = data.get("keys", data if isinstance(data, list) else [])
    return set(keys)


def write_baseline(path: Path, violations: list[Violation]) -> None:
    keys = sorted({v.key for v in violations})
    by_rule: dict[str, int] = {}
    for v in violations:
        by_rule[v.rule] = by_rule.get(v.rule, 0) + 1
    payload = {
        "version": 2,
        "description": (
            "DS style gate baseline — hex/adhoc/legacy + rgba/color-mix + font-size + "
            "max-width debt. New keys fail CI; listed keys warn only. Shrink as "
            "Task 2.6 / 2.6b / 2.7 migrations land."
        ),
        "generated_by": "scripts/check_ds_style_gate.py --write-baseline",
        "counts": {
            "keys": len(keys),
            "occurrences": len(violations),
            "by_rule": by_rule,
        },
        "keys": keys,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def format_violation(v: Violation, *, level: str) -> str:
    return f"{level}: {v.path}:{v.line}: [{v.rule}] {v.detail}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="Scan root (default: frontend/src)",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=DEFAULT_BASELINE,
        help="Baseline JSON path",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Report all violations as warnings; exit 0",
    )
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help="Rewrite baseline from current tree; exit 0",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print errors + summary (suppress baselined warnings)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON summary on stdout",
    )
    args = parser.parse_args(argv)

    root = args.root if args.root.is_absolute() else REPO_ROOT / args.root
    files = iter_module_css(root)
    all_v: list[Violation] = []
    for f in files:
        all_v.extend(scan_file(f))

    if args.write_baseline:
        write_baseline(args.baseline, all_v)
        print(
            f"Wrote baseline {args.baseline.relative_to(REPO_ROOT)} "
            f"({len({v.key for v in all_v})} keys, {len(all_v)} occurrences, {len(files)} files)"
        )
        return 0

    baseline = load_baseline(args.baseline)
    errors: list[Violation] = []
    warnings: list[Violation] = []

    for v in all_v:
        if args.warn_only or v.key in baseline:
            warnings.append(v)
        else:
            errors.append(v)

    if args.json:
        print(
            json.dumps(
                {
                    "files_scanned": len(files),
                    "errors": [asdict(v) for v in errors],
                    "warnings": [asdict(v) for v in warnings],
                    "baseline_keys": len(baseline),
                },
                indent=2,
            )
        )
    else:
        if not args.quiet:
            for v in warnings:
                print(format_violation(v, level="warning"))
        for v in errors:
            print(format_violation(v, level="error"))
        print(
            f"\nds-style-gate: scanned {len(files)} module.css · "
            f"{len(errors)} new error(s) · {len(warnings)} baselined warning(s) · "
            f"baseline={args.baseline.relative_to(REPO_ROOT) if args.baseline.exists() else 'missing'}"
        )
        if errors:
            print(
                "New design-system gate violations. Use DsButton/DsCard/DsTypography + --tf-*/--day-* "
                "/ --tf-type-* / --tf-shell-* or add `/* ds-gate: allow — <ticket> */` with justification."
            )

    if args.warn_only:
        return 0
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
