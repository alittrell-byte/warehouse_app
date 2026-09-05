from pydantic import BaseModel
import datetime
from decimal import Decimal
from typing import Optional


class POLineItemCreate(BaseModel):
    po_id: int
    product_id: int
    vendor_sku: str
    cost: Decimal
    qty_ordered: int
    expected_delivery_date: datetime.date
    notes: Optional[str] = None

class POLineItemOut(BaseModel):
    id: int
    po_id: int
    product_id: int
    vendor_sku: str
    cost: Decimal
    qty_ordered: int
    expected_delivery_date: datetime.date
    notes: str

    class Config:
        from_attributes = True