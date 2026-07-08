#!/usr/bin/env python3
"""Smoke-test Gemini на продакшн-промптах TodayFlow (DayMeaning forecast).

Usage:
  export GEMINI_API_KEY=your-key
  cd backend && python scripts/test_gemini_text.py

  # другая модель
  python scripts/test_gemini_text.py --model gemini-2.5-flash

  # переключить весь backend на Gemini (не только этот скрипт):
  # LLM_PROVIDER=gemini
  # GEMINI_API_KEY=...
  # GEMINI_MODEL=gemini-2.0-flash
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT / "src"))

from todayflow_backend.core.ai_client import (  # noqa: E402
    SYSTEM_PROMPT_DAY_MEANING,
    _build_meaning_prompt,
    _is_valid_forecast_blocks,
    _parse_llm_json,
)
from todayflow_backend.core.config import settings  # noqa: E402
from todayflow_backend.core.llm_openai_compatible import (  # noqa: E402
    chat_completion_plain,
    get_gemini_compatible_client,
    is_gemini_configured,
)


SAMPLE_DAY_MEANING = {
    "date": "2026-07-05",
    "interpretation_direction": "сфокусироваться и не распыляться",
    "focus_area": "work",
    "intensity": "medium",
    "astro_state": {
        "tensions": [
            {"description": "Меркурий в напряжении к Марсу — разговоры могут быть резче обычного"},
            {"description": "Луна проходит через дом дел — эмоции завязаны на задачи и сроки"},
        ],
        "resources": [
            {"description": "Солнце в гармонии с Юпитером — проще видеть главный приоритет"},
        ],
    },
    "numerology_context": {
        "personal_day": 5,
        "personal_year": 1,
        "day_number_title": "День перемен и гибкости",
    },
    "archetype": {
        "name": "Колесница",
        "orientation": "upright",
        "keywords": ["движение", "направление", "контроль темпа"],
    },
}

SAMPLE_INTERPRETATION_FOCUS = {
    "primary_theme": "управляемый темп",
    "tone": "прямой, без суеты",
}

SAMPLE_LEXICON = {
    "theme": [{"text": "Сегодня лучше держать один курс, чем переключаться между десятью задачами."}],
    "notice": [
        {"text": "Утром заметишь, что мелкие просьбы отвлекают от главного."},
        {"text": "В переписке помогает короткий ответ вместо длинного объяснения."},
    ],
}

SAMPLE_USER_CONTEXT = {
    "natal_chart": {
        "sun_sign": "Дева",
        "moon_sign": "Рак",
        "rising_sign": "Стрелец",
    },
    "needs": "work",
}


def _format_blocks(blocks: dict) -> str:
    lines = [
        f"Theme:\n  {blocks.get('theme', '')}",
        "",
        "Notice:",
    ]
    for item in blocks.get("notice") or []:
        lines.append(f"  • {item}")
    lines.extend(["", "Scene:"])
    for item in blocks.get("scene") or []:
        lines.append(f"  • {item}")
    lines.extend(["", f"Micro action:\n  {blocks.get('micro_action', '')}"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Gemini text generation for TodayFlow")
    parser.add_argument("--model", default=settings.gemini_model, help="Gemini model id")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=4096)
    args = parser.parse_args()

    if not is_gemini_configured():
        print("GEMINI_API_KEY не задан.", file=sys.stderr)
        print("Получить ключ: https://aistudio.google.com/apikey", file=sys.stderr)
        print("Затем: export GEMINI_API_KEY=... && python scripts/test_gemini_text.py", file=sys.stderr)
        return 1

    client = get_gemini_compatible_client()
    if client is None:
        print("Не удалось создать Gemini-клиент (проверьте openai SDK).", file=sys.stderr)
        return 1

    user_prompt = _build_meaning_prompt(
        SAMPLE_DAY_MEANING,
        SAMPLE_INTERPRETATION_FOCUS,
        SAMPLE_LEXICON,
        SAMPLE_USER_CONTEXT,
        "ru",
    )

    print("=" * 72)
    print(f"Gemini text test — model: {args.model}")
    print("=" * 72)
    print("\n--- User prompt (sample DayMeaning) ---\n")
    print(user_prompt)
    print("\n--- Calling Gemini ---\n")

    started = perf_counter()
    raw = chat_completion_plain(
        client,
        model=args.model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_DAY_MEANING},
            {"role": "user", "content": user_prompt},
        ],
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )
    elapsed_ms = int((perf_counter() - started) * 1000)

    if not raw:
        print("Пустой ответ от Gemini.", file=sys.stderr)
        return 1

    print("--- Raw response ---\n")
    print(raw)
    print(f"\n--- Parsed ({elapsed_ms} ms) ---\n")

    parsed = _parse_llm_json(raw)
    if not parsed:
        print("Не удалось распарсить JSON из ответа.", file=sys.stderr)
        return 1

    valid = _is_valid_forecast_blocks(parsed)
    print(_format_blocks(parsed))
    print(f"\nSemantic validation: {'OK' if valid else 'FAILED (would fallback in prod)'}")
    print("\nJSON:")
    print(json.dumps(parsed, ensure_ascii=False, indent=2))
    return 0 if valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
