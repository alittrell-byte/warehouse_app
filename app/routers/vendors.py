from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.vendor import Vendor
from app.schemas.vendor import VendorCreate, VendorOut

router = APIRouter()

@router.post("/", response_model=VendorOut)
async def create_vendor(vendor: VendorCreate, db: Session = Depends(get_db)):
    new_vendor = Vendor(name=vendor.name)
    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)
    return new_vendor