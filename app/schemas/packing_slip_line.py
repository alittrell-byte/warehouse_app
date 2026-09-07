from pydantic import BaseModel


class PackingSlipLineCreate(BaseModel):
    packing_slip_id: int
    product_id: int
    qty_shipped: int


class PackingSlipLineOut(BaseModel):
    id: int
    packing_slip_id: int
    product_id: int
    qty_shipped: int

    class Config:
        from_attributes = True