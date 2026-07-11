from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.availability_rule import AvailabilityRule
from app.models.service import Service
from app.models.organization import Organization
from app.modules.availability.schemas import AvailabilityRuleCreate


def create_rule(db: Session, data: AvailabilityRuleCreate) -> AvailabilityRule:
    rule = AvailabilityRule(
        service_id=data.service_id,
        day_of_week=data.day_of_week,
        start_time=data.start_time,
        end_time=data.end_time,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def list_rules_for_service(db: Session, service_id: int) -> list[AvailabilityRule]:
    return list(
        db.scalars(
            select(AvailabilityRule)
            .where(AvailabilityRule.service_id == service_id)
            .order_by(AvailabilityRule.day_of_week, AvailabilityRule.start_time)
        )
    )


def get_owned_rule(db: Session, rule_id: int, owner_id: int) -> AvailabilityRule | None:
    # A rule is owned if its service's org belongs to the user.
    return db.scalar(
        select(AvailabilityRule)
        .join(Service, AvailabilityRule.service_id == Service.id)
        .join(Organization, Service.organization_id == Organization.id)
        .where(AvailabilityRule.id == rule_id, Organization.owner_id == owner_id)
    )


def delete_rule(db: Session, rule: AvailabilityRule) -> None:
    db.delete(rule)
    db.commit()
