# MediaPilot AI — Enterprise Foundation

MediaPilot AI is being built as an enterprise media operations platform, not as a static prototype. This repository now contains the first production-oriented foundation for a multi-tenant application.

## Repository layout

- `apps/web` — Next.js + TypeScript web application.
- `apps/api` — FastAPI service with PostgreSQL-backed multi-tenant domain models.
- `docs` — architecture and security decisions.
- `docker-compose.yml` — local PostgreSQL and Redis services.

## Local development

1. Copy `.env.example` to `.env` and review the values.
2. Start infrastructure: `docker compose up -d`.
3. API:
   - `cd apps/api`
   - create a virtual environment
   - install the project: `pip install -e .`
   - run: `uvicorn app.main:app --reload --port 8000`
4. Web:
   - install pnpm if needed
   - from repository root: `pnpm install`
   - run: `pnpm dev:web`

## Security note

`MP_AUTH_MODE=development` exists only for local work. Enterprise deployments must use OIDC/SSO with verified tokens. The API always scopes project data by organization.

## Current scope

The foundation includes organization-scoped projects, clients, source bindings, governance rules, audit events, bilingual project creation UI, health endpoints, CI configuration, and deployment-ready service boundaries. AI providers, media processing workers, connectors, and automation workers are intentionally separate services to be added behind stable interfaces rather than embedded as browser-only logic.
