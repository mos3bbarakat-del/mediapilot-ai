import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

DB_PATH = Path(__file__).with_name("test_automation.db")
if DB_PATH.exists():
    DB_PATH.unlink()

os.environ["MP_DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["MP_AUTO_CREATE_SCHEMA"] = "true"
os.environ["MP_AUTH_MODE"] = "development"

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402


def create_project(client: TestClient) -> dict:
    response = client.post(
        "/v1/projects",
        json={
            "intake_mode": "form",
            "name": "Automation Test",
            "client_name": "Client",
            "production_category": "program",
            "production_type": "podcast",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_each_clip_creates_independent_ingest_and_policy_jobs():
    with TestClient(app) as client:
        project = create_project(client)
        policy = client.post(
            "/v1/automation/policies",
            json={
                "scope_type": "project",
                "scope_id": project["id"],
                "trigger_type": "clip.arrived",
                "action_type": "create_proxy",
                "decision_mode": "automatic",
                "configuration": {"codec": "prores_proxy"},
            },
        )
        assert policy.status_code == 201

        first = client.post(
            f"/v1/projects/{project['id']}/media/clips",
            json={"original_filename": "A001_C001.mov", "source_uri": "edge://camera-a/A001_C001.mov", "size_bytes": 1024},
        )
        second = client.post(
            f"/v1/projects/{project['id']}/media/clips",
            json={"original_filename": "A001_C002.mov", "source_uri": "edge://camera-a/A001_C002.mov", "size_bytes": 2048},
        )
        assert first.status_code == 201
        assert second.status_code == 201
        assert [job["job_type"] for job in first.json()["jobs"]] == ["ingest", "create_proxy"]
        assert [job["job_type"] for job in second.json()["jobs"]] == ["ingest", "create_proxy"]
        assert first.json()["asset_id"] != second.json()["asset_id"]


def test_ask_policy_does_not_block_safe_ingest():
    with TestClient(app) as client:
        project = create_project(client)
        client.post(
            "/v1/automation/policies",
            json={
                "scope_type": "project",
                "scope_id": project["id"],
                "trigger_type": "clip.arrived",
                "action_type": "publish_external",
                "decision_mode": "ask",
            },
        )
        response = client.post(
            f"/v1/projects/{project['id']}/media/clips",
            json={"original_filename": "clip.mov", "source_uri": "edge://clip.mov"},
        )
        assert response.status_code == 201
        jobs = {job["job_type"]: job for job in response.json()["jobs"]}
        assert jobs["ingest"]["status"] == "queued"
        assert jobs["publish_external"]["status"] == "waiting_approval"


def test_provider_billing_rule_unlimited_vs_credits():
    with TestClient(app) as client:
        unlimited = client.post(
            "/v1/automation/providers",
            json={
                "provider_key": "unlimited-video-provider",
                "capability": "video_generation",
                "billing_mode": "unlimited",
                "automatic_allowed": True,
            },
        )
        assert unlimited.status_code == 201
        assert unlimited.json()["execution_mode"] == "automatic"

        credits = client.post(
            "/v1/automation/providers",
            json={
                "provider_key": "credit-video-provider",
                "capability": "video_generation",
                "billing_mode": "credits",
                "automatic_allowed": True,
            },
        )
        assert credits.status_code == 201
        assert credits.json()["execution_mode"] == "approval_required"
