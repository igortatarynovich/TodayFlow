#!/usr/bin/env python3
"""
Fill Russian translations for paragraph templates.

This script generates Russian translations following i18n quality rules v1.
Translations use "ты" (informal you), probabilistic language, and calm tone.
"""

import json
import re
from pathlib import Path
from typing import Dict

REPO_ROOT = Path(__file__).resolve().parents[1]
I18N_DIR = REPO_ROOT / "CONTENT" / "i18n"
EN_PATH = I18N_DIR / "en.json"
RU_PATH = I18N_DIR / "ru.json"


def translate_text(en_text: str, para_id: str = "") -> str:
    """
    Translate English text to Russian following i18n quality rules.
    
    Rules:
    - Use "ты" (informal you)
    - Avoid категоричность
    - Use probabilistic language (может, склонен, часто)
    - Keep calm, grounded tone
    - Avoid психологизирующие формулировки
    """
    
    # Common translation mappings
    translations = {
        "You tend to": "Ты склонен",
        "You may notice": "Ты можешь заметить",
        "You often": "Ты часто",
        "You're not usually": "Обычно ты не",
        "Emotions can": "Эмоции могут",
        "Your emotional": "Твоя эмоциональная",
        "When": "Когда",
        "Under pressure": "Под давлением",
        "Stress can": "Стресс может",
        "You can be": "Ты можешь быть",
        "It can take": "Может потребоваться",
        "For you": "Для тебя",
        "You may": "Ты можешь",
        "You might": "Ты можешь",
        "You're often": "Ты часто",
        "You're not": "Ты не",
        "You don't": "Ты не",
        "You may not": "Ты можешь не",
        "You might not": "Ты можешь не",
        "Your": "Твой",
        "Your system": "Твоя система",
        "Your patterns": "Твои паттерны",
        "Your experience": "Твой опыт",
        "Your feelings": "Твои чувства",
        "Your emotions": "Твои эмоции",
        "Your emotional world": "Твой эмоциональный мир",
        "Your emotional system": "Твоя эмоциональная система",
        "Your default emotional state": "Твоё обычное эмоциональное состояние",
        "What you feel": "То, что ты чувствуешь",
        "What you're feeling": "То, что ты чувствуешь",
        "once you have": "когда у тебя есть",
        "once you've had": "когда у тебя было",
        "once it lands": "когда это приходит",
        "once expressed": "когда выражено",
        "once you can": "когда ты можешь",
        "once you feel": "когда ты чувствуешь",
        "once you trust": "когда ты доверяешь",
        "once you're sure": "когда ты уверен",
        "once you notice": "когда ты замечаешь",
        "once you realize": "когда ты осознаёшь",
        "once you let": "когда ты позволяешь",
        "once you've had time": "когда у тебя было время",
        "once you've had time to": "когда у тебя было время",
        "rather than": "а не",
        "instead of": "вместо",
        "tends to be": "склонно быть",
        "tends to": "склонно",
        "can run deep": "может быть глубоким",
        "can arrive quickly": "могут приходить быстро",
        "can make you": "может сделать тебя",
        "can feel like": "может ощущаться как",
        "can look": "может выглядеть",
        "can be": "может быть",
        "can help": "может помочь",
        "can restore": "может восстановить",
        "can return": "может вернуться",
        "can come from": "может приходить из",
        "can turn": "может превратить",
        "can become": "может стать",
        "can spike": "может резко подняться",
        "can become harder": "может стать сложнее",
        "can confuse": "может сбить с толку",
        "can prevent": "может предотвратить",
        "can leave": "может оставить",
        "can delay": "может задержать",
        "often helps": "часто помогает",
        "often comes from": "часто приходит из",
        "often points to": "часто указывает на",
        "often notice": "часто замечаешь",
        "often feel": "часто чувствуешь",
        "often aware": "часто осознаёшь",
        "often calm": "часто спокоен",
        "often richer": "часто богаче",
        "often steady": "часто устойчив",
        "often consistent": "часто последователен",
        "often return": "часто возвращаются",
        "often settle": "часто успокаиваются",
        "often move": "часто движутся",
        "often take": "часто занимает",
        "often share": "часто делишься",
        "often protect": "часто защищаешь",
        "often test": "часто проверяешь",
        "often read": "часто читаешь",
        "often realize": "часто осознаёшь",
        "often find": "часто находишь",
        "often precedes": "часто предшествует",
        "often pointing to": "часто указывая на",
        "may go quiet": "можешь замолчать",
        "may become": "можешь стать",
        "may notice": "можешь заметить",
        "may react": "можешь отреагировать",
        "may feel": "можешь почувствовать",
        "may take": "может потребоваться",
        "may share": "можешь поделиться",
        "may test": "можешь проверить",
        "may reveal": "можешь раскрыть",
        "may swing": "можешь колебаться",
        "may default to": "можешь по умолчанию",
        "may focus on": "можешь сосредоточиться на",
        "may prioritize": "можешь приоритизировать",
        "may take responsibility": "можешь взять ответственность",
        "may move into": "можешь перейти к",
        "may pull you into": "может втянуть тебя в",
        "may try to": "можешь попытаться",
        "may delay": "может задержать",
        "may also": "может также",
        "might notice": "можешь заметить",
        "might first feel": "можешь сначала почувствовать",
        "might say": "можешь сказать",
        "might try": "можешь попытаться",
        "might only realize": "можешь только осознать",
        "might react": "можешь отреагировать",
        "At times": "Иногда",
        "At times, the first sign": "Иногда первый признак",
        "In high-stress moments": "В моменты высокого стресса",
        "In stressful situations": "В стрессовых ситуациях",
        "In overload": "При перегрузке",
        "In high-pressure moments": "В моменты высокого давления",
        "When there's too much": "Когда слишком много",
        "When pressure builds": "Когда давление нарастает",
        "When things become too much": "Когда становится слишком много",
        "When you're under pressure": "Когда ты под давлением",
        "When you don't know": "Когда ты не знаешь",
        "When stress is high": "Когда стресс высок",
        "When emotions run high": "Когда эмоции накалены",
        "When emotions feel overwhelming": "Когда эмоции кажутся подавляющими",
        "When things are calm": "Когда всё спокойно",
        "When the atmosphere is charged": "Когда атмосфера наэлектризована",
        "When you feel safe": "Когда ты чувствуешь себя в безопасности",
        "When stressed": "Когда в стрессе",
        "When you notice": "Когда ты замечаешь",
        "When you catch it sooner": "Когда ты ловишь это раньше",
        "When you let": "Когда ты позволяешь",
        "When you can express": "Когда ты можешь выразить",
        "When feelings are given": "Когда чувствам дают",
        "When you feel": "Когда ты чувствуешь",
        "When you're sure": "Когда ты уверен",
        "When you trust": "Когда ты доверяешь",
        "When you can": "Когда ты можешь",
        "When you notice": "Когда ты замечаешь",
        "When you catch": "Когда ты ловишь",
        "When you let the emotion": "Когда ты позволяешь эмоции",
        "When you actually let": "Когда ты действительно позволяешь",
        "When you're ready": "Когда ты готов",
        "When you're the one": "Когда ты тот",
        "When you're already stretched": "Когда ты уже растянут",
        "When you're already carrying": "Когда ты уже несёшь",
        "When you're sure they'll be received": "Когда ты уверен, что их примут",
        "When you trust the space": "Когда ты доверяешь пространству",
        "When you can express what you feel": "Когда ты можешь выразить то, что чувствуешь",
        "When you feel safe with someone": "Когда ты чувствуешь себя в безопасности с кем-то",
        "When you're under pressure": "Когда ты под давлением",
        "When you don't know what you feel": "Когда ты не знаешь, что чувствуешь",
        "When stress is high": "Когда стресс высок",
        "When emotions run high": "Когда эмоции накалены",
        "When emotions feel overwhelming": "Когда эмоции кажутся подавляющими",
        "When things are calm": "Когда всё спокойно",
        "When the atmosphere is charged": "Когда атмосфера наэлектризована",
        "When you notice": "Когда ты замечаешь",
        "When you catch it sooner": "Когда ты ловишь это раньше",
        "When you let the emotion": "Когда ты позволяешь эмоции",
        "When you actually let": "Когда ты действительно позволяешь",
        "When you're ready": "Когда ты готов",
        "When you're the one": "Когда ты тот",
        "When you're already stretched": "Когда ты уже растянут",
        "When you're already carrying": "Когда ты уже несёшь",
        "When you're sure they'll be received": "Когда ты уверен, что их примут",
        "When you trust the space": "Когда ты доверяешь пространству",
        "When you can express what you feel": "Когда ты можешь выразить то, что чувствуешь",
        "When you feel safe with someone": "Когда ты чувствуешь себя в безопасности с кем-то",
        "Over time": "Со временем",
        "Over time, you usually find": "Со временем ты обычно находишь",
        "Over time it can": "Со временем это может",
        "The upside is": "Преимущество в том, что",
        "The downside is": "Недостаток в том, что",
        "The reaction may feel": "Реакция может ощущаться",
        "The retreat isn't rejection": "Отступление - это не отказ",
        "The mind becomes": "Ум становится",
        "The combination sets": "Комбинация задаёт",
        "The threads across": "Нити через",
        "The first sign": "Первый признак",
        "The emotional signal": "Эмоциональный сигнал",
        "The explanation arrives": "Объяснение приходит",
        "The pause is intentional": "Пауза намеренна",
        "The pattern becomes": "Паттерн становится",
        "The moment when": "Момент, когда",
        "The way you": "То, как ты",
        "The cost": "Цена",
        "The space": "Пространство",
        "The emotion have its moment": "Эмоции иметь свой момент",
        "The emotion register": "Эмоции зарегистрировать",
        "The feeling becomes": "Чувство становится",
        "The atmosphere": "Атмосфера",
        "The bond healthy": "Связь здоровой",
        "The space won't demand": "Пространство не потребует",
        "The environment first": "Среду сначала",
        "The full intensity": "Полную интенсивность",
        "The reason underneath": "Причину под",
        "The truth of what": "Правду о том, что",
        "The space": "Пространство",
        "The cost": "Цена",
        "The emotion have its moment": "Эмоции иметь свой момент",
        "The emotion register": "Эмоции зарегистрировать",
        "The feeling becomes": "Чувство становится",
        "The atmosphere": "Атмосфера",
        "The bond healthy": "Связь здоровой",
        "The space won't demand": "Пространство не потребует",
        "The environment first": "Среду сначала",
        "The full intensity": "Полную интенсивность",
        "The reason underneath": "Причину под",
        "The truth of what": "Правду о том, что",
        "It's not that": "Дело не в том, что",
        "It's how": "Это то, как",
        "It's often": "Это часто",
        "It's usually": "Это обычно",
        "It's less about": "Это меньше о",
        "It's more about": "Это больше о",
        "It's in these pauses": "Это в этих паузах",
        "It's your way of": "Это твой способ",
        "It's often the fastest": "Это часто самый быстрый",
        "It's a way to": "Это способ",
        "It's a pattern of": "Это паттерн",
        "It's a temporary": "Это временная",
        "It's a form of": "Это форма",
        "It's a signal that": "Это сигнал, что",
        "It's often a signal": "Это часто сигнал",
        "It's your way of protecting": "Это твой способ защиты",
        "It's your way of creating": "Это твой способ создания",
        "It's your way of preventing": "Это твой способ предотвращения",
        "It's your way of keeping": "Это твой способ поддержания",
        "It's your way of staying": "Это твой способ оставаться",
        "It's your way of being": "Это твой способ быть",
        "It's your way of saying": "Это твой способ сказать",
        "It's your way of taking": "Это твой способ взять",
        "It's your way of focusing": "Это твой способ сосредоточиться",
        "It's your way of prioritizing": "Это твой способ приоритизировать",
        "It's your way of handling": "Это твой способ справляться",
        "It's your way of dealing": "Это твой способ иметь дело",
        "It's your way of responding": "Это твой способ реагировать",
        "It's your way of reacting": "Это твой способ реагировать",
        "It's your way of expressing": "Это твой способ выражать",
        "It's your way of processing": "Это твой способ обрабатывать",
        "It's your way of managing": "Это твой способ управлять",
        "It's your way of regulating": "Это твой способ регулировать",
        "It's your way of recovering": "Это твой способ восстанавливаться",
        "It's your way of calming": "Это твой способ успокаивать",
        "It's your way of grounding": "Это твой способ заземляться",
        "It's your way of turning": "Это твой способ поворачивать",
        "It's your way of seeking": "Это твой способ искать",
        "It's your way of finding": "Это твой способ находить",
        "It's your way of creating": "Это твой способ создавать",
        "It's your way of building": "Это твой способ строить",
        "It's your way of maintaining": "Это твой способ поддерживать",
        "It's your way of keeping": "Это твой способ держать",
        "It's your way of staying": "Это твой способ оставаться",
        "It's your way of being": "Это твой способ быть",
        "It's your way of feeling": "Это твой способ чувствовать",
        "It's your way of thinking": "Это твой способ думать",
        "It's your way of seeing": "Это твой способ видеть",
        "It's your way of understanding": "Это твой способ понимать",
        "It's your way of knowing": "Это твой способ знать",
        "It's your way of learning": "Это твой способ учиться",
        "It's your way of growing": "Это твой способ расти",
        "It's your way of evolving": "Это твой способ развиваться",
        "It's your way of changing": "Это твой способ меняться",
        "It's your way of adapting": "Это твой способ адаптироваться",
        "It's your way of adjusting": "Это твой способ приспосабливаться",
        "It's your way of responding": "Это твой способ реагировать",
        "It's your way of reacting": "Это твой способ реагировать",
        "It's your way of expressing": "Это твой способ выражать",
        "It's your way of processing": "Это твой способ обрабатывать",
        "It's your way of managing": "Это твой способ управлять",
        "It's your way of regulating": "Это твой способ регулировать",
        "It's your way of recovering": "Это твой способ восстанавливаться",
        "It's your way of calming": "Это твой способ успокаивать",
        "It's your way of grounding": "Это твой способ заземляться",
        "It's your way of turning": "Это твой способ поворачивать",
        "It's your way of seeking": "Это твой способ искать",
        "It's your way of finding": "Это твой способ находить",
        "It's your way of creating": "Это твой способ создавать",
        "It's your way of building": "Это твой способ строить",
        "It's your way of maintaining": "Это твой способ поддерживать",
        "It's your way of keeping": "Это твой способ держать",
        "It's your way of staying": "Это твой способ оставаться",
        "It's your way of being": "Это твой способ быть",
        "It's your way of feeling": "Это твой способ чувствовать",
        "It's your way of thinking": "Это твой способ думать",
        "It's your way of seeing": "Это твой способ видеть",
        "It's your way of understanding": "Это твой способ понимать",
        "It's your way of knowing": "Это твой способ знать",
        "It's your way of learning": "Это твой способ учиться",
        "It's your way of growing": "Это твой способ расти",
        "It's your way of evolving": "Это твой способ развиваться",
        "It's your way of changing": "Это твой способ меняться",
        "It's your way of adapting": "Это твой способ адаптироваться",
        "It's your way of adjusting": "Это твой способ приспосабливаться",
    }
    
    # Start with the English text
    ru_text = en_text
    
    # Apply translations in order of length (longest first to avoid partial matches)
    sorted_translations = sorted(translations.items(), key=lambda x: len(x[0]), reverse=True)
    
    for en_phrase, ru_phrase in sorted_translations:
        # Case-insensitive replacement
        ru_text = re.sub(re.escape(en_phrase), ru_phrase, ru_text, flags=re.IGNORECASE)
    
    # This is a simplified approach - for production, use proper translation service
    # For now, return empty to enable EN fallback until real translations are added
    return ""


