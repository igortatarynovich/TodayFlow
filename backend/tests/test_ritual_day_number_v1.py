from datetime import date

from todayflow_backend.services.day_sources.adapters.numerology import (
    personal_day_number,
    personal_month_number,
    personal_year_number,
    ritual_day_number,
    universal_day_number,
)


def test_ritual_without_birth_is_universal():
    target = date(2026, 8, 15)
    ritual = ritual_day_number(target=target, birth_date=None)
    assert ritual["kind"] == "universal_day"
    assert ritual["value"] == universal_day_number(target)


def test_ritual_with_birth_is_personal_not_universal():
    target = date(2026, 8, 15)
    birth = date(1990, 3, 15)
    ritual = ritual_day_number(target=target, birth_date=birth)
    py = personal_year_number(birth, target.year)
    pm = personal_month_number(py, target.month)
    pd = personal_day_number(pm, target.day)
    assert ritual["kind"] == "personal_day"
    assert ritual["value"] == pd
    assert ritual["universal_day"] == universal_day_number(target)
    assert ritual["value"] != ritual["universal_day"] or pd == universal_day_number(target)
