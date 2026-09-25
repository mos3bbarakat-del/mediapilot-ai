# Architecture

## Design principles

1. **Multi-tenant by default** — every business entity is scoped to an organization.
2. **Auditability** — important mutations produce immutable audit events.
3. **Automation-first** — long-running work will execute outside request/response cycles through durable workers.
4. **Provider-neutral AI** — MediaPilot owns orchestration and policy; external AI providers are adapters.
5. **Media originals are immutable** — derived proxies, edits, renders and AI outputs are separate assets.
6. **Enterprise deployment** — architecture supports public cloud, private cloud, and later on-premises deployments.

## Initial services

### Web
Next.js application for Home, Models, Projects, Project workspace, approvals and administration.

### Core API
FastAPI service for organizations, clients, projects, source bindings, rules, permissions and audit events.

### Planned services
- Automation service: durable workflows and retries.
- Media service: ingest, checksum, proxy, transcode, metadata and render jobs.
- AI orchestration service: routing to language, vision, speech, image, video, music and editing providers.
- Connector service: email, messaging, drives, NAS, stock providers, NLE integrations.
- Search/indexing service: transcript, semantic, visual and asset search.

## Data model

The first schema includes:
- Organization
- Client
- Project
- ProjectSource
- GovernanceRule
- AuditEvent

Future schema additions will include versions, approvals, scenes, shots, assets, timelines, automations and tasks.

## Deployment

GitHub Pages remains a demo-only surface. The enterprise application requires a runtime that supports server-side execution and persistent services. The web and API are therefore kept deployable independently.
