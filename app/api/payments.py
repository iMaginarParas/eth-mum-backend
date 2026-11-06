from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
import secrets
import hashlib
from datetime import datetime, timedelta

from app.core.supabase import get_supabase
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentStatusResponse
from app.core.config import settings

router = APIRouter(prefix="/api/payments", tags=["payments"])


async def get_merchant_by_api_key(
    api_key: str = Header(..., alias="X-API-Key")
):
    """Authenticate merchant by API key"""
    supabase = get_supabase()

    result = supabase.table('merchants').select('*').eq('api_key', api_key).eq('is_active', True).execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return result.data[0]


@router.post("/checkout/create", response_model=PaymentResponse)
async def create_checkout_session(
    payment_data: PaymentCreate,
    merchant: dict = Depends(get_merchant_by_api_key)
):
    """Create a new payment checkout session"""
    supabase = get_supabase()

    # Generate unique payment ID
    payment_id = f"pay_{secrets.token_urlsafe(16)}"

    # Calculate expiry (1 hour from now)
    expires_at = (datetime.utcnow() + timedelta(hours=1)).isoformat()

    # Create payment record
    payment_data_dict = {
        "payment_id": payment_id,
        "merchant_id": merchant['id'],
        "amount": str(payment_data.amount),
        "currency": payment_data.currency,
        "merchant_wallet": merchant['payout_address'],
        "status": "created",
        "order_id": payment_data.order_id,
        "description": payment_data.description,
        "success_url": payment_data.success_url,
        "cancel_url": payment_data.cancel_url,
        "payment_metadata": payment_data.metadata or {},
        "expires_at": expires_at,
        "checkout_url": f"{settings.FRONTEND_URL}/checkout/{payment_id}"
    }

    result = supabase.table('payments').insert(payment_data_dict).execute()

    return result.data[0]


@router.get("/{payment_id}/status", response_model=PaymentStatusResponse)
async def get_payment_status(payment_id: str):
    """Get payment status"""
    supabase = get_supabase()

    result = supabase.table('payments').select('*').eq('payment_id', payment_id).execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="Payment not found")

    return result.data[0]


@router.post("/{payment_id}/confirm")
async def confirm_payment(
    payment_id: str,
    tx_hash: str,
    customer_wallet: str
):
    """Confirm payment transaction"""
    from app.services.blockchain import blockchain_service
    from app.services.webhook import webhook_service

    supabase = get_supabase()

    # Get payment
    payment_result = supabase.table('payments').select('*').eq('payment_id', payment_id).execute()

    if not payment_result.data or len(payment_result.data) == 0:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment = payment_result.data[0]

    if payment['status'] == 'confirmed':
        raise HTTPException(status_code=400, detail="Payment already confirmed")

    if payment['status'] == 'expired':
        raise HTTPException(status_code=400, detail="Payment expired")

    # Update payment status to pending
    supabase.table('payments').update({
        'status': 'pending',
        'tx_hash': tx_hash,
        'customer_wallet': customer_wallet
    }).eq('payment_id', payment_id).execute()

    # Verify transaction on blockchain
    payment_id_hash = hashlib.sha256(payment_id.encode()).hexdigest()
    expected_amount = blockchain_service.convert_to_token_amount(payment['amount'])

    is_valid = blockchain_service.verify_payment_transaction(
        tx_hash=tx_hash,
        expected_payment_id=payment_id_hash,
        expected_merchant=payment['merchant_wallet'],
        expected_amount=expected_amount
    )

    if is_valid:
        # Update payment to confirmed
        update_data = {
            'status': 'confirmed',
            'confirmed_at': datetime.utcnow().isoformat()
        }

        # Get transaction receipt for block number
        receipt = blockchain_service.get_transaction_receipt(tx_hash)
        if receipt:
            update_data['block_number'] = str(receipt.get('blockNumber'))

        result = supabase.table('payments').update(update_data).eq('payment_id', payment_id).execute()
        updated_payment = result.data[0]

        # Get merchant for webhook
        merchant_result = supabase.table('merchants').select('*').eq('id', payment['merchant_id']).execute()
        merchant = merchant_result.data[0]

        # Send webhook if configured
        if merchant.get('webhook_url'):
            await webhook_service.send_webhook(
                webhook_url=merchant['webhook_url'],
                event_type="payment.confirmed",
                data={
                    "payment_id": payment_id,
                    "amount": payment['amount'],
                    "currency": payment['currency'],
                    "tx_hash": tx_hash,
                    "customer_wallet": customer_wallet,
                    "order_id": payment.get('order_id')
                }
            )

        return {"status": "confirmed", "payment": updated_payment}
    else:
        supabase.table('payments').update({'status': 'failed'}).eq('payment_id', payment_id).execute()
        raise HTTPException(status_code=400, detail="Transaction verification failed")
