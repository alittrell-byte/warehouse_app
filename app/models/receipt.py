import datetime
from sqlalchemy import Enum as SQLEnum, TEXT, DateTime, Integer, Computed, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from typing import Optional
from app.enums.approval_status import ApprovalStatus


class Receipt(Base):
    __tablename__ = 'receipt'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    po_line_item_id: Mapped[int] = mapped_column()  # BIGINT NOT NULL REFERENCES po_line_item(id),
    packing_slip_line_id: Mapped[Optional[int]] = mapped_column() #BIGINT REFERENCES packing_slip_line(id),
    qty_counted: Mapped[int] = mapped_column(nullable=False)      #INT NOT NULL,          -- physically counted at dock
    qty_accepted: Mapped[Optional[int]] = mapped_column()
    qty_quarantined: Mapped[Optional[int]] = mapped_column(Integer,Computed("qty_counted - qty_accepted", persisted=True))
    is_overage: Mapped[bool] = mapped_column(nullable=False, default=False)        #BOOLEAN NOT NULL DEFAULT FALSE,
    is_shortage: Mapped[bool] = mapped_column(nullable=False, default=False)       #BOOLEAN NOT NULL DEFAULT FALSE,
    is_duplicate: Mapped[bool] = mapped_column(nullable=False, default=False)      #BOOLEAN NOT NULL DEFAULT FALSE,
    approval_status: Mapped[ApprovalStatus] = mapped_column(SQLEnum(ApprovalStatus, native_enum=False), nullable=False, default="auto")   #VARCHAR(20) NOT NULL DEFAULT 'auto',-- auto (within tolerance) | pending | approved | rejected
    approved_by: Mapped[Optional[int]] = mapped_column(
        # ForeignKey("users.id")
    )       #BIGINT,                -- FK to users, nullable
    approved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))      #TIMESTAMPTZ,
    received_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())      #TIMESTAMPTZ NOT NULL DEFAULT now(),
    notes: Mapped[Optional[str]] = mapped_column(TEXT)             #TEXT