from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.service import Service
from app.models.organization import Organization
from app.modules.service.schemas import ServiceCreate, ServiceUpdate


def create_service(db: Session, data: ServiceCreate) -> Service:
    svc = Service(
        organization_id=data.organization_id,
        title=data.title,
        duration_minutes=data.duration_minutes,
        price=data.price,
        mode=data.mode,
    )
    db.add(svc)
    db.commit()
    db.refresh(svc)
    return svc


def list_services_for_org(db: Session, organization_id: int) -> list[Service]:
    return list(db.scalars(select(Service).where(Service.organization_id == organization_id)))


def get_owned_service(db: Session, service_id: int, owner_id: int) -> Service | None:
    return db.scalar(
        select(Service)
        .join(Organization, Service.organization_id == Organization.id)
        .where(Service.id == service_id, Organization.owner_id == owner_id)
    )


def update_service(db: Session, svc: Service, data: ServiceUpdate) -> Service:
    if data.title is not None:
        svc.title = data.title
    if data.duration_minutes is not None:
        svc.duration_minutes = data.duration_minutes
    if data.price is not None:
        svc.price = data.price
    if data.mode is not None:
        svc.mode = data.mode
    db.commit()
    db.refresh(svc)
    return svc


def delete_service(db: Session, svc: Service) -> None:
    db.delete(svc)
    db.commit()