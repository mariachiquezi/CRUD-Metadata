from app.utils.contract_parser import ContractParser
from app.validators.contract_validator import ContractValidator
from app.services.metadata_service import MetadataService
from app.models.metadata import MetadataCreate


class ContractService:

    def __init__(self):
        self.metadata_service = MetadataService()

    def process(self, content: str, changed_by: str):
        contract = ContractParser.parse(content)
        ContractValidator.validate(contract)
        metadata = self._to_metadata(contract)
        metadata = MetadataCreate(**metadata)
        return self.metadata_service.create_or_update_contract(metadata, changed_by)

    def _to_metadata(self, contract):
        data = contract.contract
        asset_name = (
            data.data_asset.name
            if data.data_asset
            else data.source.table or data.name
        )
        asset_type = data.data_asset.type if data.data_asset else "table"

        return {
            "data_asset": {
                "name": asset_name,
                "type": asset_type,
            },
            "table_name": asset_name,

            "description": (
                data.data_product.description
                if data.data_product
                else None
            ),

            "domain": data.domain,

            "schema": [
                {
                    "name": field.name,
                    "type": field.type,
                    "description": field.description,
                    "nullable": field.nullable,
                    "unique": field.unique,
                }
                for field in data.schema_
            ],

            "owner_info": {
                "team": data.ownership.owner,
                "email": None,
            },

            "source_system": data.source.system,
            "source_type": data.source.type,

            "freshness": (
                data.quality.freshness.max_delay
                if data.quality and data.quality.freshness
                else None
            ),

            "quality": (
                data.quality.model_dump()
                if data.quality
                else None
            ),

            "data_product": (
                data.data_product.model_dump()
                if data.data_product
                else None
            ),

            "classification": (
                data.classification.model_dump()
                if data.classification
                else None
            ),

            "lifecycle": (
                data.lifecycle.model_dump()
                if data.lifecycle
                else None
            ),

            "contract_name": asset_name,
            "contract_version": getattr(data, "version", None),
            "tags": [],
        }