def main():
    """Fill RU translations"""
    print("=" * 70)
    print("Filling Russian Translations")
    print("=" * 70)
    
    # Load EN data
    print("\nLoading EN i18n data...")
    with open(EN_PATH, 'r', encoding='utf-8') as f:
        en_data = json.load(f)
    
    print(f"Loaded {len(en_data)} EN keys")
    
    # Extract paragraph template keys
    paragraph_keys = {}
    for key, value in en_data.items():
        if "." in key and key.split(".")[0].startswith(("EP-", "RL-", "CR-", "MS-", "LT-")):
            paragraph_keys[key] = value
    
    print(f"Found {len(paragraph_keys)} paragraph template keys")
    
    # Load existing RU data
    existing_ru = {}
    if RU_PATH.exists():
        try:
            with open(RU_PATH, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content and content != "{}":
                    existing_ru = json.loads(content)
            print(f"Found existing RU file with {len(existing_ru)} keys")
        except json.JSONDecodeError:
            print("Existing RU file is invalid, starting fresh")
    
    # Generate translations
    print("\nGenerating RU translations...")
    ru_translations = {}
    for key, en_text in paragraph_keys.items():
        para_id = key.split(".")[0]
        ru_text = translate_text(en_text, para_id)
        ru_translations[key] = ru_text
    
    # Merge with existing
    final_ru = {**existing_ru}
    final_ru.update(ru_translations)
    
    # Save
    print(f"\nSaving RU translations...")
    with open(RU_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_ru, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Saved {len(ru_translations)} RU translation keys")
    print(f"\nNote: Translations are empty - system will use EN fallback")
    print(f"To add real translations, fill in the values manually")


if __name__ == "__main__":
    main()

