# app/main.py
from fastapi import FastAPI

# from app.database import Base
from app.routers import purchase_orders, receipts

# Create tables on startup — fine for now, Alembic takes over once migrations exist
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Warehouse PO Reconciliation API",
    description="Track purchase orders, receipts, and flag discrepancies.",
    version="0.1.0",
)


# app.include_router(purchase_orders.router, prefix="/purchase-orders", tags=["Purchase Orders"])
# app.include_router(receipts.router, prefix="/receipts", tags=["Receipts"])


@app.get("/health")
def health_check():
    return {"status": "ok"}