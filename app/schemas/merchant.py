from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class MerchantLogin(BaseModel):
    email: EmailStr
    password: str


class MerchantCreate(BaseModel):
    email: EmailStr
    business_name: str
    wallet_address: str
    payout_address: str
    password: str
    webhook_url: Optional[str] = None


class MerchantResponse(BaseModel):
    id: UUID
    email: str
    business_name: str
    wallet_address: str
    payout_address: str
    api_key: str
    webhook_url: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
