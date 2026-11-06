from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class PaymentCreate(BaseModel):
    amount: str
    currency: str = "USDT"
    order_id: Optional[str] = None
    description: Optional[str] = None
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None
    metadata: Optional[str] = None


class PaymentResponse(BaseModel):
    id: UUID
    payment_id: str
    amount: Decimal
    currency: str
    status: str
    checkout_url: str
    merchant_wallet: str
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentStatusResponse(BaseModel):
    payment_id: str
    status: str
    amount: Decimal
    tx_hash: Optional[str]
    confirmed_at: Optional[datetime]

    class Config:
        from_attributes = True
