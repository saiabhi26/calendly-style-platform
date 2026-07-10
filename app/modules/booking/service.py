from datetime import timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.service import Service
from app.modules.booking.schemas import BookingCreate
from app.modules.slot import service as slot_service


class SlotInvalid(Exception):
    """Requested time is not a real, currently-open slot."""


class SlotUnavailable(Exception):
    """Slot was taken between our check and our insert (race)."""


def create_booking(db: Session, service: Service, data: BookingCreate) -> Booking:
    tz = ZoneInfo(service.organization.timezone)
    slot_start = data.slot_start
    if slot_start.tzinfo is None:                 # treat a naive input as org-local
        slot_start = slot_start.replace(tzinfo=tz)

    # 1. Validate: is this actually an open slot right now?
    target_date = slot_start.astimezone(tz).date()
    open_starts = {s["start"] for s in slot_service.generate_slots(db, service, target_date)}
    if slot_start not in open_starts:
        raise SlotInvalid()

    # 2. Insert — the UNIQUE constraint is the real guarantee
    booking = Booking(
        service_id=service.id,
        slot_start=slot_start,
        slot_end=slot_start + timedelta(minutes=service.duration_minutes),
        customer_name=data.customer_name,
        customer_email=data.customer_email,
        status="PENDING",
    )
    db.add(booking)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise SlotUnavailable()
    db.refresh(booking)
    return booking