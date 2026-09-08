from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.auth.security import require_roles
from app.config.settings import settings
from app.routes.auth_routes import router


def test_login_returns_token_for_valid_user():
    app = FastAPI()
    app.include_router(router)

    response = TestClient(app).post(
        "/auth/login", json={"username": "admin", "password": "admin123"}
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_rejects_invalid_password():
    app = FastAPI()
    app.include_router(router)

    response = TestClient(app).post("/auth/login", json={"username": "admin", "password": "teste"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Usuario ou senha invalidos."


def test_viewer_is_forbidden_from_editor_operation():
    app = FastAPI()

    @app.get("/editor-only", dependencies=[Depends(require_roles("editor"))])
    def editor_only():
        return {"ok": True}

    token = jwt.encode(
        {"sub": "viewer", "role": "viewer", "exp": datetime.now(UTC) + timedelta(minutes=5)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    response = TestClient(app).get("/editor-only", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Usuario sem permissao para esta operacao."
