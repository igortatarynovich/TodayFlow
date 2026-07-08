"""fusion_scores: согласованность bulk-расчёта с по-дневным."""

from __future__ import annotations

from datetime import date, timedelta

from todayflow_backend.services.fusion_scores import (
    compute_fusion_scores_for_date,
    compute_fusion_scores_map_for_dates,
)


def test_compute_fusion_scores_map_matches_single_day_queries(db_session):
    user_id = 1
    # Используем только даты без данных — оба пути дают одинаковый базовый вектор 50/50/50.
    d0 = date(2026, 3, 1)
    d1 = d0 + timedelta(days=1)
    single0 = compute_fusion_scores_for_date(db_session, user_id, d0)
    single1 = compute_fusion_scores_for_date(db_session, user_id, d1)
    m = compute_fusion_scores_map_for_dates(db_session, user_id, [d0, d1, d0])
    assert m[d0] == single0
    assert m[d1] == single1
