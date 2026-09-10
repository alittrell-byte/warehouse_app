from pydantic import BaseModel
import datetime
from decimal import Decimal
from typing import Optional
from app.enums.invoice_status import InvoiceStatus


class InvoiceCreate(BaseModel):
    vendor_id: int
    vendor_invoice_number: str
    invoice_date: datetime.date
    ship_start_date: datetime.date
    status: InvoiceStatus = "created"
    payment_due_date: datetime.date
    sub_total: Decimal
    tax_total: Decimal
    shipping_total: Decimal
    notes: str
    

class InvoiceOut(BaseModel):
    id: int
    vendor_id: int
    vendor_invoice_number: str
    invoice_date: datetime.date
    ship_start_date: datetime.date
    status: InvoiceStatus
    payment_due_date: datetime.date
    sub_total: Decimal
    tax_total: Decimal
    shipping_total: Decimal
    notes: str

    class Config:
        from_attributes = True