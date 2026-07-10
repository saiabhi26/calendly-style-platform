from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models.service import Service
from app.modules.booking import service as booking_service
from app.modules.booking.schemas import BookingCreate, BookingResponse

router = APIRouter(prefix="/bookings", tags=["bookings (public)"])


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(data: BookingCreate, db: Session = Depends(get_db)):
    svc = db.get(Service, data.service_id)
    if svc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Service not found.")
    try:
        return booking_service.create_booking(db, svc, data)
    except booking_service.SlotInvalid:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "That time is not an available slot.")
    except booking_service.SlotUnavailable:
        raise HTTPException(status.HTTP_409_CONFLICT, "That slot was just booked — please pick another.")