from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.purchase_order import PurchaseOrder
from app.models.po_line_item import POLineItem
from app.schemas.purchase_order import PurchaseOrderCreate, PurchaseOrderOut

router = APIRouter()

@router.post("/", response_model=PurchaseOrderOut)
async def create_purchase_order(purchase_order: PurchaseOrderCreate, db: Session = Depends(get_db)):
    new_purchase_order = PurchaseOrder(
        vendor_id=purchase_order.vendor_id,
        created_by=purchase_order.created_by,
        description=purchase_order.description,
        notes=purchase_order.notes,
        status=purchase_order.status,
        reconciliation_status=purchase_order.reconciliation_status,
        order_date=purchase_order.order_date
    )
    db.add(new_purchase_order)
    db.flush()
    for item in purchase_order.line_items:
        db.add(POLineItem(
            po_id=new_purchase_order.id,
            product_id=item.product_id,
            vendor_sku=item.vendor_sku,
            cost=item.cost,
            qty_ordered=item.qty_ordered,
            expected_delivery_date=item.expected_delivery_date,
            notes=item.notes,
        ))


    db.commit()
    db.refresh(new_purchase_order)
    return new_purchase_order