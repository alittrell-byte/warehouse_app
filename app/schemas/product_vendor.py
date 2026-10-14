from pydantic import BaseModel
from decimal import Decimal
from typing import Optional


class ProductVendorCreate(BaseModel):
    product_id: int
    vendor_id: int
    vendor_product_id: str
    cost: Decimal
    msrp: Optional[Decimal] = None
    map_pricing: Optional[Decimal] = None
    lead_time_days: int = 0
    minimum_order_qty: int = 1
    pack_qty: int = 1
    is_preferred: bool = False

class ProductVendorOut(BaseModel):
    product_id: int
    vendor_id: int
    vendor_product_id: str
    cost: Decimal
    msrp: Optional[Decimal]
    map_pricing: Optional[Decimal]
    lead_time_days: int
    minimum_order_qty: int
    pack_qty: int
    is_preferred: bool

    class Config:
        from_attributes = True