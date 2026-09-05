from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError


def register_exception_handlers(app: FastAPI) -> None:
    def format_validation_errors(errors) -> str:
        messages = []
        for error in errors:
            location = ".".join(str(part) for part in error["loc"])
            message = error["msg"]
            if error["type"] == "value_error" and error.get("ctx", {}).get("error"):
                message = str(error["ctx"]["error"])
            messages.append(f"{location}: {message}")
        return "; ".join(messages)

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"detail": format_validation_errors(exc.errors())},
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        missing_fields = [
            ".".join(str(part) for part in error["loc"])
            for error in exc.errors()
            if error["type"] == "missing"
        ]

        if missing_fields:
            detail = "Campo(s) obrigatorio(s) ausente(s): " + ", ".join(missing_fields)
        else:
            detail = format_validation_errors(exc.errors())

        return JSONResponse(status_code=422, content={"detail": detail})

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DuplicateKeyError)
    async def duplicate_key_exception_handler(
        request: Request, exc: DuplicateKeyError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"detail": "Já existe um contrato com esse nome e versão."},
        )
