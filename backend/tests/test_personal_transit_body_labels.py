"""Body-id case normalization for transit→natal lookups."""

from todayflow_backend.services.personal_transits import index_chart_positions_by_label


def test_index_chart_positions_maps_lowercase_body_to_labels():
    positions = [
        {"body": "sun", "longitude": 10.0, "sign": "Aries"},
        {"body": "north_node", "longitude": 20.0, "sign": "Taurus"},
        {"body": "rising", "longitude": 30.0, "sign": "Gemini"},
    ]
    idx = index_chart_positions_by_label(positions)
    assert idx["Sun"]["longitude"] == 10.0
    assert idx["North Node"]["longitude"] == 20.0
    assert idx["Ascendant"]["longitude"] == 30.0
