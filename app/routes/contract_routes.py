import asyncio

from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError

from app.services.contract_service import ContractService
from app.auth.security import get_current_user, require_roles
from app.config.settings import MAX_BULK_FILES, MAX_FILE_SIZE

router = APIRouter(prefix="/contracts", tags=["contracts"])

service = ContractService()



def _validation_detail(error: ValidationError) -> str:
    missing_fields = [
        ".".join(str(part) for part in item["loc"])
        for item in error.errors()
        if item["type"] == "missing"
    ]

    if missing_fields:
        return "Campo(s) obrigatorio(s) ausente(s): " + ", ".join(missing_fields)
    return "Contrato invalido. Verifique os campos enviados."


@router.post("/bulk", dependencies=[Depends(require_roles("admin", "editor"))])
async def upload_contracts(
    files: list[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user),
):
    if not files or len(files) > MAX_BULK_FILES:
        raise ValueError(f"Envie entre 1 e {MAX_BULK_FILES} contratos por lote.")

    contents = await asyncio.gather(*(file.read() for file in files))

    async def process_file(file: UploadFile, content: bytes):
        try:
            if len(content) > MAX_FILE_SIZE:
                raise ValueError("Arquivo excede o limite de 5 MB.")
            metadata = await asyncio.to_thread(
                service.process,
                content.decode("utf-8"),
                current_user["username"],
            )
            return {
                "filename": file.filename,
                "status": "success",
                "status_code": 201,
                "metadata": metadata,
            }
        except (ValidationError, RequestValidationError) as error:
            return {
                "filename": file.filename,
                "status": "error",
                "status_code": 422,
                "detail": _validation_detail(error),
            }
        except (DuplicateKeyError, ValueError) as error:
            return {
                "filename": file.filename,
                "status": "error",
                "status_code": 409,
                "detail": str(error),
            }
        except Exception as error:
            return {
                "filename": file.filename,
                "status": "error",
                "status_code": 500,
                "detail": str(error),
            }

    results = await asyncio.gather(
        *(process_file(file, content) for file, content in zip(files, contents))
    )

    return {"items": results, "total": len(results)}
