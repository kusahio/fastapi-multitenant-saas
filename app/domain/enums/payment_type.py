from enum import Enum

class PaymentType(str, Enum):
    CASH = "cash"
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    TRANSFER = "transfer"
    VIRTUAL_WALLET = "virtual_wallet"