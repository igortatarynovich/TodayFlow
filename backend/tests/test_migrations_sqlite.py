"""SQLite: много-стейтмент .sql миграции и idempotent apply."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, text

from todayflow_backend.db.models import Base
from todayflow_backend.db.migrations import apply_migrations


@pytest.fixture
def memory_engine():
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=eng)
    yield eng
    eng.dispose()


def test_apply_migrations_sqlite_includes_calendar_tables(memory_engine):
    apply_migrations(memory_engine)
    with memory_engine.connect() as conn:
        for name in ("calendar_events", "calendar_notes", "menstrual_cycles"):
            n = conn.execute(
                text(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=:n"
                ),
                {"n": name},
            ).scalar_one()
            assert int(n) == 1, f"missing table {name}"


def test_apply_migrations_sqlite_idempotent(memory_engine):
    apply_migrations(memory_engine)
    apply_migrations(memory_engine)
