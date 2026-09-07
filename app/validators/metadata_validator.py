from app.models.metadata import MetadataCreate
from app.validators.schema_validator import validate_schema


class MetadataValidator:
    @staticmethod
    def validate(metadata: MetadataCreate) -> None:
        if not metadata.table_name:
            raise ValueError("Campo 'table_name' é obrigatório.")
        if metadata.ownership is None:
            raise ValueError("Campo 'ownership.owner' é obrigatório.")
        validate_schema(metadata.schema_, metadata.quality)
