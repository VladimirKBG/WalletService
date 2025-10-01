from uuid import UUID
from decimal import Decimal

from fastapi import Depends

from app.db.base import DBConnectionManager
from app.models.enums import OperationType
from app.models.operation import Operation
from app.models.wallet import Wallet
import app.crud.wallet as crud_wallet
import app.crud.operation as crud_op


class WalletService:
    def __init__(self, db_connection_manager: DBConnectionManager):
        self.db_connection_manager = db_connection_manager

    async def apply_operation(
            self,
            wallet_id: UUID,
            amount: Decimal,
            op_type: OperationType,
    ) -> Operation:
        async with await self.db_connection_manager.get_session() as session:
            async with session.begin():
                wallet = await crud_wallet.get_wallet_for_update(session, wallet_id)
                if wallet is None:
                    raise UnrecognizedWalletId()
                if op_type is OperationType.WITHDRAW:
                    if wallet.balance - amount < 0:
                        raise InsufficientFundsException()
                    wallet.balance -= amount
                elif op_type is OperationType.DEPOSIT:
                    wallet.balance += amount
                else:
                    raise UnsupportedOperationException
                operation = await crud_op.create_operation(session, wallet.id, op_type, abs(amount))
                await session.flush()
                return operation

    async def get_wallet(
            self,
            wallet_id: UUID,
    ) -> Wallet:
        async with await self.db_connection_manager.get_session() as session:
            async with session.begin():
                wallet = await crud_wallet.read_wallet(session, wallet_id)
                if wallet is None:
                    raise UnrecognizedWalletId
                return wallet


class InsufficientFundsException(Exception):
    pass


class UnsupportedOperationException(Exception):
    pass


class UnrecognizedWalletId(Exception):
    pass


async def get_wallet_service(
    db_conn_manager: DBConnectionManager = Depends(DBConnectionManager),
) -> WalletService:
    return WalletService(db_connection_manager=db_conn_manager)
