from dataclasses import dataclass
from time import monotonic
from uuid import UUID

import httpx
import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings, get_settings


@dataclass(frozen=True)
class Principal:
    subject: str
    organization_id: UUID
    roles: frozenset[str]


bearer = HTTPBearer(auto_error=False)


class JWKSCache:
    def __init__(self) -> None:
        self._value: dict | None = None
        self._expires_at = 0.0

    async def get(self, url: str) -> dict:
        if self._value is not None and monotonic() < self._expires_at:
            return self._value
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            response.raise_for_status()
            self._value = response.json()
            self._expires_at = monotonic() + 300
            return self._value


jwks_cache = JWKSCache()


async def get_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    x_organization_id: str | None = Header(default=None, alias="X-Organization-ID"),
    x_subject: str | None = Header(default=None, alias="X-Subject"),
    settings: Settings = Depends(get_settings),
) -> Principal:
    if settings.auth_mode == "development":
        try:
            organization_id = UUID(x_organization_id) if x_organization_id else settings.dev_organization_id
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid X-Organization-ID") from exc
        return Principal(
            subject=x_subject or settings.dev_subject,
            organization_id=organization_id,
            roles=frozenset({"owner", "admin", "producer"}),
        )

    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    if not all([settings.oidc_issuer, settings.oidc_audience, settings.oidc_jwks_url]):
        raise HTTPException(status_code=503, detail="OIDC is not configured")

    try:
        jwks = await jwks_cache.get(settings.oidc_jwks_url)
        header = jwt.get_unverified_header(credentials.credentials)
        if header.get("alg") != settings.oidc_algorithm:
            raise HTTPException(status_code=401, detail="Unexpected signing algorithm")
        key_data = next((candidate for candidate in jwks.get("keys", []) if candidate.get("kid") == header.get("kid")), None)
        if key_data is None:
            raise HTTPException(status_code=401, detail="Unknown signing key")
        signing_key = jwt.PyJWK.from_dict(key_data, algorithm=settings.oidc_algorithm).key
        claims = jwt.decode(
            credentials.credentials,
            signing_key,
            algorithms=[settings.oidc_algorithm],
            audience=settings.oidc_audience,
            issuer=settings.oidc_issuer,
        )
        organization_id = UUID(str(claims[settings.oidc_organization_claim]))
        subject = str(claims["sub"])
        raw_roles = claims.get(settings.oidc_roles_claim, [])
        roles = frozenset(str(role) for role in raw_roles) if isinstance(raw_roles, list) else frozenset()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid identity token") from exc

    return Principal(subject=subject, organization_id=organization_id, roles=roles)


def require_roles(*allowed_roles: str):
    async def dependency(principal: Principal = Depends(get_principal)) -> Principal:
        if principal.roles.isdisjoint(allowed_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return principal
    return dependency
