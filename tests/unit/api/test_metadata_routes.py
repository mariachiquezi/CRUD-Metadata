from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config.settings import settings
from app.models.metadata import MetadataOut
from app.routes import metadata_routes


def make_app(service):
    app = FastAPI()
    app.dependency_overrides[metadata_routes.get_metadata_service] = lambda: service
    app.include_router(metadata_routes.router)
    return app


def auth_header(role="admin"):
    token = jwt.encode(
        {"sub": role, "role": role, "exp": datetime.now(UTC) + timedelta(minutes=5)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return {"Authorization": f"Bearer {token}"}


class FakeService:
    def create(self, payload, username):
        return MetadataOut(
            id=str(uuid4()),
            table_name="orders",
            ownership={"owner": "commerce"},
            schema=[{"name": "order_id", "type": "string"}],
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )


def test_metadata_list_requires_authentication():
    # acesso sem token
    response = TestClient(make_app(FakeService())).get("/metadata")

    assert response.status_code == 401


def test_viewer_cannot_create_metadata():
    response = TestClient(make_app(FakeService())).post(
        "/metadata",
        headers=auth_header("viewer"),
        json={"table_name": "orders", "ownership": {"owner": "commerce"}},
    )

    assert response.status_code == 403
    
def test_editor_cannot_delete_metadata():
    response = TestClient(make_app(FakeService())).delete(
        "/metadata/123",
        headers=auth_header("editor"),
    )

    assert response.status_code == 403
