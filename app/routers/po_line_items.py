from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.po_line_item import POLineItem
from app.schemas.po_line_item import POLineItemCreate, POLineItemOut

router = APIRouter()

@router.post("/", response_model=POLineItemOut)
async def create_po_line_item(po_line_item: POLineItemCreate, db: Session = Depends(get_db)):
    new_po_line_item = POLineItem(
        po_id=po_line_item.po_id,
        product_id=po_line_item.product_id,
        vendor_sku=po_line_item.vendor_sku,
        cost=po_line_item.cost,
        qty_ordered=po_line_item.qty_ordered,
        expected_delivery_date=po_line_item.expected_delivery_date,
        notes=po_line_item.notes
    )
    db.add(new_po_line_item)
    db.commit()
    db.refresh(new_po_line_item)
    return new_po_line_item