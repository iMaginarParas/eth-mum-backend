from fastapi import APIRouter, HTTPException
import secrets

from app.core.supabase import get_supabase
from app.schemas.merchant import MerchantCreate, MerchantResponse

router = APIRouter(prefix="/api/merchants", tags=["merchants"])


@router.post("/register", response_model=MerchantResponse)
async def register_merchant(merchant_data: MerchantCreate):
    """Register a new merchant"""
    supabase = get_supabase()

    # Check if email already exists
    existing = supabase.table('merchants').select('*').eq('email', merchant_data.email).execute()

    if existing.data and len(existing.data) > 0:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate API key
    api_key = f"pk_live_{secrets.token_urlsafe(32)}"

    merchant_dict = {
        "email": merchant_data.email,
        "business_name": merchant_data.business_name,
        "wallet_address": merchant_data.wallet_address,
        "payout_address": merchant_data.payout_address,
        "webhook_url": merchant_data.webhook_url,
        "api_key": api_key,
        "is_active": True
    }

    result = supabase.table('merchants').insert(merchant_dict).execute()

    return result.data[0]
