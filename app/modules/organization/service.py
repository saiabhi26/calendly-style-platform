from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.modules.organization.schemas import OrganizationCreate, OrganizationUpdate


def get_by_slug(db: Session, slug: str) -> Organization | None:
    return db.scalar(select(Organization).where(Organization.slug == slug))


def create_organization(db: Session, owner_id: int, data: OrganizationCreate) -> Organization:
    org = Organization(
        owner_id=owner_id,
        name=data.name,
        slug=data.slug,
        timezone=data.timezone,
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def list_organizations(db: Session, owner_id: int) -> list[Organization]:
    return list(db.scalars(select(Organization).where(Organization.owner_id == owner_id)))


def get_owned_organization(db: Session, org_id: int, owner_id: int) -> Organization | None:
    return db.scalar(
        select(Organization).where(
            Organization.id == org_id,
            Organization.owner_id == owner_id,
        )
    )


def update_organization(db: Session, org: Organization, data: OrganizationUpdate) -> Organization:
    if data.name is not None:
        org.name = data.name
    if data.timezone is not None:
        org.timezone = data.timezone
    db.commit()
    db.refresh(org)
    return org


def delete_organization(db: Session, org: Organization) -> None:
    db.delete(org)
    db.commit()