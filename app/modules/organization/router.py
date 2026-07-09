from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models.user import User
from app.modules.organization import service
from app.modules.organization.schemas import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_org(
    data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if service.get_by_slug(db, data.slug):
        raise HTTPException(status.HTTP_409_CONFLICT, "That slug is already taken.")
    return service.create_organization(db, current_user.id, data)


@router.get("", response_model=list[OrganizationResponse])
def list_orgs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.list_organizations(db, current_user.id)


@router.get("/{org_id}", response_model=OrganizationResponse)
def get_org(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org = service.get_owned_organization(db, org_id, current_user.id)
    if org is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Organization not found.")
    return org


@router.patch("/{org_id}", response_model=OrganizationResponse)
def update_org(
    org_id: int,
    data: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org = service.get_owned_organization(db, org_id, current_user.id)
    if org is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Organization not found.")
    return service.update_organization(db, org, data)


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_org(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    org = service.get_owned_organization(db, org_id, current_user.id)
    if org is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Organization not found.")
    service.delete_organization(db, org)