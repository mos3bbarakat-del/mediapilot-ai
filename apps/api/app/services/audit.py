from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.domain import AuditEvent


def write_audit_event(
    session: Session,
    *,
    organization_id: UUID,
    actor_subject: str,
    action: str,
    entity_type: str,
    entity_id: UUID | None = None,
    project_id: UUID | None = None,
    payload: dict[str, Any] | None = None,
) -> None:
    session.add(
        AuditEvent(
            organization_id=organization_id,
            actor_subject=actor_subject,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            project_id=project_id,
            payload=payload or {},
        )
    )
