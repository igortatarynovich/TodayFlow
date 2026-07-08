"""Subscription management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from todayflow_backend.api.auth import require_user
from todayflow_backend.i18n import request_locale, translate
from todayflow_backend.services.subscriptions import SubscriptionService, SubscriptionError, get_subscription_service

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


class CreateSubscriptionPayload(BaseModel):
    plan_id: str
    trial_days: int | None = None
    promo_code: str | None = None


class CancelSubscriptionPayload(BaseModel):
    subscription_id: int | None = None


@router.get("/plans")
async def get_subscription_plans(request: Request) -> dict:
    """Get available subscription plans."""
    service = get_subscription_service()
    return {
        "plans": {
            plan_id: {
                "name": plan["name"],
                "features": plan["features"],
            }
            for plan_id, plan in service.plans.items()
        }
    }


@router.post("/create-checkout")
async def create_subscription_checkout(
    request: Request,
    payload: CreateSubscriptionPayload,
    user=Depends(require_user),
    service: SubscriptionService = Depends(get_subscription_service),
) -> dict:
    """Create Stripe Checkout session for subscription."""
    locale = request_locale(request)
    try:
        success_url = f"{request.base_url}account/subscriptions?success=1"
        cancel_url = f"{request.base_url}account/subscriptions?cancelled=1"
        return service.create_checkout_session(user, payload.plan_id, success_url, cancel_url, promo_code=payload.promo_code)
    except SubscriptionError as exc:
        message = translate("subscriptions.errors.createFailed", locale=locale, default="Failed to create subscription")
        raise HTTPException(status_code=400, detail=f"{message}: {exc}") from exc


@router.post("/cancel")
async def cancel_subscription(
    request: Request,
    payload: CancelSubscriptionPayload,
    user=Depends(require_user),
    service: SubscriptionService = Depends(get_subscription_service),
) -> dict:
    """Cancel user's subscription."""
    locale = request_locale(request)
    try:
        return service.cancel_subscription(user, payload.subscription_id)
    except SubscriptionError as exc:
        message = translate("subscriptions.errors.cancelFailed", locale=locale, default="Failed to cancel subscription")
        raise HTTPException(status_code=400, detail=f"{message}: {exc}") from exc


@router.get("/list")
async def list_user_subscriptions(
    request: Request,
    user=Depends(require_user),
    service: SubscriptionService = Depends(get_subscription_service),
) -> dict:
    """Get all subscriptions for the current user."""
    subscriptions = service.get_user_subscriptions(user)
    return {
        "subscriptions": [
            {
                "id": sub.id,
                "plan_id": sub.plan_id,
                "status": sub.status,
                "current_period_start": sub.current_period_start.isoformat(),
                "current_period_end": sub.current_period_end.isoformat(),
                "cancel_at_period_end": sub.cancel_at_period_end,
                "trial_start": sub.trial_start.isoformat() if sub.trial_start else None,
                "trial_end": sub.trial_end.isoformat() if sub.trial_end else None,
            }
            for sub in subscriptions
        ]
    }


@router.get("/history")
async def get_subscription_history(
    request: Request,
    subscription_id: int | None = None,
    user=Depends(require_user),
    service: SubscriptionService = Depends(get_subscription_service),
) -> dict:
    """Get billing history for user's subscriptions."""
    from todayflow_backend.db.session import SessionLocal
    from todayflow_backend.db import models as db_models

    session = SessionLocal()
    try:
        subscriptions = service.get_user_subscriptions(user)
        if subscription_id:
            subscriptions = [s for s in subscriptions if s.id == subscription_id]

        history_records = []
        for sub in subscriptions:
            records = session.query(db_models.SubscriptionHistory).filter_by(subscription_id=sub.id).order_by(db_models.SubscriptionHistory.created_at.desc()).all()
            history_records.extend(records)

        return {
            "history": [
                {
                    "id": record.id,
                    "subscription_id": record.subscription_id,
                    "amount": record.amount,
                    "currency": record.currency,
                    "status": record.status,
                    "period_start": record.period_start.isoformat(),
                    "period_end": record.period_end.isoformat(),
                    "created_at": record.created_at.isoformat(),
                    "stripe_invoice_id": record.stripe_invoice_id,
                }
                for record in history_records
            ]
        }
    finally:
        session.close()
