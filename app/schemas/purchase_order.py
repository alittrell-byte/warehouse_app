from pydantic import BaseModel

from app.enums.po_status import POStatus
from app.enums.reconciliation_status import ReconciliationStatus
import datetime
from decimal import Decimal
from typing import Optional


class POLineItemNested(BaseModel):
    product_id: int
    vendor_sku: str
    cost: Decimal
    qty_ordered: int
    expected_delivery_date: datetime.date
    notes: Optional[str] = None

class PurchaseOrderCreate(BaseModel):
    vendor_id: int
    created_by: int
    description: str
    notes: str = ""
    status: POStatus = "created"
    reconciliation_status: ReconciliationStatus = "pending"
    order_date: datetime.date
    line_items: list[POLineItemNested]

class PurchaseOrderOut(BaseModel):
    id: int
    vendor_id: int
    created_by: int
    description: str
    notes: str
    status: POStatus
    reconciliation_status: ReconciliationStatus
    order_date: datetime.date
    created_at: datetime.datetime

    class Config:
        from_attributes = True