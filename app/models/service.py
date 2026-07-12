from decimal import Decimal
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.booking import Booking
    from app.models.availability_rule import AvailabilityRule


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)
    mode: Mapped[str] = mapped_column(String(16), default="OFFLINE", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    organization: Mapped["Organization"] = relationship(back_populates="services")

    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="service", cascade="all, delete-orphan"
    )

    availability_rules: Mapped[list["AvailabilityRule"]] = relationship(
        back_populates="service", cascade="all, delete-orphan"
    )