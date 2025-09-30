from uuid import UUID
from typing import Annotated
from decimal import Decimal

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import app.crud.wallet as crud_wallet
import app.crud.operation as crud_op
from app.schemas.operation import OperationRead, OperationCreate
from app.schemas.wallet import WalletRead
from app.models.enums import OperationType
from app.db.base import DBConnectionManager
from app.services.wallet_service import WalletService


router = APIRouter(prefix="/api/v1", tags=["operations", "wallets"])


@router.post(
    "/wallets/{wallet_id}/operation",
    response_model=OperationRead,
    status_code=status.HTTP_201_CREATED,
    summary=f"Apply operation ({OperationType}) to wallet.",
)
async def apply_operation(
        wallet_id: UUID,
        op: OperationCreate,
        session: Annotated[AsyncSession, Depends(DBConnectionManager.get_session)]
) -> OperationRead:
    async with session.begin():
        if op.operation_type == OperationType.WITHDRAW:
            amount = -op.amount
        elif op.operation_type == OperationType.DEPOSIT:
            amount = op.amount
        wallet = await crud_wallet.get_wallet_for_update(session, wallet_id)
        if wallet is None:
            wallet = await crud_wallet.create_wallet(session, Decimal("0.00"))
            await session.flush()
        if wallet.balance + amount < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds.")
        wallet.balance += amount
        operation = await crud_op.create_operation(session, wallet.id, op.operation_type, op.amount)
        await session.flush()
        return OperationRead.model_validate(operation)


@router.get(
    "/wallets/{wallet_id}",
    response_model=WalletRead,
    status_code=status.HTTP_200_OK,
    summary="Return wallet's balance and metadata."
)
async def get_wallet(
        wallet_id: UUID,
        session: Annotated[AsyncSession, Depends(DBConnectionManager.get_session)]
) -> WalletRead:
    async with session.begin():
        wallet = await crud_wallet.read_wallet(session, wallet_id)
        if wallet is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Wallet with id={wallet_id} not found.")
        return WalletRead.model_validate(wallet)


