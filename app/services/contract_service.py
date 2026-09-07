from app.models.contract import ContractDefinition
from app.models.metadata import MetadataCreate, MetadataOut
from app.services.metadata_service import MetadataService
from app.utils.contract_parser import ContractParser


class ContractService:
    def __init__(self, metadata_service: MetadataService):
        self.metadata_service = metadata_service

    def process(self, content: str, changed_by: str) -> MetadataOut:
        contract = ContractParser.parse(content)
        return self.metadata_service.create(self._to_metadata(contract.contract), changed_by)

    @staticmethod
    def _to_metadata(contract: ContractDefinition) -> MetadataCreate:
        data = contract.model_dump(by_alias=True, exclude={"version"})
        data["contract_version"] = contract.version
        data["contract_name"] = contract.data_asset.name
        if data["description"] is None and contract.data_product is not None:
            data["description"] = contract.data_product.description
        return MetadataCreate.model_validate(data)
