from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import Principal, get_principal, require_roles
from app.db.session import get_session
from app.models.domain import GovernanceRule
from app.services.audit import write_audit_event

router = APIRouter(prefix="/v1/rules", tags=["rules"])


class RuleCreate(BaseModel):
    scope_type: str = Field(max_length=32)
    scope_id: UUID | None = None
    policy_text: str = Field(min_length=1, max_length=10000)
    enforcement: str = Field(default="hard", max_length=24)
    priority: int = 100


@router.get("")
def list_rules(principal: Principal = Depends(get_principal), session: Session = Depends(get_session)):
    result = session.execute(
        select(GovernanceRule)
        .where(GovernanceRule.organization_id == principal.organization_id, GovernanceRule.enabled.is_(True))
        .order_by(GovernanceRule.priority.asc(), GovernanceRule.created_at.asc())
    )
    return [
        {
            "id": str(rule.id),
            "scope_type": rule.scope_type,
            "scope_id": str(rule.scope_id) if rule.scope_id else None,
            "policy_text": rule.policy_text,
            "enforcement": rule.enforcement,
            "priority": rule.priority,
        }
        for rule in result.scalars()
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_rule(
    body: RuleCreate,
    principal: Principal = Depends(require_roles("owner", "admin")),
    session: Session = Depends(get_session),
):
    rule = GovernanceRule(
        organization_id=principal.organization_id,
        scope_type=body.scope_type,
        scope_id=body.scope_id,
        policy_text=body.policy_text,
        enforcement=body.enforcement,
        priority=body.priority,
    )
    session.add(rule)
    session.flush()
    write_audit_event(
        session,
        organization_id=principal.organization_id,
        actor_subject=principal.subject,
        action="governance_rule.created",
        entity_type="governance_rule",
        entity_id=rule.id,
        payload={"scope_type": body.scope_type, "scope_id": str(body.scope_id) if body.scope_id else None},
    )
    session.commit()
    return {"id": str(rule.id), "status": "created"}
