from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.operation import OperationCreate
from app.models.enums import OperationType


@pytest.mark.parametrize("amount", [Decimal("0"), Decimal("-0.01")])
def test_amount_rejects_non_positive(amount):
    with pytest.raises(ValidationError):
        OperationCreate(operation_type=OperationType.DEPOSIT, amount=amount)
