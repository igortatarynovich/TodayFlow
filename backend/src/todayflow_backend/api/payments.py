"""Stripe payment endpoints."""

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel

from todayflow_backend.api.auth import require_user
from todayflow_backend.i18n import request_locale, translate
from todayflow_backend.services import payments as payment_service
from todayflow_backend.services.subscriptions import get_subscription_service


class CheckoutPayload(BaseModel):
    user_id: int


router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/checkout-session")
async def create_checkout_session(request: Request, payload: CheckoutPayload, user=Depends(require_user)) -> dict:
    locale = request_locale(request)
    if not user.is_admin and payload.user_id != user.id:
        raise HTTPException(status_code=403, detail=translate("auth.errors.adminRequired", locale=locale))

    target_user_id = payload.user_id if user.is_admin else user.id
    try:
        return payment_service.create_checkout_session(user_id=target_user_id)
    except payment_service.PaymentError as exc:
        message = translate("payments.errors.checkoutFailed", locale=locale)
        raise HTTPException(status_code=400, detail=f"{message}: {exc}") from exc


@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
) -> dict:
    payload = await request.body()
    if stripe_signature is None:
        raise HTTPException(
            status_code=400, detail=translate("payments.errors.missingSignature", locale=request_locale(request))
        )
    try:
        import stripe
        from todayflow_backend.core.config import settings

        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=stripe_signature,
            secret=settings.stripe_webhook_secret,
        )

        # Handle one-time payments
        payment_service.handle_webhook(payload, stripe_signature)

        # Handle subscription events
        subscription_service = get_subscription_service()
        subscription_service.handle_webhook(event)

    except payment_service.PaymentError as exc:
        message = translate("payments.errors.webhook", locale=request_locale(request))
        raise HTTPException(status_code=400, detail=f"{message}: {exc}") from exc
    except Exception as exc:
        message = translate("payments.errors.webhook", locale=request_locale(request))
        raise HTTPException(status_code=400, detail=f"{message}: {exc}") from exc
    return {"status": "ok"}
