from uuid import UUID
from typing import Optional, List
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import Wallet


async def get_wallet_for_update(session: AsyncSession, wallet_id: UUID) -> Optional[Wallet]:
    stmt = select(Wallet).where(Wallet.id == wallet_id).with_for_update()
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def read_wallet(session: AsyncSession, wallet_id: UUID) -> Optional[Wallet]:
    stmt = select(Wallet).where(Wallet.id == wallet_id)
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def read_all_wallets(session: AsyncSession) -> List[Wallet]:
    stmt = select(Wallet)
    res = await session.execute(stmt)
    return list(res.scalars().all())


async def create_wallet(session: AsyncSession, initial_balance: Decimal) -> Wallet:
    initial_balance = initial_balance.quantize(Decimal("0.01"))
    wallet = Wallet()
    wallet.balance = initial_balance
    session.add(wallet)
    await session.flush()
    return wallet


async def update_wallet_balance(session: AsyncSession, wallet_id: UUID, new_balance: Decimal) -> Optional[UUID]:
    stmt = (
        update(Wallet)
        .where(wallet_id == Wallet.id)
        .values(balance=new_balance)
        .returning(Wallet.id)
    )
    res = await session.execute(stmt)
    await session.flush()
    w_id = res.scalar_one_or_none()
    return w_id


async def increment_wallet_balance(session: AsyncSession, wallet_id: UUID, amount: Decimal) -> Optional[UUID]:
    stmt = (
        update(Wallet)
        .where(Wallet.id == wallet_id)
        .values(balance=Wallet.balance + amount)
        .returning(Wallet.id)
    )
    res = await session.execute(stmt)
    await session.flush()
    w_id = res.scalar_one_or_none()
    return w_id
