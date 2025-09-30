from enum import Enum


class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"

    @classmethod
    def __str__(cls):
        return f"{cls.DEPOSIT} or {cls.WITHDRAW}"
