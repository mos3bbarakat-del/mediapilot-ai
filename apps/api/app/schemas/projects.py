from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class ProjectCreate(BaseModel):
    intake_mode: Literal["chat", "form", "hybrid"] = "chat"
    natural_language: str | None = Field(default=None, max_length=20000)
    name: str | None = Field(default=None, max_length=240)
    description: str | None = Field(default=None, max_length=20000)
    client_name: str | None = Field(default=None, max_length=220)
    production_category: str | None = Field(default=None, max_length=80)
    production_type: str | None = Field(default=None, max_length=120)

    @model_validator(mode="after")
    def validate_input(self):
        if self.intake_mode == "chat" and not (self.natural_language or "").strip():
            raise ValueError("natural_language is required for chat intake")
        if self.intake_mode == "form" and not (self.name or "").strip():
            raise ValueError("name is required for form intake")
        return self


class ProjectRead(BaseModel):
    id: UUID
    name: str
    description: str | None
    client_name: str | None
    production_category: str | None
    production_type: str | None
    status: str
    intake_mode: str
    ai_extraction_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectSourceCreate(BaseModel):
    source_type: str = Field(max_length=50)
    source_ref: str = Field(max_length=512)
    binding_mode: Literal["explicit", "discovery"] = "explicit"
    exclusive: bool = False
