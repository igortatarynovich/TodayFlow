"""Утилита для загрузки JSON файлов из CONTENT директории."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


def get_content_path() -> Path:
    """Получить путь к CONTENT директории."""
    # Проверяем переменную окружения (для Docker)
    env_content_dir = os.getenv("CONTENT_DIR")
    if env_content_dir:
        return Path(env_content_dir)
    
    # От backend/src/todayflow_backend/core/content_loader.py
    # до CONTENT/
    current_file = Path(__file__).resolve()
    backend_dir = current_file.parent.parent.parent.parent.parent
    content_dir = backend_dir / "CONTENT"
    
    # Если не найдено, пробуем /CONTENT (для Docker)
    if not content_dir.exists():
        docker_content = Path("/CONTENT")
        if docker_content.exists():
            return docker_content
    
    return content_dir


def load_json_file(relative_path: str) -> Dict[str, Any]:
    """Загрузить JSON файл из CONTENT директории.
    
    Args:
        relative_path: Относительный путь от CONTENT/, например "lexicon/lexicon.json"
    
    Returns:
        Словарь с данными из JSON файла
    """
    content_dir = get_content_path()
    file_path = content_dir / relative_path
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_lexicon() -> Dict[str, Any]:
    """Загрузить Lexicon."""
    return load_json_file("lexicon/lexicon.json")


def load_practices() -> Dict[str, Any]:
    """Загрузить Practices."""
    return load_json_file("practices/practices.json")


def load_asceticisms() -> Dict[str, Any]:
    """Загрузить Asceticisms."""
    return load_json_file("practices/asceticisms.json")


def load_affirmations() -> Dict[str, Any]:
    """Загрузить Affirmations."""
    return load_json_file("practices/affirmations.json")


def get_lexicon_phrase(phrase_id: str) -> Optional[Dict[str, Any]]:
    """Получить фразу из Lexicon по ID."""
    lexicon = load_lexicon()
    phrases = lexicon.get('phrases', [])
    for phrase in phrases:
        if phrase.get('id') == phrase_id:
            return phrase
    return None
