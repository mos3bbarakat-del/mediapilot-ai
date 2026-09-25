from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models.domain import AutomationPolicy, ProcessingJob, Project, ProviderAccessPolicy


def matching_policies(session: Session, *, organization_id: UUID, project: Project, trigger_type: str) -> list[AutomationPolicy]:
    scope_predicates = [
        AutomationPolicy.scope_type == "organization",
        and_(AutomationPolicy.scope_type == "project", AutomationPolicy.scope_id == project.id),
    ]
    if project.client_id:
        scope_predicates.append(and_(AutomationPolicy.scope_type == "client", AutomationPolicy.scope_id == project.client_id))

    result = session.execute(
        select(AutomationPolicy)
        .where(
            AutomationPolicy.organization_id == organization_id,
            AutomationPolicy.enabled.is_(True),
            AutomationPolicy.trigger_type == trigger_type,
            or_(*scope_predicates),
        )
        .order_by(AutomationPolicy.priority.asc(), AutomationPolicy.created_at.asc())
    )
    policies = list(result.scalars())

    # String scopes are evaluated explicitly because their value is stored in conditions.
    extra = session.execute(
        select(AutomationPolicy)
        .where(
            AutomationPolicy.organization_id == organization_id,
            AutomationPolicy.enabled.is_(True),
            AutomationPolicy.trigger_type == trigger_type,
            AutomationPolicy.scope_type.in_(["production_category", "production_type"]),
        )
        .order_by(AutomationPolicy.priority.asc(), AutomationPolicy.created_at.asc())
    )
    for policy in extra.scalars():
        expected = policy.conditions_json.get("value")
        actual = project.production_category if policy.scope_type == "production_category" else project.production_type
        if expected and actual == expected:
            policies.append(policy)

    return policies


def enqueue_clip_jobs(session: Session, *, organization_id: UUID, project: Project, asset_id: UUID) -> list[ProcessingJob]:
    jobs: list[ProcessingJob] = []

    # Registration of each individual clip always creates an ingest job. Derived processing
    # only exists when the organization/project has an explicit automation policy.
    ingest = ProcessingJob(
        organization_id=organization_id,
        project_id=project.id,
        asset_id=asset_id,
        job_type="ingest",
        decision_mode="automatic",
        status="queued",
        parameters_json={"preserve_original": True},
    )
    session.add(ingest)
    jobs.append(ingest)

    for policy in matching_policies(session, organization_id=organization_id, project=project, trigger_type="clip.arrived"):
        status = "waiting_approval" if policy.decision_mode == "ask" else ("suppressed" if policy.decision_mode == "deny" else "queued")
        job = ProcessingJob(
            organization_id=organization_id,
            project_id=project.id,
            asset_id=asset_id,
            job_type=policy.action_type,
            decision_mode=policy.decision_mode,
            status=status,
            parameters_json=policy.configuration_json,
            blocked_reason="policy_requires_approval" if policy.decision_mode == "ask" else ("policy_denied" if policy.decision_mode == "deny" else None),
        )
        session.add(job)
        jobs.append(job)
    return jobs


def provider_execution_mode(policy: ProviderAccessPolicy) -> str:
    # Product rule: unlimited + explicitly authorized can run automatically.
    # Credits are never spent automatically; they require approval.
    if not policy.enabled:
        return "unavailable"
    if policy.billing_mode == "credits":
        return "approval_required"
    if policy.billing_mode == "unlimited" and policy.automatic_allowed:
        return "automatic"
    return "approval_required"
