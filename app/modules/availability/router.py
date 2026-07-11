from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models.user import User
from app.modules.availability import service
from app.modules.availability.schemas import AvailabilityRuleCreate, AvailabilityRuleResponse
from app.modules.service.service import get_owned_service

router = APIRouter(prefix="/availability", tags=["availability"])


@router.post("", response_model=AvailabilityRuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(
    data: AvailabilityRuleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if get_owned_service(db, data.service_id, current_user.id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Service not found.")
    return service.create_rule(db, data)


@router.get("", response_model=list[AvailabilityRuleResponse])
def list_rules(
    service_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if get_owned_service(db, service_id, current_user.id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Service not found.")
    return service.list_rules_for_service(db, service_id)


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rule = service.get_owned_rule(db, rule_id, current_user.id)
    if rule is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Availability rule not found.")
    service.delete_rule(db, rule)
