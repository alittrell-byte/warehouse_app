from pydantic import BaseModel

class VendorCreate(BaseModel):
    name: str

class VendorOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True