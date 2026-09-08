from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.exceptions.handlers import register_exception_handlers


def test_validation_handler_returns_serializable_detail():
    app = FastAPI()
    register_exception_handlers(app)

    class Payload(BaseModel):
        value: int

    @app.post("/payload")
    def receive_payload(payload: Payload):
        return payload

    # esperava int recebeu uma string
    response = TestClient(app).post("/payload", json={"value": "invalid"})

    assert response.status_code == 422
    assert response.json()["detail"].startswith("body.value: Input should be a valid integer")
