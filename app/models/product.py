import datetime

from sqlalchemy import String, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Product(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    internal_sku: Mapped[str]    = mapped_column(String(255), nullable=False, unique=True)
    name: Mapped[str]            = mapped_column(String(255), nullable=False)
    manufacturer_id: Mapped[int] = mapped_column(
        # ForeignKey("manufacturer.id"), 
        nullable=False)
    category_id: Mapped[int]     = mapped_column(
        # ForeignKey("category.id"), 
        nullable=False)
    product_type_id: Mapped[int] = mapped_column(
        # ForeignKey("product_type.id"), 
        nullable=False)
    brand_id: Mapped[int]        = mapped_column(
        # ForeignKey("brand.id"), 
        nullable=False)
    family_id: Mapped[int]       = mapped_column(
        # ForeignKey("product_family.id"), 
        nullable=False)
    options: Mapped[dict]        = mapped_column(JSONB, nullable=False, default=dict)
    is_active: Mapped[bool]      = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())