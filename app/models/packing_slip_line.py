from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class PackingSlipLine(Base):
    __tablename__ = "packing_slip_line"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    packing_slip_id: Mapped[int] = mapped_column(ForeignKey("packing_slip.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), nullable=False)
    qty_shipped: Mapped[int] = mapped_column(nullable=False)