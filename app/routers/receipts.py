from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.receipt import Receipt
from app.models.packing_slip_line import PackingSlipLine
from app.schemas.receipt import ReceiptCreate, ReceiptOut, ReceiptDecision
from app.services.reconciliation import evaluate_receipt

router = APIRouter()

TOLERANCE_PCT = 0.02  # hardcoded for now -- swap for reconciliation_tolerance_policy later

# Creates a new receipt from a completed packing slip line
@router.post("/", response_model=ReceiptOut)
def create_receipt(receipt_data: ReceiptCreate, db: Session = Depends(get_db)):

    # move to crud file
    slip_line = db.get(PackingSlipLine, receipt_data.packing_slip_line_id)

    # confirm slip_line exists
    if slip_line is None:
        raise HTTPException(status_code=404, detail="packing_slip_line not found")


    qty_shipped = slip_line.qty_shipped
    qty_counted = receipt_data.qty_counted

    is_duplicate = db.query(Receipt).filter(
        Receipt.packing_slip_line_id == receipt_data.packing_slip_line_id
    ).first() is not None

    result = evaluate_receipt(qty_counted, qty_shipped, is_duplicate)

    is_overage = result["is_overage"]
    is_shortage = result["is_shortage"]
    approval_status = result["approval_status"]
    qty_accepted = result["qty_accepted"]

    new_receipt = Receipt(
        po_line_item_id=receipt_data.po_line_item_id,
        packing_slip_line_id=receipt_data.packing_slip_line_id,
        qty_counted=qty_counted,
        qty_accepted=qty_accepted,
        is_overage=is_overage,
        is_shortage=is_shortage,
        is_duplicate=is_duplicate,
        approval_status=approval_status,
        notes=receipt_data.notes,
    )
    db.add(new_receipt)
    db.commit()
    db.refresh(new_receipt)
    return new_receipt


@router.patch("/{receipt_id}", response_model=ReceiptOut)
def decide_receipt(receipt_id: int, decision: ReceiptDecision, db: Session = Depends(get_db)):
    receipt = db.get(Receipt, receipt_id)
    if receipt is None:
        raise HTTPException(status_code=404, detail="receipt not found")
    if receipt.approval_status != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"receipt is '{receipt.approval_status}', not awaiting review",
        )

    receipt.qty_accepted = decision.qty_accepted
    receipt.approval_status = decision.approval_status
    receipt.approved_by = decision.approved_by
    receipt.approved_at = func.now()
    if decision.notes:
        receipt.notes = decision.notes

    db.commit()
    db.refresh(receipt)
    return receipt