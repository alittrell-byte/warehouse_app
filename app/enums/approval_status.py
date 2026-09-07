from enum import Enum

class ApprovalStatus(str, Enum):
    auto = "auto"
    pending = "pending"
    approved = "approved"
    rejected = "rejected"