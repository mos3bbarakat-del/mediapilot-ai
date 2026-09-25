from functools import lru_cache
from uuid import UUID

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MP_", env_file=".env", extra="ignore")

    env: str = "development"
    database_url: str = "sqlite:///./mediapilot.db"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:3000"
    auto_create_schema: bool = True

    auth_mode: str = "development"
    dev_organization_id: UUID = UUID("11111111-1111-4111-8111-111111111111")
    dev_subject: str = "local-admin"

    oidc_issuer: str | None = None
    oidc_audience: str | None = None
    oidc_jwks_url: str | None = None
    oidc_organization_claim: str = "org_id"
    oidc_roles_claim: str = "roles"
    oidc_algorithm: str = "RS256"

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
