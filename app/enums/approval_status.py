from enum import Enum

class ApprovalStatus(str, Enum):
    auto = "auto"
    pending = "pending"
    approval = "approval"
    rejected = "rejected"