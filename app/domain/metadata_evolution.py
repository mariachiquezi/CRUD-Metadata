from typing import Any

from app.domain.metadata_identity import DataAssetIdentity
from app.domain.schema_compatibility import SchemaCompatibilityPolicy
from app.domain.versioning import ContractVersionPolicy
from app.exceptions.domain import DomainError
from app.models.metadata import MetadataCreate, MetadataUpdate
from app.validators.metadata_validator import MetadataValidator


class MetadataEvolutionService:
    """Prepara e valida uma evolução de metadado antes da persistência."""

    def __init__(
        self,
        version_policy: ContractVersionPolicy | None = None,
        schema_policy: SchemaCompatibilityPolicy | None = None,
    ):
        self.version_policy = version_policy or ContractVersionPolicy()
        self.schema_policy = schema_policy or SchemaCompatibilityPolicy()

    def prepare_update(
        self, current: dict[str, Any], payload: MetadataUpdate, *, replace: bool = False
    ) -> dict[str, Any]:
        """Combina os dados oficiais e valida a evolução antes de salvar."""
        data = self._extract_payload(payload, replace)
        data = self._merge_partial_schema(current, data, replace)
        merged = self._merge_data(current, data)
        merged = self._validate_candidate(merged)
        self._validate_identity(current, merged)
        self._validate_contract_version(current, data, merged)
        self._validate_schema(current, merged)
        return merged

    @staticmethod
    def _extract_payload(payload: MetadataUpdate, replace: bool) -> dict[str, Any]:
        data = payload.model_dump(by_alias=True, exclude_unset=not replace)
        if not data:
            raise ValueError("Envie ao menos um campo para atualizar.")
        return data

    @staticmethod
    def _merge_partial_schema(
        current: dict[str, Any], data: dict[str, Any], replace: bool
    ) -> dict[str, Any]:
        if replace or "schema" not in data:
            return data
        if not data["schema"]:
            raise ValueError("schema não pode ser nulo ou vazio.")

        names = [field["name"] for field in data["schema"]]
        if len(names) != len(set(names)):
            raise ValueError("Campo duplicado no schema.")

        fields = {field["name"]: field for field in current["schema"]}
        fields.update({field["name"]: field for field in data["schema"]})
        data["schema"] = list(fields.values())
        return data

    @staticmethod
    def _merge_data(current: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
        """Combina o estado atual com os campos oficiais enviados."""
        return {**current, **data}

    @staticmethod
    def _validate_candidate(merged: dict[str, Any]) -> dict[str, Any]:
        public = {key: merged.get(key) for key in MetadataCreate.model_fields if key != "schema_"}
        public["schema"] = merged.get("schema")
        validated = MetadataCreate.model_validate(public)
        MetadataValidator.validate(validated)
        merged.update(validated.model_dump(by_alias=True))
        return merged

    @staticmethod
    def _validate_identity(current: dict[str, Any], merged: dict[str, Any]) -> None:
        merged["data_asset_key"] = DataAssetIdentity.from_document(merged).key
        if merged["data_asset_key"] != current["data_asset_key"]:
            raise DomainError("A identidade da tabela é imutável; cadastre outro metadado.")

    def _validate_contract_version(
        self,
        current: dict[str, Any],
        data: dict[str, Any],
        merged: dict[str, Any],
    ) -> None:
        if current.get("contract_version") and merged.get("contract_version") is None:
            raise ValueError("contract_version não pode ser removida de um contrato versionado.")
        if merged.get("contract_version") is not None:
            self.version_policy.parse(merged["contract_version"])
        if "contract_version" in data and data["contract_version"] != current.get(
            "contract_version"
        ):
            self.version_policy.validate_next(
                current.get("contract_version"),
                data["contract_version"],
                merged["data_asset_key"],
            )

    def _validate_schema(self, current: dict[str, Any], merged: dict[str, Any]) -> None:
        self.schema_policy.validate(
            current,
            merged,
            allow_type_change=self.version_policy.is_major_upgrade(
                current.get("contract_version"), merged.get("contract_version")
            ),
        )
