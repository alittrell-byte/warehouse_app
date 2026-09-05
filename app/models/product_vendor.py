from decimal import Decimal

from sqlalchemy import String, ForeignKey, func, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from app.database import Base

class ProductVendor(Base):
    __tablename__ = "product_vendor"

    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), primary_key=True) # product_id      BIGINT NOT NULL REFERENCES product(id),
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendor.id"), primary_key=True) # vendor_id       BIGINT NOT NULL REFERENCES vendor(id),
    vendor_product_id: Mapped[str] = mapped_column(String(255), nullable=False) # vendor_product_id VARCHAR(64) NOT NULL,   -- vendor's own sku
    cost: Mapped[Decimal] = mapped_column(Numeric(12,2), nullable=False) # cost            NUMERIC(12,2) NOT NULL,
    msrp: Mapped[Optional[Decimal]] = mapped_column(Numeric(12,2)) # msrp            NUMERIC(12,2),
    map_pricing: Mapped[Optional[Decimal]] = mapped_column(Numeric(12,2)) # map_pricing     NUMERIC(12,2),
    lead_time_days: Mapped[int] = mapped_column(nullable=False, default=0) # lead_time_days  INT NOT NULL DEFAULT 0,
    minimum_order_qty: Mapped[int] = mapped_column(nullable=False, default=1) # minimum_order_qty INT NOT NULL DEFAULT 1,
    pack_qty: Mapped[int] = mapped_column(nullable=False, default=1) # pack_qty        INT NOT NULL DEFAULT 1,
    is_preferred: Mapped[bool] = mapped_column(nullable=False, default=False) # is_preferred    BOOLEAN NOT NULL DEFAULT FALSE,   -- primary vendor flag
    # PRIMARY KEY (product_id, vendor_id)
