from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class InvoiceCreate(BaseModel):
    title: str
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    amount: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class InvoiceResponse(BaseModel):
    id: UUID
    invoice_number: str
    title: str
    customer_name: Optional[str]
    customer_email: Optional[str]
    amount: Decimal
    description: Optional[str]
    is_paid: bool
    payment_link: Optional[str]
    due_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
