from app.models.metadata import MetadataCreate
from app.validators.schema_validator import validate_schema


class MetadataValidator:
    @staticmethod
    def validate(metadata: MetadataCreate) -> None:
        if not metadata.data_asset.name:
            raise ValueError("Campo 'data_asset.name' é obrigatório.")
        if not metadata.domain:
            raise ValueError("Campo 'domain' é obrigatório.")
        if metadata.ownership is None:
            raise ValueError("Campo 'ownership.owner' é obrigatório.")
        if metadata.source is None:
            raise ValueError("Campo 'source' é obrigatório.")
        validate_schema(metadata.schema_, metadata.quality)
