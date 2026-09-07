from app.models.metadata import MetadataCreate
from app.validators.schema_validator import validate_schema


class MetadataValidator:
    @staticmethod
    def validate(metadata: MetadataCreate) -> None:
        if not metadata.table_name:
            raise ValueError("Campo 'table_name' é obrigatório.")
        if metadata.owner_info is None:
            raise ValueError("Campo 'owner_info.team' é obrigatório.")
        validate_schema(metadata.schema_, metadata.quality)
