from pydantic import BaseModel
from typing import Optional
import datetime


class PackingSlipLineNested(BaseModel):
    product_id: int
    qty_shipped: int


class PackingSlipCreate(BaseModel):
    po_id: int
    vendor_packing_slip_number: Optional[str] = None
    tracking_number: Optional[str] = None
    received_date: Optional[datetime.date] = None
    notes: Optional[str] = None
    lines: list[PackingSlipLineNested]


class PackingSlipOut(BaseModel):
    id: int
    po_id: int
    vendor_packing_slip_number: Optional[str]
    tracking_number: Optional[str]
    received_date: Optional[datetime.date]
    notes: Optional[str]

    class Config:
        from_attributes = True