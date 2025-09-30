from enum import Enum


class OperationType(Enum, str):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"

    @classmethod
    def __str__(cls):
        return f"{cls.DEPOSIT} or {cls.WITHDRAW}"
