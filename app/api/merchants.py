from fastapi import APIRouter, HTTPException, Header, Depends
import secrets

from app.core.supabase import get_supabase
from app.schemas.merchant import MerchantCreate, MerchantResponse

router = APIRouter(prefix="/api/merchants", tags=["merchants"])


async def get_merchant_by_api_key(
    api_key: str = Header(..., alias="X-API-Key")
):
    """Authenticate merchant by API key"""
    supabase = get_supabase()

    result = supabase.table('merchants').select('*').eq('api_key', api_key).eq('is_active', True).execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return result.data[0]


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


@router.get("/me", response_model=MerchantResponse)
async def get_current_merchant(merchant: dict = Depends(get_merchant_by_api_key)):
    """Get current merchant details by API key"""
    return merchant
