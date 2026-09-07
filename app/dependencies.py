from app.repositories.metadata_repository import MetadataRepository
from app.services.contract_service import ContractService
from app.services.metadata_service import MetadataService


metadata_repository = MetadataRepository()
metadata_service = MetadataService(metadata_repository)
contract_service = ContractService(metadata_service)
