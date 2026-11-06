from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import secrets
import hashlib
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.merchant import Merchant
from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentStatusResponse
from app.core.config import settings

router = APIRouter(prefix="/api/payments", tags=["payments"])


async def get_merchant_by_api_key(
    api_key: str = Header(..., alias="X-API-Key"),
    db: AsyncSession = Depends(get_db)
) -> Merchant:
    """Authenticate merchant by API key"""
    result = await db.execute(
        select(Merchant).where(Merchant.api_key == api_key, Merchant.is_active == True)
    )
    merchant = result.scalar_one_or_none()

    if not merchant:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return merchant


@router.post("/checkout/create", response_model=PaymentResponse)
async def create_checkout_session(
    payment_data: PaymentCreate,
    merchant: Merchant = Depends(get_merchant_by_api_key),
    db: AsyncSession = Depends(get_db)
):
    """Create a new payment checkout session"""

    # Generate unique payment ID
    payment_id = f"pay_{secrets.token_urlsafe(16)}"

    # Calculate expiry (1 hour from now)
    expires_at = datetime.utcnow() + timedelta(hours=1)

    # Create payment record
    payment = Payment(
        payment_id=payment_id,
        merchant_id=merchant.id,
        amount=payment_data.amount,
        currency=payment_data.currency,
        merchant_wallet=merchant.payout_address,
        status=PaymentStatus.CREATED,
        order_id=payment_data.order_id,
        description=payment_data.description,
        success_url=payment_data.success_url,
        cancel_url=payment_data.cancel_url,
        metadata=payment_data.metadata,
        expires_at=expires_at
    )

    # Generate checkout URL
    payment.checkout_url = f"{settings.FRONTEND_URL}/checkout/{payment_id}"

    db.add(payment)
    await db.commit()
    await db.refresh(payment)

    return payment


@router.get("/{payment_id}/status", response_model=PaymentStatusResponse)
async def get_payment_status(
    payment_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get payment status"""
    result = await db.execute(
        select(Payment).where(Payment.payment_id == payment_id)
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return payment


@router.post("/{payment_id}/confirm")
async def confirm_payment(
    payment_id: str,
    tx_hash: str,
    customer_wallet: str,
    db: AsyncSession = Depends(get_db)
):
    """Confirm payment transaction"""
    from app.services.blockchain import blockchain_service
    from app.services.webhook import webhook_service

    result = await db.execute(
        select(Payment).where(Payment.payment_id == payment_id)
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status == PaymentStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="Payment already confirmed")

    if payment.status == PaymentStatus.EXPIRED:
        raise HTTPException(status_code=400, detail="Payment expired")

    # Update payment status to pending
    payment.status = PaymentStatus.PENDING
    payment.tx_hash = tx_hash
    payment.customer_wallet = customer_wallet
    await db.commit()

    # Verify transaction on blockchain
    payment_id_hash = hashlib.sha256(payment_id.encode()).hexdigest()
    expected_amount = blockchain_service.convert_to_token_amount(str(payment.amount))

    is_valid = blockchain_service.verify_payment_transaction(
        tx_hash=tx_hash,
        expected_payment_id=payment_id_hash,
        expected_merchant=payment.merchant_wallet,
        expected_amount=expected_amount
    )

    if is_valid:
        # Update payment to confirmed
        payment.status = PaymentStatus.CONFIRMED
        payment.confirmed_at = datetime.utcnow()

        # Get transaction receipt for block number
        receipt = blockchain_service.get_transaction_receipt(tx_hash)
        if receipt:
            payment.block_number = str(receipt.get('blockNumber'))

        await db.commit()
        await db.refresh(payment)

        # Get merchant for webhook
        merchant_result = await db.execute(
            select(Merchant).where(Merchant.id == payment.merchant_id)
        )
        merchant = merchant_result.scalar_one()

        # Send webhook if configured
        if merchant.webhook_url:
            await webhook_service.send_webhook(
                webhook_url=merchant.webhook_url,
                event_type="payment.confirmed",
                data={
                    "payment_id": payment.payment_id,
                    "amount": str(payment.amount),
                    "currency": payment.currency,
                    "tx_hash": tx_hash,
                    "customer_wallet": customer_wallet,
                    "order_id": payment.order_id
                }
            )

        return {"status": "confirmed", "payment": payment}
    else:
        payment.status = PaymentStatus.FAILED
        await db.commit()
        raise HTTPException(status_code=400, detail="Transaction verification failed")
