"""Birth timezone resolve — fail closed, no civil-as-UT invention."""

from todayflow_backend.services.birth_timezone_resolve_v1 import (
    profile_needs_timezone,
    resolve_birth_timezone,
    timezone_for_city_name,
)


def test_minsk_and_kyiv_city_names():
    assert timezone_for_city_name("Minsk") == "Europe/Minsk"
    assert timezone_for_city_name("Kyiv") == "Europe/Kyiv"


def test_resolve_from_location_name_cyrillic():
    out = resolve_birth_timezone(location_name="Минск", latitude=53.9045, longitude=27.5615)
    assert out["need_tz"] is False
    assert out["timezone_name"] == "Europe/Minsk"


def test_resolve_from_coords_nearest():
    out = resolve_birth_timezone(latitude=50.45, longitude=30.52)
    assert out["timezone_name"] == "Europe/Kyiv"
    assert out["need_tz"] is False


def test_unresolved_needs_tz():
    out = resolve_birth_timezone(location_name="Somewhere Unknown Atoll", latitude=1.0, longitude=1.0)
    # May still nearest-match a city within 120km; force far ocean
    out = resolve_birth_timezone(latitude=-40.0, longitude=-120.0)
    assert out["need_tz"] is True
    assert out["timezone_name"] is None


def test_profile_needs_timezone_flag():
    assert profile_needs_timezone(
        time_unknown=False,
        birth_time="12:12:00",
        timezone_name=None,
        timezone_offset_minutes=None,
    )
    assert not profile_needs_timezone(
        time_unknown=False,
        birth_time="12:12:00",
        timezone_name="Europe/Minsk",
        timezone_offset_minutes=None,
    )
    assert not profile_needs_timezone(
        time_unknown=True,
        birth_time=None,
        timezone_name=None,
        timezone_offset_minutes=None,
    )
