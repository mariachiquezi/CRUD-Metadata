import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError, PyMongoError
from starlette.concurrency import run_in_threadpool

from app.auth.security import get_current_user, require_roles
from app.config.settings import MAX_BULK_FILES, MAX_FILE_SIZE
from app.dependencies import contract_service
from app.exceptions.domain import DomainError
from app.models.contract import ContractBulkResponse

router = APIRouter(prefix="/contracts", tags=["contracts"])
service = contract_service
logger = logging.getLogger("metadata_catalog")


def get_contract_service():
    return service


async def read_contract(file: UploadFile) -> str:
    try:
        content = await file.read(MAX_FILE_SIZE + 1)
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Arquivo excede o limite de 5 MB.")
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError as error:
            raise HTTPException(status_code=422, detail="O arquivo deve usar UTF-8.") from error
    finally:
        await file.close()


@router.post(
    "/bulk",
    response_model=ContractBulkResponse,
    responses={
        207: {
            "model": ContractBulkResponse,
            "description": "Processamento parcial: pelo menos um arquivo falhou.",
        },
    },
    dependencies=[Depends(require_roles("admin", "editor"))],
)
async def upload_contracts(
    response: Response,
    files: Annotated[list[UploadFile], File()],
    current_user: Annotated[dict, Depends(get_current_user)],
    contract_processor: Annotated[Any, Depends(get_contract_service)],
):
    if not files or len(files) > MAX_BULK_FILES:
        for file in files:
            await file.close()
        raise HTTPException(
            status_code=422, detail=f"Envie entre 1 e {MAX_BULK_FILES} contratos por lote."
        )
    results = []
    for file in files:
        try:
            content = await read_contract(file)
            metadata = await run_in_threadpool(
                contract_processor.process, content, current_user["username"]
            )
            results.append(
                {
                    "filename": file.filename,
                    "status": "success",
                    "status_code": 201,
                    "metadata": metadata,
                }
            )
            continue
        except HTTPException as error:
            code, detail = error.status_code, error.detail
        except (DomainError, DuplicateKeyError):
            code, detail = 409, "Conflito de identidade, versão ou compatibilidade de schema."
        except (ValidationError, ValueError) as error:
            code, detail = 422, str(error)
        except PyMongoError:
            logger.exception("contract_database_error")
            code, detail = 503, "Banco de dados temporariamente indisponível."
        except Exception:
            logger.exception("contract_processing_error")
            code, detail = 500, "Erro interno ao processar contrato."
        results.append(
            {"filename": file.filename, "status": "error", "status_code": code, "detail": detail}
        )
    if any(item["status"] == "error" for item in results):
        response.status_code = 207
    return {"items": results, "total": len(results)}
