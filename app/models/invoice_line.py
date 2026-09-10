from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from decimal import Decimal


class InvoiceLine(Base):
    __tablename__ = 'invoice_line'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoice.id"), nullable=False)  # invoice_id   BIGINT NOT NULL REFERENCES invoice(id),
    po_line_item_id: Mapped[int] = mapped_column(ForeignKey("po_line_item.id"), nullable=False)  # po_line_item_id BIGINT NOT NULL REFERENCES po_line_item(id),  -- ties to the exact line, not just the PO
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), nullable=False)  # product_id   BIGINT NOT NULL REFERENCES product(id),
    qty_invoiced: Mapped[int] = mapped_column(nullable=False)  # qty_invoiced INT NOT NULL,
    price: Mapped[Decimal] = mapped_column(Numeric(12,2), nullable=False)  # price        NUMERIC(12,2) NOT NULL,
    is_problem: Mapped[bool] = mapped_column(nullable=False, default=False)  # is_problem   BOOLEAN NOT NULL DEFAULT FALSE
