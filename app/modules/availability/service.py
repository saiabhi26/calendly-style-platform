from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.availability_rule import AvailabilityRule
from app.models.organization import Organization
from app.modules.availability.schemas import AvailabilityRuleCreate


def create_rule(db: Session, data: AvailabilityRuleCreate) -> AvailabilityRule:
    rule = AvailabilityRule(
        organization_id=data.organization_id,
        day_of_week=data.day_of_week,
        start_time=data.start_time,
        end_time=data.end_time,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def list_rules_for_org(db: Session, organization_id: int) -> list[AvailabilityRule]:
    return list(
        db.scalars(
            select(AvailabilityRule)
            .where(AvailabilityRule.organization_id == organization_id)
            .order_by(AvailabilityRule.day_of_week, AvailabilityRule.start_time)
        )
    )


def get_owned_rule(db: Session, rule_id: int, owner_id: int) -> AvailabilityRule | None:
    return db.scalar(
        select(AvailabilityRule)
        .join(Organization, AvailabilityRule.organization_id == Organization.id)
        .where(AvailabilityRule.id == rule_id, Organization.owner_id == owner_id)
    )


def delete_rule(db: Session, rule: AvailabilityRule) -> None:
    db.delete(rule)
    db.commit()