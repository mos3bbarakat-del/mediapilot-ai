from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import Principal, get_principal, require_roles
from app.db.session import get_session
from app.models.domain import MediaAsset, ProcessingJob, Project
from app.schemas.automation import ClipIngestCreate
from app.services.audit import write_audit_event
from app.services.automation import enqueue_clip_jobs

router = APIRouter(prefix="/v1/projects/{project_id}/media", tags=["media"])


def get_tenant_project(session: Session, project_id: UUID, principal: Principal) -> Project:
    project = session.get(Project, project_id)
    if project is None or project.organization_id != principal.organization_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("")
def list_media(
    project_id: UUID,
    principal: Principal = Depends(get_principal),
    session: Session = Depends(get_session),
):
    get_tenant_project(session, project_id, principal)
    result = session.execute(
        select(MediaAsset)
        .where(MediaAsset.organization_id == principal.organization_id, MediaAsset.project_id == project_id)
        .order_by(MediaAsset.created_at.desc())
    )
    return [
        {
            "id": str(asset.id),
            "original_filename": asset.original_filename,
            "source_uri": asset.source_uri,
            "media_kind": asset.media_kind,
            "mime_type": asset.mime_type,
            "size_bytes": asset.size_bytes,
            "status": asset.status,
            "metadata": asset.metadata_json,
            "created_at": asset.created_at,
        }
        for asset in result.scalars()
    ]


@router.post("/clips", status_code=status.HTTP_201_CREATED)
def ingest_clip(
    project_id: UUID,
    body: ClipIngestCreate,
    principal: Principal = Depends(require_roles("owner", "admin", "producer", "crew")),
    session: Session = Depends(get_session),
):
    project = get_tenant_project(session, project_id, principal)
    asset = MediaAsset(
        organization_id=principal.organization_id,
        project_id=project.id,
        original_filename=body.original_filename,
        source_uri=body.source_uri,
        media_kind="video",
        mime_type=body.mime_type,
        size_bytes=body.size_bytes,
        checksum_sha256=body.checksum_sha256,
        metadata_json=body.metadata,
        created_by_subject=principal.subject,
    )
    session.add(asset)
    session.flush()
    jobs = enqueue_clip_jobs(session, organization_id=principal.organization_id, project=project, asset_id=asset.id)
    write_audit_event(
        session,
        organization_id=principal.organization_id,
        actor_subject=principal.subject,
        action="media.clip_registered",
        entity_type="media_asset",
        entity_id=asset.id,
        project_id=project.id,
        payload={"original_filename": body.original_filename, "jobs_created": [job.job_type for job in jobs]},
    )
    session.commit()
    return {
        "asset_id": str(asset.id),
        "status": asset.status,
        "jobs": [
            {"id": str(job.id), "job_type": job.job_type, "status": job.status, "decision_mode": job.decision_mode}
            for job in jobs
        ],
    }


@router.get("/jobs")
def list_jobs(
    project_id: UUID,
    principal: Principal = Depends(get_principal),
    session: Session = Depends(get_session),
):
    get_tenant_project(session, project_id, principal)
    result = session.execute(
        select(ProcessingJob)
        .where(ProcessingJob.organization_id == principal.organization_id, ProcessingJob.project_id == project_id)
        .order_by(ProcessingJob.created_at.desc())
    )
    return [
        {
            "id": str(job.id),
            "asset_id": str(job.asset_id),
            "job_type": job.job_type,
            "status": job.status,
            "decision_mode": job.decision_mode,
            "blocked_reason": job.blocked_reason,
            "parameters": job.parameters_json,
        }
        for job in result.scalars()
    ]
