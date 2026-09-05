from typing import TypedDict


class TestUser(TypedDict):
    password: str
    role: str


TEST_USERS: dict[str, TestUser] = {
    "admin": {"password": "admin123", "role": "admin"},
    "editor": {"password": "editor123", "role": "editor"},
    "viewer": {"password": "viewer123", "role": "viewer"},
}