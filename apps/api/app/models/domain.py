from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Organization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "organizations"
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"
    external_subject: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(320))
    display_name: Mapped[str | None] = mapped_column(String(220))


class Membership(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "memberships"
    __table_args__ = (Index("ux_membership_org_user", "organization_id", "user_id", unique=True),)

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(40), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Client(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "clients"
    __table_args__ = (Index("ix_clients_org_name", "organization_id", "name"),)

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(220), nullable=False)
    external_ref: Mapped[str | None] = mapped_column(String(255))


class Project(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "projects"
    __table_args__ = (Index("ix_projects_org_status", "organization_id", "status"),)

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True)
    client_name: Mapped[str | None] = mapped_column(String(220))
    name: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    production_category: Mapped[str | None] = mapped_column(String(80))
    production_type: Mapped[str | None] = mapped_column(String(120))
    intake_mode: Mapped[str] = mapped_column(String(24), nullable=False, default="chat")
    intake_text: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(48), nullable=False, default="intake")
    ai_extraction_status: Mapped[str] = mapped_column(String(48), nullable=False, default="pending_provider_configuration")
    created_by_subject: Mapped[str] = mapped_column(String(255), nullable=False)


class ProjectSource(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_sources"
    __table_args__ = (Index("ix_project_sources_project_type", "project_id", "source_type"),)

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_ref: Mapped[str] = mapped_column(String(512), nullable=False)
    binding_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="explicit")
    exclusive: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class GovernanceRule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "governance_rules"
    __table_args__ = (Index("ix_rules_org_scope", "organization_id", "scope_type"),)

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    scope_type: Mapped[str] = mapped_column(String(32), nullable=False)
    scope_id: Mapped[UUID | None] = mapped_column(Uuid)
    policy_text: Mapped[str] = mapped_column(Text, nullable=False)
    enforcement: Mapped[str] = mapped_column(String(24), nullable=False, default="hard")
    priority: Mapped[int] = mapped_column(nullable=False, default=100)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class MediaAsset(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "media_assets"
    __table_args__ = (
        Index("ix_assets_org_project", "organization_id", "project_id"),
        Index("ix_assets_project_status", "project_id", "status"),
    )

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    source_uri: Mapped[str] = mapped_column(String(2048), nullable=False)
    storage_uri: Mapped[str | None] = mapped_column(String(2048))
    media_kind: Mapped[str] = mapped_column(String(32), nullable=False, default="video")
    mime_type: Mapped[str | None] = mapped_column(String(160))
    size_bytes: Mapped[int | None] = mapped_column()
    checksum_sha256: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(48), nullable=False, default="registered")
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_by_subject: Mapped[str] = mapped_column(String(255), nullable=False)


class AutomationPolicy(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "automation_policies"
    __table_args__ = (
        Index("ix_automation_policy_org_trigger", "organization_id", "trigger_type"),
        Index("ix_automation_policy_scope", "organization_id", "scope_type", "scope_id"),
    )

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    scope_type: Mapped[str] = mapped_column(String(40), nullable=False)
    scope_id: Mapped[UUID | None] = mapped_column(Uuid)
    trigger_type: Mapped[str] = mapped_column(String(80), nullable=False)
    action_type: Mapped[str] = mapped_column(String(80), nullable=False)
    decision_mode: Mapped[str] = mapped_column(String(24), nullable=False, default="automatic")
    conditions_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    configuration_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    priority: Mapped[int] = mapped_column(nullable=False, default=100)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class ProviderAccessPolicy(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "provider_access_policies"
    __table_args__ = (Index("ux_provider_policy_org_key", "organization_id", "provider_key", "capability", unique=True),)

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_key: Mapped[str] = mapped_column(String(120), nullable=False)
    capability: Mapped[str] = mapped_column(String(80), nullable=False)
    billing_mode: Mapped[str] = mapped_column(String(24), nullable=False)
    connection_ref: Mapped[str | None] = mapped_column(String(255))
    automatic_allowed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    constraints_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class ProcessingJob(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "processing_jobs"
    __table_args__ = (Index("ix_processing_jobs_asset_status", "asset_id", "status"),)

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("media_assets.id", ondelete="CASCADE"), nullable=False, index=True)
    job_type: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(48), nullable=False, default="queued")
    decision_mode: Mapped[str] = mapped_column(String(24), nullable=False, default="automatic")
    parameters_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    blocked_reason: Mapped[str | None] = mapped_column(String(255))


class AuditEvent(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "audit_events"

    organization_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[UUID | None] = mapped_column(Uuid, index=True)
    actor_subject: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_id: Mapped[UUID | None] = mapped_column(Uuid)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
