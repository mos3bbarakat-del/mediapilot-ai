# Security baseline

MediaPilot is intended for broadcasters, enterprises and government organizations. The baseline therefore assumes:

- OIDC/SSO authentication in non-development deployments.
- Organization-level tenant isolation in every API query.
- Role and permission checks before privileged mutations.
- TLS in transit and encryption at rest at the infrastructure layer.
- Immutable audit events for sensitive actions.
- Separate secrets from source control.
- No direct browser access to third-party provider credentials.
- Signed, time-limited media URLs when object storage is introduced.
- Private-cloud and on-premises deployment paths for restricted environments.

Development header-based identity is explicitly disabled when `MP_AUTH_MODE` is not `development`.
