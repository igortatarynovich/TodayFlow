"""Legacy natal cache may store positions as a dict keyed by body name."""

from todayflow_backend.services.astro import ChartResponse, coerce_chart_positions


def test_coerce_dict_positions_to_list_rows():
    rows = coerce_chart_positions(
        {
            "Sun": {"sign": "taurus", "longitude": 40.0, "retrograde": None},
            "Moon": {"sign": "cancer", "longitude": 100.0},
        }
    )
    assert len(rows) == 2
    assert rows[0]["body"] == "Sun"
    assert rows[0]["sign"] == "taurus"
    assert rows[1]["body"] == "Moon"


def test_chart_response_accepts_legacy_dict_positions():
    chart = ChartResponse(
        mode="natal",
        positions={"Sun": {"sign": "taurus", "degree": 12}},
        houses={"1": {"sign": "leo"}},
        metadata=None,
    )
    assert chart.positions[0]["body"] == "Sun"
    assert chart.houses == {"1": {"sign": "leo"}}
    assert chart.metadata == {}
