from decimal import Decimal
from typing import List, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.operation import Operation
from app.models.enums import OperationType


async def create_operation(
    session: AsyncSession,
    wallet_id: UUID,
    operation_type: OperationType,
    amount: Decimal,
) -> Operation:
    op = Operation(wallet_id=wallet_id, operation_type=operation_type, amount=amount)
    session.add(op)
    return op


async def list_operations_by_wallet(
    session: AsyncSession,
    wallet_id: UUID,
    limit: int = 100,
    offset: int = 0,
) -> List[Operation]:
    stmt = (
        select(Operation)
        .where(Operation.wallet_id == wallet_id)
        .order_by(Operation.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    res = await session.execute(stmt)
    return cast(List[Operation], res.scalars().all())
