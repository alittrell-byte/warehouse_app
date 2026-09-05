from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductOut

router = APIRouter()

@router.post("/", response_model=ProductOut)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(
        name=product.name,
        internal_sku=product.internal_sku,
        manufacturer_id=product.manufacturer_id,
        category_id=product.category_id,
        product_type_id=product.product_type_id,
        brand_id=product.brand_id,
        family_id=product.family_id,
        options=product.options,
        is_active=product.is_active
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product