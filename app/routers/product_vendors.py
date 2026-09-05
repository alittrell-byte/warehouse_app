from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.product_vendor import ProductVendor
from app.schemas.product_vendor import ProductVendorCreate, ProductVendorOut

router = APIRouter()

@router.post("/", response_model=ProductVendorOut)
async def create_product_vendor(product_vendor: ProductVendorCreate, db: Session = Depends(get_db)):
    new_product_vendor = ProductVendor(
        product_id=product_vendor.product_id,
        vendor_id=product_vendor.vendor_id,
        vendor_product_id=product_vendor.vendor_product_id,
        cost=product_vendor.cost,
        msrp=product_vendor.msrp,
        map_pricing=product_vendor.map_pricing,
        lead_time_days=product_vendor.lead_time_days,
        minimum_order_qty=product_vendor.minimum_order_qty,
        pack_qty=product_vendor.pack_qty,
        is_preferred=product_vendor.is_preferred
    )
    db.add(new_product_vendor)
    db.commit()
    db.refresh(new_product_vendor)
    return new_product_vendor