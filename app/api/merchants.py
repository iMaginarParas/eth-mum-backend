from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import secrets

from app.core.database import get_db
from app.models.merchant import Merchant
from app.schemas.merchant import MerchantCreate, MerchantResponse

router = APIRouter(prefix="/api/merchants", tags=["merchants"])


@router.post("/register", response_model=MerchantResponse)
async def register_merchant(
    merchant_data: MerchantCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new merchant"""

    # Check if email already exists
    result = await db.execute(
        select(Merchant).where(Merchant.email == merchant_data.email)
    )
    existing_merchant = result.scalar_one_or_none()

    if existing_merchant:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate API key
    api_key = f"pk_live_{secrets.token_urlsafe(32)}"

    merchant = Merchant(
        email=merchant_data.email,
        business_name=merchant_data.business_name,
        wallet_address=merchant_data.wallet_address,
        payout_address=merchant_data.payout_address,
        webhook_url=merchant_data.webhook_url,
        api_key=api_key
    )

    db.add(merchant)
    await db.commit()
    await db.refresh(merchant)

    return merchant
