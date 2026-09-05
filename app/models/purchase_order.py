import datetime

from sqlalchemy import  ForeignKey, func, Enum as SQLEnum, TEXT, DATE, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


from app.enums.po_status import POStatus
from app.enums.reconciliation_status import ReconciliationStatus

class PurchaseOrder(Base):
    __tablename__ = 'purchase_order'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendor.id"), nullable=False) # vendor_id     BIGINT NOT NULL REFERENCES vendor(id),
    created_by: Mapped[int] = mapped_column() # created_by    BIGINT NOT NULL,   -- FK to users table
    description: Mapped[str] = mapped_column(TEXT, nullable=False) # description   TEXT,
    notes: Mapped[str] = mapped_column(TEXT) # notes         TEXT,
    status: Mapped[POStatus] = mapped_column(SQLEnum(POStatus, native_enum=False), nullable=False, default="created") # status        VARCHAR(20) NOT NULL DEFAULT 'created',#     -- created | sent | receiving | received | problem | closed
    reconciliation_status: Mapped[ReconciliationStatus] = mapped_column(SQLEnum(ReconciliationStatus, native_enum=False), nullable=False, default="pending") # reconciliation_status VARCHAR(20) NOT NULL DEFAULT 'pending', #     -- pending | matched | overage | shortage | price_mismatch | resolved
    order_date: Mapped[datetime.date] = mapped_column(DATE) # order_date    DATE,
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now()) # created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
