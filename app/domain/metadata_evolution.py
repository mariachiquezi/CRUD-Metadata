from typing import Any

from app.domain.metadata_normalizer import data_asset_key, normalize_asset_data
from app.domain.schema_compatibility import validate_schema_compatibility
from app.domain.versioning import (
    is_major_version_upgrade,
    validate_next_contract_version,
    version_parts,
)
from app.exceptions.domain import DomainError
from app.models.metadata import MetadataCreate, MetadataUpdate
from app.validators.metadata_validator import MetadataValidator


def prepare_update(
    current: dict[str, Any], payload: MetadataUpdate, *, replace: bool = False
) -> dict[str, Any]:
    """Merge, normalize and validate a metadata evolution before persistence."""
    data = payload.model_dump(by_alias=True, exclude_unset=not replace)
    if not data:
        raise ValueError("Envie ao menos um campo para atualizar.")

    if not replace and "schema" in data:
        if not data["schema"]:
            raise ValueError("schema não pode ser nulo ou vazio.")
        names = [field["name"] for field in data["schema"]]
        if len(names) != len(set(names)):
            raise ValueError("Campo duplicado no schema.")
        fields = {field["name"]: field for field in current["schema"]}
        fields.update({field["name"]: field for field in data["schema"]})
        data["schema"] = list(fields.values())

    data = normalize_asset_data(data)
    merged = {**current, **data}
    if not replace and "quality" not in data and "freshness" in data and merged.get("quality"):
        merged["quality"] = {
            **merged["quality"],
            "freshness": {"max_delay": data["freshness"]} if data["freshness"] else None,
        }
    if not replace and "source" not in data and merged.get("source"):
        merged["source"] = {
            **merged["source"],
            "system": merged["source_system"],
            "type": merged["source_type"],
        }

    public = {key: merged.get(key) for key in MetadataCreate.model_fields if key != "schema_"}
    public["schema"] = merged.get("schema")
    validated = MetadataCreate.model_validate(public)
    MetadataValidator.validate(validated)
    merged.update(validated.model_dump(by_alias=True))

    merged["data_asset_key"] = data_asset_key(merged)
    if merged["data_asset_key"] != current["data_asset_key"]:
        raise DomainError("A identidade da tabela é imutável; cadastre outro metadado.")
    if current.get("contract_version") and merged.get("contract_version") is None:
        raise ValueError("contract_version não pode ser removida de um contrato versionado.")
    if merged.get("contract_version") is not None:
        version_parts(merged["contract_version"])
    if "contract_version" in data and data["contract_version"] != current.get("contract_version"):
        validate_next_contract_version(
            current.get("contract_version"), data["contract_version"], merged["data_asset_key"]
        )
    validate_schema_compatibility(
        current,
        merged,
        allow_type_change=is_major_version_upgrade(
            current.get("contract_version"), merged.get("contract_version")
        ),
    )
    return merged
