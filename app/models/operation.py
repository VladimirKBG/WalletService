from decimal import Decimal

from sqlalchemy import (
    ForeignKey,
    Enum as PG_Enum,
    Numeric,
    DateTime,
    func,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from uuid import UUID, uuid4

from app.models.enums import OperationType
from app.db.base import Base


class Operation(Base):
    __tablename__ = "operations"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_operation_amount_positive"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid4,
    )

    wallet_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("wallets.id", ondelete="CASCADE"),
        nullable=False,
    )

    operation_type: Mapped[OperationType] = mapped_column(
        PG_Enum(OperationType, name="operation_type_enum"),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=False,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    wallet = relationship(
        "Wallet",
        backref="operations",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Operation id={self.id}, type={self.operation_type}, amount={self.amount}>"

