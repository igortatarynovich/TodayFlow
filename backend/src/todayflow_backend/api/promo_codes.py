"""Promo code endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from todayflow_backend.api.auth import require_user, get_optional_user
from todayflow_backend.db import models as db_models
from todayflow_backend.db.session import get_session
from todayflow_backend.i18n import request_locale, translate

router = APIRouter(prefix="/promo-codes", tags=["promo-codes"])


class ValidatePromoCodePayload(BaseModel):
    code: str
    amount: int | None = None  # Amount in cents (for validation)
    product_type: str | None = None  # 'subscription', 'report', etc.


class PromoCodeResponse(BaseModel):
    code: str
    discount_type: str
    discount_value: float
    discount_amount: int  # Calculated discount in cents
    final_amount: int  # Final amount after discount
    description: str | None = None


@router.post("/validate", response_model=PromoCodeResponse)
async def validate_promo_code(
    request: Request,
    payload: ValidatePromoCodePayload,
    user=Depends(get_optional_user),
    db: Session = Depends(get_session),
) -> PromoCodeResponse:
    """Validate a promo code and calculate discount."""
    locale = request_locale(request)
    
    promo_code = db.query(db_models.PromoCode).filter_by(
        code=payload.code.upper().strip(),
        is_active=True
    ).first()
    
    if not promo_code:
        raise HTTPException(
            status_code=404,
            detail=translate("promo_codes.notFound", locale=locale, default="Промокод не найден")
        )
    
    user_id = user.id if user else None
    amount = payload.amount or 0
    
    # Check if code is applicable to product type
    if payload.product_type:
        if promo_code.applicable_to not in ["all", payload.product_type]:
            raise HTTPException(
                status_code=400,
                detail=translate("promo_codes.notApplicable", locale=locale, default="Промокод не применим к этому типу продукта")
            )
    
    is_valid, error_message = promo_code.is_valid(user_id=user_id, amount=amount, db_session=db)
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=error_message or translate("promo_codes.invalid", locale=locale, default="Промокод недействителен")
        )
    
    # Check if user already used this code
    if user_id:
        existing = db.query(db_models.PromoCodeUsage).filter_by(
            promo_code_id=promo_code.id,
            user_id=user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=translate("promo_codes.alreadyUsed", locale=locale, default="Вы уже использовали этот промокод")
            )
    
    discount_amount = promo_code.calculate_discount(amount) if amount > 0 else 0
    final_amount = max(0, amount - discount_amount)
    
    return PromoCodeResponse(
        code=promo_code.code,
        discount_type=promo_code.discount_type,
        discount_value=promo_code.discount_value,
        discount_amount=discount_amount,
        final_amount=final_amount,
        description=promo_code.description,
    )


@router.post("/apply")
async def apply_promo_code(
    request: Request,
    payload: ValidatePromoCodePayload,
    user=Depends(require_user),
    db: Session = Depends(get_session),
) -> dict:
    """Apply a promo code (record usage). This is called after successful payment."""
    locale = request_locale(request)
    
    promo_code = db.query(db_models.PromoCode).filter_by(
        code=payload.code.upper().strip(),
        is_active=True
    ).first()
    
    if not promo_code:
        raise HTTPException(
            status_code=404,
            detail=translate("promo_codes.notFound", locale=locale, default="Промокод не найден")
        )
    
    if not payload.amount:
        raise HTTPException(
            status_code=400,
            detail=translate("promo_codes.amountRequired", locale=locale, default="Необходимо указать сумму")
        )
    
    is_valid, error_message = promo_code.is_valid(user_id=user.id, amount=payload.amount)
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=error_message or translate("promo_codes.invalid", locale=locale, default="Промокод недействителен")
        )
    
    discount_amount = promo_code.calculate_discount(payload.amount)
    final_amount = max(0, payload.amount - discount_amount)
    
    # Record usage
    usage = db_models.PromoCodeUsage(
        promo_code_id=promo_code.id,
        user_id=user.id,
        discount_amount=discount_amount,
        original_amount=payload.amount,
        final_amount=final_amount,
    )
    db.add(usage)
    
    # Update usage count
    promo_code.current_uses = (promo_code.current_uses or 0) + 1
    
    db.commit()
    
    return {
        "message": translate("promo_codes.applied", locale=locale, default="Промокод применен"),
        "discount_amount": discount_amount,
        "final_amount": final_amount,
    }

