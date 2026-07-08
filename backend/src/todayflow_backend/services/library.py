"""My Library — сохранённые прогнозы и расчёты (Web Canon v1 / Вертикаль 2)."""

from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy.exc import IntegrityError

from todayflow_backend.db import models as db_models
from todayflow_backend.db.session import SessionLocal


def get_saved_forecasts(user_id: int) -> List[str]:
    """Список forecast_id, сохранённых пользователем."""
    session = SessionLocal()
    try:
        rows = (
            session.query(db_models.SavedForecast)
            .filter(db_models.SavedForecast.user_id == user_id)
            .order_by(db_models.SavedForecast.created_at.desc())
            .all()
        )
        return [r.forecast_id for r in rows]
    finally:
        session.close()


def toggle_saved_forecast(user_id: int, forecast_id: str) -> bool:
    """Toggle: добавить в избранное или убрать. True = добавлен, False = убран."""
    session = SessionLocal()
    try:
        existing = (
            session.query(db_models.SavedForecast)
            .filter(
                db_models.SavedForecast.user_id == user_id,
                db_models.SavedForecast.forecast_id == forecast_id,
            )
            .first()
        )
        if existing:
            session.delete(existing)
            session.commit()
            return False
        rec = db_models.SavedForecast(user_id=user_id, forecast_id=forecast_id)
        session.add(rec)
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False
    finally:
        session.close()


def get_saved_calculations(user_id: int) -> List[Dict[str, Any]]:
    """Список сохранённых расчётов: [{ calc_type, key, payload }, ...]."""
    session = SessionLocal()
    try:
        rows = (
            session.query(db_models.SavedCalculation)
            .filter(db_models.SavedCalculation.user_id == user_id)
            .order_by(db_models.SavedCalculation.created_at.desc())
            .all()
        )
        return [
            {"calc_type": r.calc_type, "key": r.key, "payload": r.payload or {}}
            for r in rows
        ]
    finally:
        session.close()


def toggle_saved_calculation(
    user_id: int,
    calc_type: str,
    key: str,
    payload: Dict[str, Any],
) -> bool:
    """Toggle: добавить расчёт в избранное или убрать. True = добавлен, False = убран."""
    session = SessionLocal()
    try:
        existing = (
            session.query(db_models.SavedCalculation)
            .filter(
                db_models.SavedCalculation.user_id == user_id,
                db_models.SavedCalculation.key == key,
            )
            .first()
        )
        if existing:
            session.delete(existing)
            session.commit()
            return False
        rec = db_models.SavedCalculation(
            user_id=user_id,
            calc_type=calc_type,
            key=key,
            payload=payload,
        )
        session.add(rec)
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False
    finally:
        session.close()
