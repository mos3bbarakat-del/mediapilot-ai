import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

DB_PATH = Path(__file__).with_name("test_mediapilot.db")
if DB_PATH.exists():
    DB_PATH.unlink()

os.environ["MP_DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["MP_AUTO_CREATE_SCHEMA"] = "true"
os.environ["MP_AUTH_MODE"] = "development"

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402


def test_health_and_project_flow():
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"
        assert client.get("/v1/projects").json() == []

        created = client.post(
            "/v1/projects",
            json={
                "intake_mode": "form",
                "name": "Professional Test",
                "client_name": "Test Client",
                "production_category": "standard-video",
                "production_type": "interview",
            },
        )
        assert created.status_code == 201
        project = created.json()
        assert project["name"] == "Professional Test"

        fetched = client.get(f"/v1/projects/{project['id']}")
        assert fetched.status_code == 200
        assert fetched.json()["client_name"] == "Test Client"

        source = client.post(
            f"/v1/projects/{project['id']}/sources",
            json={
                "source_type": "email",
                "source_ref": "client@example.com",
                "binding_mode": "explicit",
                "exclusive": True,
            },
        )
        assert source.status_code == 201

        rule = client.post(
            "/v1/rules",
            json={
                "scope_type": "organization",
                "policy_text": "Do not use prohibited music.",
                "enforcement": "hard",
                "priority": 10,
            },
        )
        assert rule.status_code == 201
        assert len(client.get("/v1/rules").json()) == 1


def test_tenant_isolation():
    with TestClient(app) as client:
        other_headers = {
            "X-Organization-ID": "22222222-2222-4222-8222-222222222222",
            "X-Subject": "other-user",
        }
        response = client.get("/v1/projects", headers=other_headers)
        assert response.status_code == 200
        assert response.json() == []
