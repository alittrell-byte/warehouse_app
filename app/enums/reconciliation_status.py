from enum import Enum

class ReconciliationStatus(str, Enum):
    pending  = "pending"
    matched  = "matched"
    overage  = "overage"
    shortage = "shortage"
    price_mismatch = "price_mismatch"
    resolved = "resolved"