from collections.abc import Callable
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.users import TEST_USERS
from app.config.settings import settings

bearer_scheme = HTTPBearer(auto_error=False)


def authenticate_user(username: str, password: str) -> dict[str, str] | None:
    user = TEST_USERS.get(username)
    if user is None or user["password"] != password:
        return None
    return {"username": username, "role": user["role"]}


def create_access_token(user: dict[str, str]) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": user["username"], "role": user["role"], "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, str]:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticacao necessaria. Por favor, forneca um token de acesso valido.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "sub", "role"]},
        )
        username = payload.get("sub")
        role = payload.get("role")
        if not isinstance(username, str) or not isinstance(role, str):
            raise credentials_exception
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise credentials_exception from None

    return {"username": username, "role": role}


def require_roles(*allowed_roles: str) -> Callable:
    def role_dependency(user: dict[str, str] = Depends(get_current_user)):
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario sem permissao para esta operacao.",
            )
        return user

    return role_dependency
