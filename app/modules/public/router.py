from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models.organization import Organization
from app.models.service import Service
from app.modules.organization.schemas import OrganizationResponse
from app.modules.service.schemas import ServiceResponse

# Public, unauthenticated browse endpoints for the customer booking page.
router = APIRouter(prefix="/orgs", tags=["public"])


def _get_org_or_404(db: Session, slug: str) -> Organization:
    org = db.scalar(select(Organization).where(Organization.slug == slug))
    if org is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Organization not found.")
    return org


@router.get("/{slug}", response_model=OrganizationResponse)
def get_org(slug: str, db: Session = Depends(get_db)):
    return _get_org_or_404(db, slug)


@router.get("/{slug}/services", response_model=list[ServiceResponse])
def list_services(slug: str, db: Session = Depends(get_db)):
    org = _get_org_or_404(db, slug)
    return list(db.scalars(select(Service).where(Service.organization_id == org.id)))
