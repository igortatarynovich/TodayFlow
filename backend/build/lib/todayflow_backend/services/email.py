"""Email service helpers."""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from todayflow_backend.core.config import settings

logger = logging.getLogger(__name__)


def _build_password_reset_message(to_email: str, reset_url: str) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = "TodayFlow password reset"
    msg["From"] = settings.email_from
    msg["To"] = to_email
    msg.set_content(
        "We received a request to reset your password.\n\n"
        f"Use this link to set a new password:\n{reset_url}\n\n"
        "If you did not request this, you can ignore this message."
    )
    return msg


def send_password_reset_email(to_email: str, reset_url: str) -> bool:
    """Send password reset email using SMTP configuration."""
    if not settings.smtp_host:
        logger.warning("SMTP host is not configured; password reset email was not sent")
        return False

    msg = _build_password_reset_message(to_email, reset_url)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_username and settings.smtp_password:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(msg)
        return True
    except Exception as exc:
        logger.exception("Failed to send password reset email: %s", exc)
        return False
