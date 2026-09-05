import datetime
from typing import Optional

from sqlalchemy import ForeignKey, TEXT, DATE, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class PackingSlip(Base):
    __tablename__ = "packing_slip"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    po_id: Mapped[int] = mapped_column(ForeignKey("purchase_order.id"), nullable=False)
    vendor_packing_slip_number: Mapped[Optional[str]] = mapped_column(String(100))
    tracking_number: Mapped[Optional[str]] = mapped_column(String(100))
    received_date: Mapped[Optional[datetime.date]] = mapped_column(DATE)
    notes: Mapped[Optional[str]] = mapped_column(TEXT)