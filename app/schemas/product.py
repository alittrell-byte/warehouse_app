from pydantic import BaseModel
import datetime


class ProductCreate(BaseModel):
    name: str
    internal_sku: str
    manufacturer_id: int
    category_id: int
    product_type_id: int
    brand_id: int
    family_id: int
    options: dict
    is_active: bool = True

class ProductOut(BaseModel):
    id: int
    name: str
    internal_sku: str
    manufacturer_id: int
    category_id: int
    product_type_id: int
    brand_id: int
    family_id: int
    options: dict
    is_active: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True