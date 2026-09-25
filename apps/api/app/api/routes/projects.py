from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import Principal, get_principal, require_roles
from app.db.session import get_session
from app.models.domain import Organization, Project, ProjectSource
from app.schemas.projects import ProjectCreate, ProjectRead, ProjectSourceCreate
from app.services.audit import write_audit_event

router = APIRouter(prefix="/v1/projects", tags=["projects"])


def ensure_organization(session: Session, principal: Principal) -> None:
    organization = session.get(Organization, principal.organization_id)
    if organization is None:
        if get_settings().auth_mode != "development":
            raise HTTPException(status_code=403, detail="Organization is not provisioned")
        session.add(
            Organization(
                id=principal.organization_id,
                name="Development Organization",
                slug=f"org-{str(principal.organization_id)[:8]}",
            )
        )
        session.flush()


@router.get("", response_model=list[ProjectRead])
def list_projects(
    principal: Principal = Depends(get_principal),
    session: Session = Depends(get_session),
):
    result = session.execute(
        select(Project)
        .where(Project.organization_id == principal.organization_id)
        .order_by(Project.created_at.desc())
    )
    return list(result.scalars())


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: UUID,
    principal: Principal = Depends(get_principal),
    session: Session = Depends(get_session),
):
    project = session.get(Project, project_id)
    if project is None or project.organization_id != principal.organization_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    body: ProjectCreate,
    principal: Principal = Depends(require_roles("owner", "admin", "producer", "creative")),
    session: Session = Depends(get_session),
):
    ensure_organization(session, principal)

    if body.intake_mode == "chat":
        name = "مشروع قيد الاستخراج"
        ai_status = "pending_provider_configuration"
    else:
        name = (body.name or "").strip()
        ai_status = "not_required" if body.intake_mode == "form" else "pending_provider_configuration"

    project = Project(
        organization_id=principal.organization_id,
        name=name,
        description=body.description,
        client_name=body.client_name,
        production_category=body.production_category,
        production_type=body.production_type,
        intake_mode=body.intake_mode,
        intake_text=body.natural_language,
        ai_extraction_status=ai_status,
        created_by_subject=principal.subject,
    )
    session.add(project)
    session.flush()
    write_audit_event(
        session,
        organization_id=principal.organization_id,
        actor_subject=principal.subject,
        action="project.created",
        entity_type="project",
        entity_id=project.id,
        project_id=project.id,
        payload={"intake_mode": body.intake_mode},
    )
    session.commit()
    session.refresh(project)
    return project


@router.post("/{project_id}/sources", status_code=status.HTTP_201_CREATED)
def bind_source(
    project_id: UUID,
    body: ProjectSourceCreate,
    principal: Principal = Depends(require_roles("owner", "admin", "producer", "creative")),
    session: Session = Depends(get_session),
):
    project = session.get(Project, project_id)
    if project is None or project.organization_id != principal.organization_id:
        raise HTTPException(status_code=404, detail="Project not found")

    source = ProjectSource(
        organization_id=principal.organization_id,
        project_id=project.id,
        source_type=body.source_type,
        source_ref=body.source_ref,
        binding_mode=body.binding_mode,
        exclusive=body.exclusive,
    )
    session.add(source)
    session.flush()
    write_audit_event(
        session,
        organization_id=principal.organization_id,
        actor_subject=principal.subject,
        action="project.source_bound",
        entity_type="project_source",
        entity_id=source.id,
        project_id=project.id,
        payload={"source_type": body.source_type, "binding_mode": body.binding_mode, "exclusive": body.exclusive},
    )
    session.commit()
    return {"id": str(source.id), "status": "bound"}
