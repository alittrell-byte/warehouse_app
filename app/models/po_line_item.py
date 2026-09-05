import datetime
from decimal import Decimal

from sqlalchemy import String, ForeignKey, func, DATE, TEXT, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from app.database import Base

class POLineItem(Base):
    __tablename__ = 'po_line_item'
    id: Mapped[int] = mapped_column(primary_key=True, index=True) # id                BIGSERIAL PRIMARY KEY,
    po_id: Mapped[int] = mapped_column(ForeignKey("purchase_order.id"), nullable=False) # po_id             BIGINT NOT NULL REFERENCES purchase_order(id),
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), nullable=False) # product_id        BIGINT NOT NULL REFERENCES product(id),
    vendor_sku: Mapped[Optional[str]] = mapped_column(String(255)) # vendor_sku        VARCHAR(64),          -- snapshot, vendor sku can change
    cost: Mapped[Decimal] = mapped_column(Numeric(12,2), nullable=False) # cost              NUMERIC(12,2) NOT NULL,  -- snapshot at order time,#-- NOT a live join to product_vendor.cost
    qty_ordered: Mapped[int] = mapped_column(nullable=False) # qty_ordered       INT NOT NULL,
    expected_delivery_date: Mapped[Optional[datetime.date]] = mapped_column(DATE) # expected_delivery_date DATE,
    notes: Mapped[Optional[str]] = mapped_column(TEXT) # notes             TEXT
