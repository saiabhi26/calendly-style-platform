from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models.service import Service
from app.modules.slot import service as slot_service
from app.modules.slot.schemas import SlotResponse

router = APIRouter(prefix="/slots", tags=["slots (public)"])


@router.get("", response_model=list[SlotResponse])
def get_slots(service_id: int, date: date, db: Session = Depends(get_db)):
    svc = db.get(Service, service_id)
    if svc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Service not found.")
    return slot_service.generate_slots(db, svc, date)