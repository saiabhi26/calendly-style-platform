from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models.user import User
from app.modules.service import service
from app.modules.service.schemas import ServiceCreate, ServiceUpdate, ServiceResponse
from app.modules.organization import service as org_service

router = APIRouter(prefix="/services", tags=["services"])


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(
    data: ServiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if org_service.get_owned_organization(db, data.organization_id, current_user.id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Organization not found.")
    return service.create_service(db, data)


@router.get("", response_model=list[ServiceResponse])
def list_services(
    organization_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if org_service.get_owned_organization(db, organization_id, current_user.id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Organization not found.")
    return service.list_services_for_org(db, organization_id)


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = service.get_owned_service(db, service_id, current_user.id)
    if svc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Service not found.")
    return svc


@router.patch("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    data: ServiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = service.get_owned_service(db, service_id, current_user.id)
    if svc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Service not found.")
    return service.update_service(db, svc, data)


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = service.get_owned_service(db, service_id, current_user.id)
    if svc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Service not found.")
    service.delete_service(db, svc)