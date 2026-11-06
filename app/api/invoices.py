from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.core.database import get_db
from app.models.merchant import Merchant
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceCreate, InvoiceResponse
from app.api.payments import get_merchant_by_api_key
from app.core.config import settings

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


def generate_invoice_number() -> str:
    """Generate unique invoice number"""
    import time
    timestamp = int(time.time())
    return f"INV-{timestamp}"


@router.post("/create", response_model=InvoiceResponse)
async def create_invoice(
    invoice_data: InvoiceCreate,
    merchant: Merchant = Depends(get_merchant_by_api_key),
    db: AsyncSession = Depends(get_db)
):
    """Create a new invoice"""

    invoice_number = generate_invoice_number()

    invoice = Invoice(
        invoice_number=invoice_number,
        merchant_id=merchant.id,
        title=invoice_data.title,
        customer_name=invoice_data.customer_name,
        customer_email=invoice_data.customer_email,
        amount=invoice_data.amount,
        description=invoice_data.description,
        due_date=invoice_data.due_date
    )

    # Generate payment link
    invoice.payment_link = f"{settings.FRONTEND_URL}/invoice/{invoice_number}"

    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)

    return invoice


@router.get("/{invoice_number}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Get invoice by number"""
    result = await db.execute(
        select(Invoice).where(Invoice.invoice_number == invoice_number)
    )
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return invoice
