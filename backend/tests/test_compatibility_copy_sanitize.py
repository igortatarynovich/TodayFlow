
def test_sanitize_compatibility_copy_strips_hashtag_garbage() -> None:
    from todayflow_backend.services.compatibility_llm import sanitize_compatibility_copy

    raw = "Нормальный текст\n#Numerology\n#SelfWorth\nЕщё строка"
    out = sanitize_compatibility_copy(raw, locale="ru")
    assert "#Numerology" not in out
    assert "#SelfWorth" not in out
    assert "Нормальный текст" in out
    assert "Ещё строка" in out
