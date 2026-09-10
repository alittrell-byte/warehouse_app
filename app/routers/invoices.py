from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceCreate, InvoiceOut

router = APIRouter()

@router.post("/", response_model=InvoiceOut)
async def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    new_invoice = Invoice(
        vendor_id=invoice.vendor_id,
        vendor_invoice_number=invoice.vendor_invoice_number,
        invoice_date=invoice.invoice_date,
        ship_start_date=invoice.ship_start_date,
        status=invoice.status,
        payment_due_date=invoice.payment_due_date,
        sub_total=invoice.sub_total,
        tax_total=invoice.tax_total,
        shipping_total=invoice.shipping_total,
        notes=invoice.notes
    )
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)
    return new_invoice