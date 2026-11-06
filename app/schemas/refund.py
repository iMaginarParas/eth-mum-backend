from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class RefundCreate(BaseModel):
    payment_id: str
    amount: str
    reason: Optional[str] = None


class RefundResponse(BaseModel):
    id: UUID
    refund_id: str
    payment_id: UUID
    amount: Decimal
    reason: Optional[str]
    status: str
    tx_hash: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
