from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import Principal, get_principal, require_roles
from app.db.session import get_session
from app.models.domain import AutomationPolicy, ProviderAccessPolicy
from app.schemas.automation import AutomationPolicyCreate, ProviderPolicyCreate
from app.services.audit import write_audit_event
from app.services.automation import provider_execution_mode

router = APIRouter(prefix="/v1/automation", tags=["automation"])


@router.get("/policies")
def list_policies(principal: Principal = Depends(get_principal), session: Session = Depends(get_session)):
    result = session.execute(
        select(AutomationPolicy)
        .where(AutomationPolicy.organization_id == principal.organization_id, AutomationPolicy.enabled.is_(True))
        .order_by(AutomationPolicy.priority.asc(), AutomationPolicy.created_at.asc())
    )
    return [
        {
            "id": str(policy.id),
            "scope_type": policy.scope_type,
            "scope_id": str(policy.scope_id) if policy.scope_id else None,
            "trigger_type": policy.trigger_type,
            "action_type": policy.action_type,
            "decision_mode": policy.decision_mode,
            "conditions": policy.conditions_json,
            "configuration": policy.configuration_json,
            "priority": policy.priority,
        }
        for policy in result.scalars()
    ]


@router.post("/policies", status_code=status.HTTP_201_CREATED)
def create_policy(
    body: AutomationPolicyCreate,
    principal: Principal = Depends(require_roles("owner", "admin", "producer")),
    session: Session = Depends(get_session),
):
    policy = AutomationPolicy(
        organization_id=principal.organization_id,
        scope_type=body.scope_type,
        scope_id=body.scope_id,
        trigger_type=body.trigger_type,
        action_type=body.action_type,
        decision_mode=body.decision_mode,
        conditions_json=body.conditions,
        configuration_json=body.configuration,
        priority=body.priority,
    )
    session.add(policy)
    session.flush()
    write_audit_event(
        session,
        organization_id=principal.organization_id,
        actor_subject=principal.subject,
        action="automation_policy.created",
        entity_type="automation_policy",
        entity_id=policy.id,
        payload={"trigger_type": body.trigger_type, "action_type": body.action_type, "decision_mode": body.decision_mode},
    )
    session.commit()
    return {"id": str(policy.id), "status": "created"}


@router.get("/providers")
def list_provider_policies(principal: Principal = Depends(get_principal), session: Session = Depends(get_session)):
    result = session.execute(
        select(ProviderAccessPolicy)
        .where(ProviderAccessPolicy.organization_id == principal.organization_id, ProviderAccessPolicy.enabled.is_(True))
        .order_by(ProviderAccessPolicy.provider_key.asc(), ProviderAccessPolicy.capability.asc())
    )
    return [
        {
            "id": str(policy.id),
            "provider_key": policy.provider_key,
            "capability": policy.capability,
            "billing_mode": policy.billing_mode,
            "automatic_allowed": policy.automatic_allowed,
            "execution_mode": provider_execution_mode(policy),
            "constraints": policy.constraints_json,
        }
        for policy in result.scalars()
    ]


@router.post("/providers", status_code=status.HTTP_201_CREATED)
def create_provider_policy(
    body: ProviderPolicyCreate,
    principal: Principal = Depends(require_roles("owner", "admin")),
    session: Session = Depends(get_session),
):
    existing = session.execute(
        select(ProviderAccessPolicy).where(
            ProviderAccessPolicy.organization_id == principal.organization_id,
            ProviderAccessPolicy.provider_key == body.provider_key,
            ProviderAccessPolicy.capability == body.capability,
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Provider policy already exists")

    policy = ProviderAccessPolicy(
        organization_id=principal.organization_id,
        provider_key=body.provider_key,
        capability=body.capability,
        billing_mode=body.billing_mode,
        connection_ref=body.connection_ref,
        automatic_allowed=body.automatic_allowed,
        constraints_json=body.constraints,
    )
    session.add(policy)
    session.flush()
    write_audit_event(
        session,
        organization_id=principal.organization_id,
        actor_subject=principal.subject,
        action="provider_policy.created",
        entity_type="provider_access_policy",
        entity_id=policy.id,
        payload={"provider_key": body.provider_key, "capability": body.capability, "billing_mode": body.billing_mode},
    )
    session.commit()
    return {"id": str(policy.id), "execution_mode": provider_execution_mode(policy)}
