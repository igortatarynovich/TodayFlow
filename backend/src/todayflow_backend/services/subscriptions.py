"""Stripe subscription management service."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Optional

try:
    import stripe
except ImportError:
    stripe = None

from todayflow_backend.core.config import settings
from todayflow_backend.db import models as db_models
from todayflow_backend.db.models import utc_naive_now
from todayflow_backend.db.session import SessionLocal

logger = logging.getLogger(__name__)

USE_STRIPE = settings.payments_mode.lower() == "stripe"

if USE_STRIPE:
    if stripe is None:
        raise RuntimeError("Stripe SDK not installed but payments_mode=stripe")
    stripe.api_key = settings.stripe_secret_key


SUBSCRIPTION_PLANS = {
    "lite_plus": {
        "name": "Lite Plus",
        "stripe_price_id": settings.stripe_lite_plus_price_id if hasattr(settings, "stripe_lite_plus_price_id") else None,
        "features": ["lite_reports", "weekly_insights"],
    },
    "full_access": {
        "name": "Full Access",
        "stripe_price_id": settings.stripe_full_access_price_id if hasattr(settings, "stripe_full_access_price_id") else None,
        "features": ["full_reports", "lite_reports", "weekly_insights", "tarot_flow", "numerology", "celestial_flow"],
    },
    "tarot_plus": {
        "name": "Tarot Flow Plus",
        "stripe_price_id": settings.stripe_tarot_plus_price_id if hasattr(settings, "stripe_tarot_plus_price_id") else None,
        "features": ["tarot_flow", "tarot_history", "tarot_spreads"],
    },
}


class SubscriptionError(Exception):
    pass


class SubscriptionService:
    def __init__(self):
        self.plans = SUBSCRIPTION_PLANS

    def get_or_create_customer(self, user: db_models.User) -> str:
        """Get or create Stripe customer ID for user."""
        if user.stripe_customer_id:
            return user.stripe_customer_id

        if not USE_STRIPE:
            return f"mock_customer_{user.id}"

        try:
            customer = stripe.Customer.create(email=user.email, metadata={"user_id": user.id})
            session = SessionLocal()
            try:
                user.stripe_customer_id = customer.id
                session.add(user)
                session.commit()
            finally:
                session.close()
            return customer.id
        except stripe.error.StripeError as exc:
            logger.error(f"Failed to create Stripe customer: {exc}")
            raise SubscriptionError(f"Failed to create customer: {exc}") from exc

    def create_subscription(
        self,
        user: db_models.User,
        plan_id: str,
        trial_days: Optional[int] = None,
    ) -> dict:
        """Create a new subscription."""
        if plan_id not in self.plans:
            raise SubscriptionError(f"Unknown plan: {plan_id}")

        plan = self.plans[plan_id]
        if not plan["stripe_price_id"]:
            raise SubscriptionError(f"Plan {plan_id} not configured")

        customer_id = self.get_or_create_customer(user)

        if not USE_STRIPE:
            # Mock subscription
            session = SessionLocal()
            try:
                subscription = db_models.Subscription(
                    user_id=user.id,
                    stripe_subscription_id=f"mock_sub_{user.id}_{plan_id}",
                    stripe_price_id=plan["stripe_price_id"] or "mock_price",
                    plan_id=plan_id,
                    status="active",
                    current_period_start=utc_naive_now(),
                    current_period_end=utc_naive_now() + timedelta(days=30),
                    cancel_at_period_end=False,
                )
                session.add(subscription)
                user.subscription_status = "active"
                session.add(user)
                session.commit()
                return {
                    "subscription_id": subscription.id,
                    "stripe_subscription_id": subscription.stripe_subscription_id,
                    "checkout_url": f"{settings.frontend_app_url.rstrip('/')}/account/subscriptions?mock_subscription=1",
                    "mode": "mock",
                }
            finally:
                session.close()

        try:
            subscription_data = {
                "customer": customer_id,
                "items": [{"price": plan["stripe_price_id"]}],
                "metadata": {"user_id": user.id, "plan_id": plan_id},
            }

            if trial_days:
                subscription_data["trial_period_days"] = trial_days

            subscription = stripe.Subscription.create(**subscription_data)

            # Save to database
            session = SessionLocal()
            try:
                db_subscription = db_models.Subscription(
                    user_id=user.id,
                    stripe_subscription_id=subscription.id,
                    stripe_price_id=plan["stripe_price_id"],
                    plan_id=plan_id,
                    status=subscription.status,
                    current_period_start=datetime.fromtimestamp(subscription.current_period_start),
                    current_period_end=datetime.fromtimestamp(subscription.current_period_end),
                    cancel_at_period_end=subscription.cancel_at_period_end,
                    trial_start=datetime.fromtimestamp(subscription.trial_start) if subscription.trial_start else None,
                    trial_end=datetime.fromtimestamp(subscription.trial_end) if subscription.trial_end else None,
                )
                session.add(db_subscription)
                user.subscription_status = subscription.status
                session.add(user)
                session.commit()
                return {
                    "subscription_id": db_subscription.id,
                    "stripe_subscription_id": subscription.id,
                    "checkout_url": subscription.latest_invoice.payment_intent.client_secret if subscription.latest_invoice else None,
                }
            finally:
                session.close()

        except stripe.error.StripeError as exc:
            logger.error(f"Failed to create subscription: {exc}")
            raise SubscriptionError(f"Failed to create subscription: {exc}") from exc

    def create_checkout_session(
        self,
        user: db_models.User,
        plan_id: str,
        success_url: str,
        cancel_url: str,
        promo_code: str | None = None,
    ) -> dict:
        """Create Stripe Checkout session for subscription."""
        if plan_id not in self.plans:
            raise SubscriptionError(f"Unknown plan: {plan_id}")

        plan = self.plans[plan_id]
        if not plan["stripe_price_id"]:
            raise SubscriptionError(f"Plan {plan_id} not configured")

        customer_id = self.get_or_create_customer(user)

        if not USE_STRIPE:
            return {
                "session_id": f"mock_session_{user.id}_{plan_id}",
                "checkout_url": f"{settings.frontend_app_url.rstrip('/')}/account/subscriptions?mock_subscription=1",
                "mode": "mock",
            }

        try:
            # Если есть промокод, создаем или получаем Stripe coupon
            discounts = []
            if promo_code:
                try:
                    # Ищем промокод в базе
                    from todayflow_backend.db.session import SessionLocal
                    from todayflow_backend.db import models as db_models
                    db_session = SessionLocal()
                    try:
                        promo = db_session.query(db_models.PromoCode).filter_by(
                            code=promo_code.upper().strip(),
                            is_active=True
                        ).first()
                        is_valid, error_msg = promo.is_valid(user_id=user.id) if promo else (False, "Промокод не найден")
                        if promo and is_valid:
                            # Создаем или получаем Stripe coupon
                            # Для простоты используем код промокода как coupon ID
                            try:
                                coupon = stripe.Coupon.retrieve(promo.code)
                            except stripe.error.InvalidRequestError:
                                # Создаем новый coupon в Stripe
                                coupon_params = {
                                    "id": promo.code,
                                    "name": promo.description or promo.code,
                                }
                                if promo.discount_type == "percentage":
                                    coupon_params["percent_off"] = promo.discount_value
                                else:
                                    coupon_params["amount_off"] = int(promo.discount_value)
                                    coupon_params["currency"] = "usd"
                                
                                if promo.max_uses:
                                    coupon_params["max_redemptions"] = promo.max_uses
                                
                                coupon = stripe.Coupon.create(**coupon_params)
                            
                            discounts = [{"coupon": coupon.id}]
                    finally:
                        db_session.close()
                except Exception as e:
                    logger.warning(f"Failed to apply promo code {promo_code}: {e}")
                    # Продолжаем без промокода
            
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                mode="subscription",
                line_items=[{"price": plan["stripe_price_id"], "quantity": 1}],
                discounts=discounts if discounts else None,
                metadata={"user_id": user.id, "plan_id": plan_id, "promo_code": promo_code or ""},
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return {"session_id": session.id, "checkout_url": session.url}
        except stripe.error.StripeError as exc:
            logger.error(f"Failed to create checkout session: {exc}")
            raise SubscriptionError(f"Failed to create checkout session: {exc}") from exc

    def cancel_subscription(self, user: db_models.User, subscription_id: Optional[int] = None) -> dict:
        """Cancel user's subscription."""
        session = SessionLocal()
        try:
            if subscription_id:
                subscription = session.query(db_models.Subscription).filter_by(id=subscription_id, user_id=user.id).first()
            else:
                subscription = session.query(db_models.Subscription).filter_by(user_id=user.id, status="active").first()

            if not subscription:
                raise SubscriptionError("No active subscription found")

            if not USE_STRIPE:
                subscription.status = "canceled"
                subscription.cancel_at_period_end = True
                user.subscription_status = "canceled"
                session.add(subscription)
                session.add(user)
                session.commit()
                return {"status": "canceled", "cancel_at_period_end": True}

            try:
                stripe_sub = stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True,
                )
                subscription.cancel_at_period_end = True
                subscription.status = stripe_sub.status
                user.subscription_status = stripe_sub.status
                session.add(subscription)
                session.add(user)
                session.commit()
                return {"status": stripe_sub.status, "cancel_at_period_end": True}
            except stripe.error.StripeError as exc:
                logger.error(f"Failed to cancel subscription: {exc}")
                raise SubscriptionError(f"Failed to cancel subscription: {exc}") from exc
        finally:
            session.close()

    def get_user_subscriptions(self, user: db_models.User) -> list[db_models.Subscription]:
        """Get all subscriptions for user."""
        session = SessionLocal()
        try:
            return session.query(db_models.Subscription).filter_by(user_id=user.id).all()
        finally:
            session.close()

    def handle_webhook(self, event: dict) -> None:
        """Handle Stripe webhook events for subscriptions."""
        if not USE_STRIPE:
            return

        event_type = event["type"]
        session = SessionLocal()

        try:
            if event_type == "checkout.session.completed":
                data = event["data"]["object"]
                if data.get("mode") == "subscription":
                    subscription_id = data.get("subscription")
                    if subscription_id:
                        self._sync_subscription(subscription_id, session)

            elif event_type == "customer.subscription.updated":
                subscription_id = event["data"]["object"]["id"]
                self._sync_subscription(subscription_id, session)

            elif event_type == "customer.subscription.deleted":
                subscription_id = event["data"]["object"]["id"]
                subscription = session.query(db_models.Subscription).filter_by(stripe_subscription_id=subscription_id).first()
                if subscription:
                    subscription.status = "canceled"
                    subscription.user.subscription_status = "canceled"
                    session.add(subscription)
                    session.add(subscription.user)
                    session.commit()

            elif event_type == "invoice.paid":
                invoice = event["data"]["object"]
                subscription_id = invoice.get("subscription")
                if subscription_id:
                    self._record_invoice(subscription_id, invoice, session)

        finally:
            session.close()

    def _sync_subscription(self, stripe_subscription_id: str, session: SessionLocal) -> None:
        """Sync subscription from Stripe to database."""
        try:
            stripe_sub = stripe.Subscription.retrieve(stripe_subscription_id)
            subscription = session.query(db_models.Subscription).filter_by(stripe_subscription_id=stripe_subscription_id).first()

            if subscription:
                subscription.status = stripe_sub.status
                subscription.current_period_start = datetime.fromtimestamp(stripe_sub.current_period_start)
                subscription.current_period_end = datetime.fromtimestamp(stripe_sub.current_period_end)
                subscription.cancel_at_period_end = stripe_sub.cancel_at_period_end
                subscription.updated_at = utc_naive_now()
                subscription.user.subscription_status = stripe_sub.status
                session.add(subscription)
                session.add(subscription.user)
            else:
                # Create new subscription record
                user_id = stripe_sub.metadata.get("user_id")
                if user_id:
                    user = session.query(db_models.User).filter_by(id=int(user_id)).first()
                    if user:
                        subscription = db_models.Subscription(
                            user_id=user.id,
                            stripe_subscription_id=stripe_sub.id,
                            stripe_price_id=stripe_sub.items.data[0].price.id,
                            plan_id=stripe_sub.metadata.get("plan_id", "unknown"),
                            status=stripe_sub.status,
                            current_period_start=datetime.fromtimestamp(stripe_sub.current_period_start),
                            current_period_end=datetime.fromtimestamp(stripe_sub.current_period_end),
                            cancel_at_period_end=stripe_sub.cancel_at_period_end,
                            trial_start=datetime.fromtimestamp(stripe_sub.trial_start) if stripe_sub.trial_start else None,
                            trial_end=datetime.fromtimestamp(stripe_sub.trial_end) if stripe_sub.trial_end else None,
                        )
                        session.add(subscription)
                        user.subscription_status = stripe_sub.status
                        session.add(user)
            session.commit()
        except stripe.error.StripeError as exc:
            logger.error(f"Failed to sync subscription: {exc}")
            session.rollback()

    def _record_invoice(self, stripe_subscription_id: str, invoice: dict, session: SessionLocal) -> None:
        """Record invoice payment in subscription history."""
        subscription = session.query(db_models.Subscription).filter_by(stripe_subscription_id=stripe_subscription_id).first()
        if not subscription:
            return

        history = db_models.SubscriptionHistory(
            subscription_id=subscription.id,
            stripe_invoice_id=invoice.get("id"),
            stripe_payment_intent_id=invoice.get("payment_intent"),
            amount=invoice.get("amount_paid", 0),
            currency=invoice.get("currency", "usd"),
            status="paid",
            period_start=datetime.fromtimestamp(invoice.get("period_start", 0)),
            period_end=datetime.fromtimestamp(invoice.get("period_end", 0)),
        )
        session.add(history)
        session.commit()


def get_subscription_service() -> SubscriptionService:
    return SubscriptionService()

