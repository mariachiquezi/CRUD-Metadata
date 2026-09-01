from fastapi import APIRouter, UploadFile, File

from app.services.contract_service import ContractService

router = APIRouter(prefix="/contracts", tags=["contracts"])

service = ContractService()


@router.post("")
async def upload_contract(file: UploadFile = File(...)):
    content = await file.read()

    return service.process(content.decode("utf-8"))
