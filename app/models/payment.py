from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum
from app.core.database import Base


class PaymentStatus(str, enum.Enum):
    CREATED = "created"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    EXPIRED = "expired"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(String, unique=True, nullable=False, index=True)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False)

    amount = Column(Numeric(36, 18), nullable=False)
    currency = Column(String, default="USDT")

    customer_wallet = Column(String, nullable=True)
    merchant_wallet = Column(String, nullable=False)

    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.CREATED)

    order_id = Column(String, nullable=True)
    description = Column(String, nullable=True)
    payment_metadata = Column(String, nullable=True)

    checkout_url = Column(String, nullable=True)
    success_url = Column(String, nullable=True)
    cancel_url = Column(String, nullable=True)

    tx_hash = Column(String, nullable=True, index=True)
    block_number = Column(String, nullable=True)

    expires_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
