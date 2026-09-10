from pydantic import BaseModel
from decimal import Decimal

class InvoiceLineCreate(BaseModel):
    invoice_id: int
    po_line_item_id: int
    product_id: int
    qty_invoiced: int
    price: Decimal
    
class InvoiceLineOut(BaseModel):
    id: int
    invoice_id: int
    po_line_item_id: int
    product_id: int
    qty_invoiced: int
    price: Decimal
    is_problem: bool

    class Config:
        from_attributes = True