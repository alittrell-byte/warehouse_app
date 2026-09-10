from enum import Enum

class InvoiceStatus(str, Enum):
    created = "created"
    receiving = "receiving"
    received = "received"
    problem = "problem"
    closed = "closed"