from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


ScopeType = Literal["organization", "client", "production_category", "production_type", "project"]
DecisionMode = Literal["automatic", "ask", "deny"]
BillingMode = Literal["unlimited", "credits"]


class AutomationPolicyCreate(BaseModel):
    scope_type: ScopeType
    scope_id: UUID | None = None
    trigger_type: str = Field(min_length=1, max_length=80)
    action_type: str = Field(min_length=1, max_length=80)
    decision_mode: DecisionMode = "automatic"
    conditions: dict[str, Any] = Field(default_factory=dict)
    configuration: dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=100, ge=0, le=10000)

    @model_validator(mode="after")
    def validate_scope(self):
        if self.scope_type in {"client", "project"} and self.scope_id is None:
            raise ValueError("scope_id is required for client and project scopes")
        return self


class ProviderPolicyCreate(BaseModel):
    provider_key: str = Field(min_length=1, max_length=120)
    capability: str = Field(min_length=1, max_length=80)
    billing_mode: BillingMode
    connection_ref: str | None = Field(default=None, max_length=255)
    automatic_allowed: bool = False
    constraints: dict[str, Any] = Field(default_factory=dict)


class ClipIngestCreate(BaseModel):
    original_filename: str = Field(min_length=1, max_length=512)
    source_uri: str = Field(min_length=1, max_length=2048)
    mime_type: str | None = Field(default=None, max_length=160)
    size_bytes: int | None = Field(default=None, ge=0)
    checksum_sha256: str | None = Field(default=None, pattern=r"^[a-fA-F0-9]{64}$")
    metadata: dict[str, Any] = Field(default_factory=dict)
