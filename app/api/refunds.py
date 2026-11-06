from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import secrets
from decimal import Decimal

from app.core.database import get_db
from app.models.merchant import Merchant
from app.models.payment import Payment, PaymentStatus
from app.models.refund import Refund, RefundStatus
from app.schemas.refund import RefundCreate, RefundResponse
from app.api.payments import get_merchant_by_api_key

router = APIRouter(prefix="/api/refunds", tags=["refunds"])


@router.post("/create", response_model=RefundResponse)
async def create_refund(
    refund_data: RefundCreate,
    merchant: Merchant = Depends(get_merchant_by_api_key),
    db: AsyncSession = Depends(get_db)
):
    """Create a refund for a payment"""

    # Get the original payment
    result = await db.execute(
        select(Payment).where(
            Payment.payment_id == refund_data.payment_id,
            Payment.merchant_id == merchant.id
        )
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status != PaymentStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="Payment not confirmed")

    # Check refund amount doesn't exceed original payment
    refund_amount = Decimal(refund_data.amount)

    # Get total already refunded
    refunds_result = await db.execute(
        select(Refund).where(
            Refund.payment_id == payment.id,
            Refund.status == RefundStatus.COMPLETED
        )
    )
    existing_refunds = refunds_result.scalars().all()
    total_refunded = sum(r.amount for r in existing_refunds)

    if total_refunded + refund_amount > payment.amount:
        raise HTTPException(
            status_code=400,
            detail="Refund amount exceeds available balance"
        )

    # Create refund record
    refund_id = f"refund_{secrets.token_urlsafe(16)}"

    refund = Refund(
        refund_id=refund_id,
        payment_id=payment.id,
        merchant_id=merchant.id,
        amount=refund_amount,
        reason=refund_data.reason,
        customer_wallet=payment.customer_wallet,
        status=RefundStatus.PENDING
    )

    db.add(refund)
    await db.commit()
    await db.refresh(refund)

    return refund


@router.get("/{refund_id}", response_model=RefundResponse)
async def get_refund(
    refund_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get refund details"""
    result = await db.execute(
        select(Refund).where(Refund.refund_id == refund_id)
    )
    refund = result.scalar_one_or_none()

    if not refund:
        raise HTTPException(status_code=404, detail="Refund not found")

    return refund
