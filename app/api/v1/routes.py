from uuid import UUID
from typing import Annotated, List
from decimal import  Decimal

from fastapi import APIRouter, status, Depends, HTTPException

from app.schemas.operation import OperationRead, OperationCreate
from app.schemas.wallet import WalletRead, WalletCreate
from app.models.enums import OperationType
from app.services.wallet_service import (
    WalletService,
    get_wallet_service,
    InsufficientFundsException,
    UnsupportedOperationException,
    UnrecognizedWalletId,
    WalletAlreadyExistException,
)


router = APIRouter(prefix="/api/v1", tags=["wallet_service"])


@router.post(
    "/wallets/{wallet_id}/operation",
    response_model=OperationRead,
    status_code=status.HTTP_201_CREATED,
    summary=f"Apply operation ({OperationType}) to wallet.",
)
async def apply_operation(
        wallet_id: UUID,
        op: OperationCreate,
        service: Annotated[WalletService, Depends(get_wallet_service)]
) -> OperationRead:
    try:
        operation = await service.apply_operation(wallet_id, op.amount, op.operation_type)
    except InsufficientFundsException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds.")
    except UnsupportedOperationException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported operation type {op.operation_type}"
        )
    except UnrecognizedWalletId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Wallet with id={wallet_id} not found.")
    else:
        return OperationRead.model_validate(operation)


@router.get(
    "/wallets/{wallet_id}/operation",
    response_model=List[OperationRead],
    status_code=status.HTTP_200_OK,
    summary=f"Get all operations of specified wallet.",
)
async def apply_operation(
        wallet_id: UUID,
        service: Annotated[WalletService, Depends(get_wallet_service)]
) -> List[OperationRead]:
    try:
        ops = await service.get_all_operations_by_wallet_id(wallet_id)
    except UnrecognizedWalletId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Wallet's root not found.")
    else:
        return [OperationRead.model_validate(op) for op in ops]


@router.get(
    "/wallets/{wallet_id}",
    response_model=WalletRead,
    status_code=status.HTTP_200_OK,
    summary="Return wallet's balance and metadata."
)
async def get_wallet(
        wallet_id: UUID,
        service: Annotated[WalletService, Depends(get_wallet_service)]
) -> WalletRead:
    try:
        wallet = await service.get_wallet(wallet_id)
    except UnrecognizedWalletId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Wallet with id={wallet_id} not found.")
    else:
        return WalletRead.model_validate(wallet)


@router.get(
    "/wallets",
    response_model=List[WalletRead],
    status_code=status.HTTP_200_OK,
    summary="Return wallets."
)
async def get_wallets(
        service: Annotated[WalletService, Depends(get_wallet_service)]
) -> List[WalletRead]:
    try:
        wallets = await service.get_all_wallets()
    except UnrecognizedWalletId:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Wallet's root not found.")
    else:
        return [WalletRead.model_validate(w) for w in wallets]


@router.post(
    "/wallets",
    response_model=WalletRead,
    status_code=status.HTTP_200_OK,
    summary="Create wallets with given id."
)
async def get_wallet_by_id(
        w: WalletCreate,
        service: Annotated[WalletService, Depends(get_wallet_service)],
) -> WalletRead:
    try:
        wallet = await service.create_wallet_by_id(w.id, w.balance)
    except WalletAlreadyExistException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Wallet with id={w.id} is already exist.")
    else:
        return WalletRead.model_validate(wallet)
