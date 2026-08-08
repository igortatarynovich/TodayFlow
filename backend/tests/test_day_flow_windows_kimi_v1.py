"""Unit tests for day_flow_windows_kimi_v1 — no live Nebius."""

from todayflow_backend.services.day_flow_windows_kimi_v1 import (
    COPY_SOURCE_BANK,
    COPY_SOURCE_KIMI,
    fingerprint_for_windows,
    merge_window_copy,
    validate_windows_payload,
)


def test_fingerprint_stable_for_same_windows():
    rows = [
        {"driver_id": "a", "time_local": "2026-08-08T12:33+03:00", "valence": "favorable"},
        {"driver_id": "b", "time_local": "2026-08-08T17:45+03:00", "valence": "favorable"},
    ]
    assert fingerprint_for_windows(rows) == fingerprint_for_windows(list(rows))
    other = [
        {"driver_id": "a", "time_local": "2026-08-08T12:34+03:00", "valence": "favorable"},
        {"driver_id": "b", "time_local": "2026-08-08T17:45+03:00", "valence": "favorable"},
    ]
    assert fingerprint_for_windows(rows) != fingerprint_for_windows(other)


def test_validate_rejects_jargon_and_unknown_ids():
    allowed = {"pt-moon-trine-north_node"}
    ok = validate_windows_payload(
        {
            "schema_version": "day_flow_windows_v1",
            "windows": [
                {
                    "driver_id": "pt-moon-trine-north_node",
                    "title": "Лучше снизить темп",
                    "detail": "Хорошо для спокойных разговоров и разбора дел.",
                },
                {
                    "driver_id": "invented",
                    "title": "Лишнее",
                    "detail": "нет",
                },
            ],
        },
        allowed_ids=allowed,
    )
    assert ok is not None
    assert len(ok) == 1
    assert ok[0]["title"] == "Лучше снизить темп"

    bad = validate_windows_payload(
        {
            "schema_version": "day_flow_windows_v1",
            "windows": [
                {
                    "driver_id": "pt-moon-trine-north_node",
                    "title": "Луна в трине",
                    "detail": "ок",
                }
            ],
        },
        allowed_ids=allowed,
    )
    assert bad is None


def test_merge_prefers_kimi_then_bank():
    glance = [
        {
            "driver_id": "a",
            "time_local": "t1",
            "label_short": "Отдых и пауза",
            "detail": None,
            "valence": "favorable",
            "copy_source": COPY_SOURCE_BANK,
        },
        {
            "driver_id": "b",
            "time_local": "t2",
            "label_short": "Живой контакт",
            "detail": None,
            "valence": "favorable",
            "copy_source": COPY_SOURCE_BANK,
        },
    ]
    merged = merge_window_copy(
        glance,
        {
            "schema_version": "day_flow_windows_v1",
            "windows": [
                {
                    "driver_id": "a",
                    "title": "Настроение ровнее — лучше снизить темп",
                    "detail": "Хорошо для спокойных разговоров.",
                }
            ],
        },
    )
    assert merged[0]["label_short"].startswith("Настроение ровнее")
    assert merged[0]["detail"]
    assert merged[0]["copy_source"] == COPY_SOURCE_KIMI
    assert merged[1]["label_short"] == "Живой контакт"
    assert merged[1]["copy_source"] == COPY_SOURCE_BANK
