"""UMTS §3.6 — daily CUM confidence snapshots for delta_30d learning metric."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from sqlalchemy.orm import Session

from todayflow_backend.db.models import CumConfidenceSnapshot, utc_naive_now

CUM_CONFIDENCE_SNAPSHOT_V0_CONTRACT = "cum_confidence_snapshot_v0"
CUM_CONFIDENCE_HISTORY_V0_CONTRACT = "cum_confidence_history_v0"
DELTA_30D_LOOKBACK_DAYS = 30
DELTA_30D_MAX_BASELINE_GAP_DAYS = 14
DEFAULT_HISTORY_WINDOW_DAYS = 90
MAX_HISTORY_WINDOW_DAYS = 90


def upsert_cum_confidence_snapshot(
    db: Session,
    *,
    user_id: int,
    snapshot_date: date,
    confidence: dict[str, Any],
    commit: bool = False,
) -> CumConfidenceSnapshot:
    """Persist one confidence point per user per day (idempotent upsert)."""
    overall = confidence.get("overall")
    if not isinstance(overall, (int, float)):
        raise ValueError("confidence.overall required for snapshot")

    payload = {
        "contract_version": CUM_CONFIDENCE_SNAPSHOT_V0_CONTRACT,
        "overall": round(float(overall), 3),
        "by_domain": confidence.get("by_domain") if isinstance(confidence.get("by_domain"), dict) else {},
        "meaning_events_28d": int(confidence.get("meaning_events_28d") or 0),
    }

    row = (
        db.query(CumConfidenceSnapshot)
        .filter(
            CumConfidenceSnapshot.user_id == user_id,
            CumConfidenceSnapshot.snapshot_date == snapshot_date,
        )
        .one_or_none()
    )
    if row is None:
        row = CumConfidenceSnapshot(
            user_id=user_id,
            snapshot_date=snapshot_date,
            overall=payload["overall"],
            by_domain=payload["by_domain"],
            meaning_events_28d=payload["meaning_events_28d"],
        )
        db.add(row)
    else:
        row.overall = payload["overall"]
        row.by_domain = payload["by_domain"]
        row.meaning_events_28d = payload["meaning_events_28d"]
        row.updated_at = utc_naive_now()

    if commit:
        db.commit()
        db.refresh(row)
    return row


def find_baseline_snapshot_for_delta_30d(
    db: Session,
    *,
    user_id: int,
    reference_date: date,
    lookback_days: int = DELTA_30D_LOOKBACK_DAYS,
    max_gap_days: int = DELTA_30D_MAX_BASELINE_GAP_DAYS,
) -> CumConfidenceSnapshot | None:
    """Latest snapshot on or before reference_date - lookback_days."""
    target = reference_date - timedelta(days=max(1, lookback_days))
    row = (
        db.query(CumConfidenceSnapshot)
        .filter(
            CumConfidenceSnapshot.user_id == user_id,
            CumConfidenceSnapshot.snapshot_date <= target,
        )
        .order_by(CumConfidenceSnapshot.snapshot_date.desc())
        .first()
    )
    if row is None:
        return None
    gap = (target - row.snapshot_date).days
    if gap > max_gap_days:
        return None
    return row


def compute_delta_30d(current_overall: float, baseline_overall: float) -> float:
    return round(current_overall - baseline_overall, 3)


def apply_confidence_delta_30d(
    db: Session,
    *,
    user_id: int,
    reference_date: date,
    confidence: dict[str, Any],
    commit_snapshot: bool = False,
) -> dict[str, Any]:
    """Upsert today's snapshot and attach delta_30d when baseline exists."""
    upsert_cum_confidence_snapshot(
        db,
        user_id=user_id,
        snapshot_date=reference_date,
        confidence=confidence,
        commit=commit_snapshot,
    )
    baseline = find_baseline_snapshot_for_delta_30d(
        db, user_id=user_id, reference_date=reference_date
    )
    enriched = dict(confidence)
    if baseline is not None and isinstance(enriched.get("overall"), (int, float)):
        enriched["delta_30d"] = compute_delta_30d(float(enriched["overall"]), float(baseline.overall))
    else:
        enriched["delta_30d"] = None
    return enriched


def _snapshot_row_to_point(row: CumConfidenceSnapshot) -> dict[str, Any]:
    by_domain = row.by_domain if isinstance(row.by_domain, dict) else {}
    return {
        "snapshot_date": row.snapshot_date.isoformat(),
        "overall": round(float(row.overall), 3),
        "by_domain": by_domain,
        "meaning_events_28d": int(row.meaning_events_28d or 0),
    }


def build_confidence_history_summary_v0(points: list[dict[str, Any]]) -> dict[str, Any]:
    if not points:
        return {
            "point_count": 0,
            "overall_min": None,
            "overall_max": None,
            "delta_window": None,
        }

    overall_values = [float(p["overall"]) for p in points if isinstance(p.get("overall"), (int, float))]
    summary: dict[str, Any] = {
        "point_count": len(points),
        "overall_min": round(min(overall_values), 3) if overall_values else None,
        "overall_max": round(max(overall_values), 3) if overall_values else None,
        "delta_window": None,
    }
    if len(overall_values) >= 2:
        summary["delta_window"] = round(overall_values[-1] - overall_values[0], 3)
    return summary


def load_cum_confidence_history_v0(
    db: Session,
    *,
    user_id: int,
    reference_date: date,
    window_days: int = DEFAULT_HISTORY_WINDOW_DAYS,
) -> dict[str, Any]:
    """Read-only confidence snapshot series for charts and delta trends (UMTS §3.6)."""
    bounded_window = max(1, min(int(window_days), MAX_HISTORY_WINDOW_DAYS))
    start_date = reference_date - timedelta(days=bounded_window - 1)

    rows = (
        db.query(CumConfidenceSnapshot)
        .filter(
            CumConfidenceSnapshot.user_id == user_id,
            CumConfidenceSnapshot.snapshot_date >= start_date,
            CumConfidenceSnapshot.snapshot_date <= reference_date,
        )
        .order_by(CumConfidenceSnapshot.snapshot_date.asc())
        .all()
    )
    points = [_snapshot_row_to_point(row) for row in rows]
    return {
        "contract_version": CUM_CONFIDENCE_HISTORY_V0_CONTRACT,
        "as_of": reference_date.isoformat(),
        "window_days": bounded_window,
        "start_date": start_date.isoformat(),
        "end_date": reference_date.isoformat(),
        "points": points,
        "summary": build_confidence_history_summary_v0(points),
    }
