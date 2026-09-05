from enum import Enum

class POStatus(str, Enum):
    created = "created"
    sent = "sent"
    receiving = "receiving"
    received  = "received"
    problem  = "problem"
    closed = "closed"