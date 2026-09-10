import datetime
from decimal import Decimal
from typing import Optional


from sqlalchemy import String, ForeignKey, func, DATE, TEXT, Numeric, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.enums.invoice_status import InvoiceStatus

class Invoice(Base):
    __tablename__ = 'invoice'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendor.id"), nullable=False)             # BIGINT NOT NULL REFERENCES vendor(id),
    vendor_invoice_number: Mapped[str] = mapped_column(String(255)) # VARCHAR(100),
    invoice_date: Mapped[datetime.date] = mapped_column(DATE)          # DATE,
    ship_start_date: Mapped[datetime.date] = mapped_column(DATE)       # DATE,
    status: Mapped[InvoiceStatus] = mapped_column(SQLEnum(InvoiceStatus, native_enum=False), nullable=False, default="created")                # VARCHAR(20) NOT NULL DEFAULT 'created', -- created | receiving | received | problem | closed
    payment_due_date: Mapped[datetime.date] = mapped_column(DATE)      # DATE,
    sub_total: Mapped[Decimal] = mapped_column(Numeric(12,2))             # NUMERIC(12,2),
    tax_total: Mapped[Decimal] = mapped_column(Numeric(12,2))             # NUMERIC(12,2),
    shipping_total: Mapped[Decimal] = mapped_column(Numeric(12,2))        # NUMERIC(12,2),
    notes: Mapped[Optional[str]] = mapped_column(TEXT)                 # TEXT
