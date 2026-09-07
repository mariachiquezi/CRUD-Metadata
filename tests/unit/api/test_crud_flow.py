import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.security import create_access_token
from app.exceptions.handlers import register_exception_handlers
from app.routes.metadata_routes import get_metadata_service, router
from app.services.metadata_service import MetadataService
from tests.support.fakes import FakeRepository


@pytest.fixture
def client():
    # preparacao para crud de teste
    app = FastAPI()
    catalog = MetadataService(FakeRepository())
    app.dependency_overrides[get_metadata_service] = lambda: catalog
    register_exception_handlers(app)
    app.include_router(router)
    token = create_access_token({"username": "admin", "role": "admin"})
    with TestClient(app, headers={"Authorization": f"Bearer {token}"}) as client:
        yield client


def payload():
    return {
        "data_asset": {"name": "orders"},
        "domain": "commerce",
        "description": "Orders placed by customers",
        "ownership": {"owner": "commerce", "steward": "analytics"},
        "source": {"system": "shop", "type": "database", "database": "sales"},
        "schema": [{"name": "order_id", "type": "string", "nullable": False}],
        "tags": ["sales"],
    }


def test_full_crud_preserves_audit_and_nested_fields(client):
    created = client.post("/metadata", json=payload())
    assert created.status_code == 201
    item = created.json()
    path = f"/metadata/{item['id']}"
    assert item["ownership"]["steward"] == "analytics"
    assert item["source"]["database"] == "sales"
    
    assert client.get(path).json() == item
    replacement = payload()
    replacement.pop("description")
    replacement.pop("tags")
    
    updated = client.put(path, json=replacement)
    assert updated.status_code == 200, updated.text
    assert updated.json()["description"] is None
    assert updated.json()["tags"] == []
    assert updated.json()["version"] == 2
    
    patched = client.patch(path, json={"description": "Updated context"})
    assert patched.status_code == 200
    assert patched.json()["schema"] == item["schema"]
    assert patched.json()["version"] == 3
    
    assert client.get("/metadata").json()["total"] == 1
    
    assert client.delete(path).status_code == 200
    
    assert client.get(path).status_code == 404
    
    history = client.get(path + "/history").json()
    assert [entry["change_type"] for entry in history] == [
        "CREATE",
        "UPDATE",
        "UPDATE",
        "DELETE",
    ]
    assert history[0]["deleted"] is False
    assert history[-1]["deleted"] is True
    assert history[0]["source"]["database"] == "sales"
    
    assert client.delete(path).status_code == 404


def test_duplicate_create_and_identity_change_return_conflict(client):
    item = client.post("/metadata", json=payload()).json()
    assert client.post("/metadata", json=payload()).status_code == 409
    assert (
        client.patch(f"/metadata/{item['id']}", json={"table_name": "renamed"}).status_code == 409
    )


def test_put_rejects_partial_body(client):
    # PUT exige o documento completo
    item = client.post("/metadata", json=payload()).json()

    response = client.put(f"/metadata/{item['id']}", json={"description": "partial"})

    assert response.status_code == 422
