from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum
from app.core.database import Base


class RefundStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    refund_id = Column(String, unique=True, nullable=False, index=True)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=False)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False)

    amount = Column(Numeric(36, 18), nullable=False)
    reason = Column(String, nullable=True)

    customer_wallet = Column(String, nullable=False)

    status = Column(SQLEnum(RefundStatus), default=RefundStatus.PENDING)

    tx_hash = Column(String, nullable=True, index=True)
    block_number = Column(String, nullable=True)

    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
