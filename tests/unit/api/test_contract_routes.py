from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config.settings import settings
from app.models.metadata import MetadataOut
from app.routes import contract_routes
from app.services.contract_service import ContractService
from app.services.metadata_service import MetadataService
from tests.support.fakes import FakeRepository


def auth_header(role="editor"):
    token = jwt.encode(
        {"sub": role, "role": role, "exp": datetime.now(UTC) + timedelta(minutes=5)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return {"Authorization": f"Bearer {token}"}


def make_app(service):
    # fastapi exclusiva para teste
    app = FastAPI()
    app.dependency_overrides[contract_routes.get_contract_service] = lambda: service
    app.include_router(contract_routes.router)
    return app


class FakeService:  # -> OK
    def process(self, content, username):
        now = datetime.now(UTC)
        return MetadataOut(
            id=str(uuid4()),
            data_asset={"name": content, "type": "table"},
            domain="test",
            ownership={"owner": "test"},
            source={"system": "test", "type": "file"},
            schema=[{"name": "id", "type": "string"}],
            created_at=now,
            updated_at=now,
        )


class FailingService:  # -> NO OK
    def process(self, content, username):
        raise ValueError("duplicate contract")


def test_bulk_upload_returns_one_result_per_file():
    app = make_app(FakeService())

    response = TestClient(app).post(
        "/contracts/bulk",
        headers=auth_header(),
        files=[
            ("files", ("orders.yaml", b"orders", "application/yaml")),
            ("files", ("payments.yaml", b"payments", "application/yaml")),
        ],
    )

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert all(item["status"] == "success" for item in response.json()["items"])


def test_bulk_upload_returns_multi_status_when_a_file_fails():
    app = make_app(FailingService())

    response = TestClient(app).post(
        "/contracts/bulk",
        headers=auth_header(),
        files=[("files", ("customer.yaml", b"customer", "application/yaml"))],
    )

    # 207 pq temos múltiplos resultados, mesmo que seja apenas um arquivo
    assert response.status_code == 207
    assert response.json()["items"][0]["status_code"] == 422


def test_bulk_upload_persists_contract_with_repository_write_flow():
    app = make_app(ContractService(MetadataService(FakeRepository())))
    content = b"""
    contract:
      version: 1.0.0
      data_asset:
        name: customer
        type: table
      domain: commerce
      schema:
        - name: customer_id
          type: string
          nullable: false
      ownership:
        owner: crm
      source:
        system: warehouse
        type: database
    """

    response = TestClient(app).post(
        "/contracts/bulk",
        headers=auth_header(),
        files=[("files", ("customer.yaml", content, "application/yaml"))],
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["status"] == "success"
    assert response.json()["items"][0]["metadata"]["data_asset"]["name"] == "customer"


def test_viewer_cannot_upload_contracts():
    app = make_app(FakeService())

    response = TestClient(app).post(
        "/contracts/bulk",
        headers=auth_header("viewer"),
        files=[("files", ("orders.yaml", b"orders", "application/yaml"))],
    )

    # viewer nao pode fazer post
    assert response.status_code == 403
