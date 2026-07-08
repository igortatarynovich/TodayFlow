#!/usr/bin/env python3
"""
Simple helper to fetch due Tarot reminders and mark them as sent.

This is a placeholder for a cron/worker job. Replace the `send_notification`
function with integration to email, push, or SMS services.
"""

from __future__ import annotations

from todayflow_backend.services.tarot import TarotService


def send_notification(user_id: int, timezone: str, hour: int, minute: int) -> None:
    """Placeholder notification action."""
    print(f"[TarotReminder] user={user_id} tz={timezone} time={hour:02d}:{minute:02d}")


def main() -> None:
    service = TarotService()
    due = service.list_due_reminders(limit=100)
    if not due:
        print("No reminders due.")
        return
    for setting in due:
        send_notification(setting.user_id, setting.timezone, setting.hour, setting.minute)
        service.record_reminder_sent(setting.user_id)


if __name__ == "__main__":
    main()
