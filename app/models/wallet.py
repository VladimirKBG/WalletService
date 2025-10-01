from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Numeric,
    func,
)

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from decimal import Decimal
from uuid import uuid4, UUID
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.db.base import Base


class Wallet(Base):
    __tablename__ = "wallets"
    __table_args__ = (
        CheckConstraint("balance >= 0", name="ck_wallets_balance_non_negative"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid4,
    )

    balance: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=False,
        default=0,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        server_onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Wallet id={self.id}, balance={self.balance}>"
