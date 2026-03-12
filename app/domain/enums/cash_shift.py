from enum import Enum

class CashShiftStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"