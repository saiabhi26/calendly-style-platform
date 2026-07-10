from datetime import datetime, timedelta, date as date_type, time as time_type
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.service import Service
from app.models.availability_rule import AvailabilityRule
from app.models.booking import Booking


def generate_slots(db: Session, service: Service, target_date: date_type) -> list[dict]:
    tz = ZoneInfo(service.organization.timezone)
    weekday = target_date.weekday()  # 0 = Monday … 6 = Sunday
    duration = timedelta(minutes=service.duration_minutes)
    now = datetime.now(tz)

    # 1. This org's availability windows for that weekday
    rules = db.scalars(
        select(AvailabilityRule).where(
            AvailabilityRule.organization_id == service.organization_id,
            AvailabilityRule.day_of_week == weekday,
        )
    ).all()

    # 2. Slice each window into duration-sized candidate slots
    candidates: list[tuple[datetime, datetime]] = []
    for rule in rules:
        cursor = datetime.combine(target_date, rule.start_time, tzinfo=tz)
        window_end = datetime.combine(target_date, rule.end_time, tzinfo=tz)
        while cursor + duration <= window_end:
            slot_end = cursor + duration
            if cursor > now:                       # skip slots already in the past
                candidates.append((cursor, slot_end))
            cursor += duration

    # 3. Fetch already-booked starts for this service on this date
    day_start = datetime.combine(target_date, time_type.min, tzinfo=tz)
    day_end = day_start + timedelta(days=1)
    booked = set(
        db.scalars(
            select(Booking.slot_start).where(
                Booking.service_id == service.id,
                Booking.status != "CANCELLED",
                Booking.slot_start >= day_start,
                Booking.slot_start < day_end,
            )
        ).all()
    )

    # 4. Free = candidates minus booked
    free = [(s, e) for (s, e) in candidates if s not in booked]
    free.sort()
    return [{"start": s, "end": e} for (s, e) in free]