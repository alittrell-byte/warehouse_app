from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.packing_slip import PackingSlip
from app.models.packing_slip_line import PackingSlipLine
from app.schemas.packing_slip import PackingSlipCreate, PackingSlipOut

router = APIRouter()


@router.post("/", response_model=PackingSlipOut)
def create_packing_slip(packing_slip: PackingSlipCreate, db: Session = Depends(get_db)):
    new_slip = PackingSlip(
        po_id=packing_slip.po_id,
        vendor_packing_slip_number=packing_slip.vendor_packing_slip_number,
        tracking_number=packing_slip.tracking_number,
        received_date=packing_slip.received_date,
        notes=packing_slip.notes,
    )
    db.add(new_slip)
    db.flush()  # assigns new_slip.id before commit, same pattern as purchase_orders.py

    for line in packing_slip.lines:
        db.add(PackingSlipLine(
            packing_slip_id=new_slip.id,
            product_id=line.product_id,
            qty_shipped=line.qty_shipped,
        ))

    db.commit()
    db.refresh(new_slip)
    return new_slip