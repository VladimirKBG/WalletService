from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.operation import OperationCreate
from app.models.enums import OperationType


def test_amount_quantize_round_half_up_down():
    amount = "1.234"
    op = OperationCreate(operation_type=OperationType.DEPOSIT, amount=amount)
    assert isinstance(op.amount, Decimal)
    assert op.amount == Decimal("1.23")

    amount = "1.235"
    op = OperationCreate(operation_type=OperationType.DEPOSIT, amount=amount)
    assert op.amount == Decimal("1.24")


@pytest.mark.parametrize("amount", [Decimal("0"), Decimal("-0.01")])
def test_amount_rejects_non_positive(amount):
    with pytest.raises(ValidationError):
        OperationCreate(operation_type=OperationType.DEPOSIT, amount=amount)
