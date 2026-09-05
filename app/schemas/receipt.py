from pydantic import BaseModel
from typing import Optional, Literal
import datetime

class ReceiptCreate(BaseModel):
    po_line_item_id: int
    packing_slip_line_id: int
    qty_counted: int
    notes: Optional[str] = None

class ReceiptOut(BaseModel):
    id: int
    po_line_item_id: int
    packing_slip_line_id: Optional[int]
    qty_counted: int
    qty_accepted: Optional[int]
    qty_quarantined: Optional[int]
    is_overage: bool
    is_shortage: bool
    is_duplicate: bool
    approval_status: str
    approved_by: Optional[int]
    approved_at: Optional[datetime.datetime]
    received_at: datetime.datetime
    notes: Optional[str]

    class Config:
        from_attributes = True

class ReceiptDecision(BaseModel):
    qty_accepted: int
    approval_status: Literal["approved", "rejected"]
    approved_by: int
    notes: Optional[str] = None