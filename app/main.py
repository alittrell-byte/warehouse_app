# app/main.py
from fastapi import FastAPI

# from app.database import Base
from app.routers import purchase_orders, vendors, po_line_items, products, product_vendors, receipts, packing_slips, packing_slip_lines

# Create tables on startup — fine for now, Alembic takes over once migrations exist
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Warehouse PO Reconciliation API",
    description="Track purchase orders, receipts, and flag discrepancies.",
    version="0.1.0",
)

app.include_router(vendors.router, prefix="/vendors", tags=["Vendors"])
app.include_router(purchase_orders.router, prefix="/purchase-orders", tags=["Purchase Orders"])
app.include_router(po_line_items.router, prefix="/po-line-items", tags=["PO Line Items"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(product_vendors.router, prefix="/product-vendors", tags=["Product Vendors"])
app.include_router(receipts.router, prefix="/receipts", tags=["Receipts"])
app.include_router(packing_slips.router, prefix="/packing-slips", tags=["Packing Slips"])
app.include_router(packing_slip_lines.router, prefix="/packing-slip-lines", tags=["Packing Slip Lines"])


@app.get("/health")
def health_check():
    return {"status": "ok"}