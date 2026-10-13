from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.invoice_line import InvoiceLine
from app.schemas.invoice_line import InvoiceLineCreate, InvoiceLineOut
from app.models.po_line_item import POLineItem
from app.services.reconciliation import evaluate_price

router = APIRouter()

@router.post("/", response_model=InvoiceLineOut)
async def create_invoice_line(invoice_line: InvoiceLineCreate, db: Session = Depends(get_db)):

    po_line = db.get(POLineItem, invoice_line.po_line_item_id)
    if po_line is None:
        raise HTTPException(status_code=404, detail="po_line_item not found")

    result = evaluate_price(po_line.cost, invoice_line.price)


    new_invoice_line = InvoiceLine(
        invoice_id=invoice_line.invoice_id,
        po_line_item_id=invoice_line.po_line_item_id,
        product_id=invoice_line.product_id,
        qty_invoiced=invoice_line.qty_invoiced,
        price=invoice_line.price,
        is_problem=result["is_problem"]
    )
    db.add(new_invoice_line)
    db.commit()
    db.refresh(new_invoice_line)
    return new_invoice_line