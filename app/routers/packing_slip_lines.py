from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.packing_slip_line import PackingSlipLine
from app.schemas.packing_slip_line import PackingSlipLineCreate, PackingSlipLineOut

router = APIRouter()


@router.post("/", response_model=PackingSlipLineOut)
def create_packing_slip_line(line: PackingSlipLineCreate, db: Session = Depends(get_db)):
    new_line = PackingSlipLine(
        packing_slip_id=line.packing_slip_id,
        product_id=line.product_id,
        qty_shipped=line.qty_shipped,
    )
    db.add(new_line)
    db.commit()
    db.refresh(new_line)
    return new_line