from fastapi import FastAPI
from pymongo.errors import DuplicateKeyError

from app.exceptions.handlers import register_exception_handlers


def test_register_exception_handlers():
    app = FastAPI()

    register_exception_handlers(app)

    assert DuplicateKeyError in app.exception_handlers
    assert ValueError in app.exception_handlers
