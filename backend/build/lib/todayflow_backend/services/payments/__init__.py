"""Payment helpers (Stripe or mock, depending on settings)."""

from __future__ import annotations

try:
    import stripe
except ImportError:  # pragma: no cover - stripe optional for mock mode
    stripe = None

from todayflow_backend.core.config import settings
from todayflow_backend.db import models as db_models
from todayflow_backend.db.session import SessionLocal

USE_STRIPE = settings.payments_mode.lower() == "stripe"

if USE_STRIPE:
    if stripe is None:
        raise RuntimeError("Stripe SDK not installed but payments_mode=stripe")
    stripe.api_key = settings.stripe_secret_key


class PaymentError(Exception):
    pass


def create_checkout_session(user_id: int) -> dict:
    if not USE_STRIPE:
        _mark_user_paid(user_id)
        return {
            "session_id": f"mock_session_{user_id}",
            "checkout_url": "http://localhost:3000/dashboard?mock_paid=1",
            "mode": "mock",
        }

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "price": settings.stripe_price_id,
                    "quantity": 1,
                }
            ],
            metadata={"user_id": user_id},
            success_url="http://localhost:3000/reports/full?success=1",
            cancel_url="http://localhost:3000/dashboard?cancelled=1",
        )
        return {"session_id": session.id, "checkout_url": session.url}
    except stripe.error.StripeError as exc:
        raise PaymentError(str(exc)) from exc


def handle_webhook(payload: bytes, signature: str) -> None:
    if not USE_STRIPE:
        return

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=settings.stripe_webhook_secret,
        )
    except stripe.error.SignatureVerificationError as exc:
        raise PaymentError(f"Invalid signature: {exc}") from exc

    if event["type"] == "checkout.session.completed":
        data = event["data"]["object"]
        user_id = data.get("metadata", {}).get("user_id")
        if user_id:
            _mark_user_paid(int(user_id))


def _mark_user_paid(user_id: int) -> None:
    session = SessionLocal()
    try:
        user = session.query(db_models.User).filter_by(id=user_id).one_or_none()
        if user:
            user.is_paid = True
            session.add(user)
            session.commit()
    finally:
        session.close()
