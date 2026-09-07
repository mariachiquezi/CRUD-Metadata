from __future__ import annotations

import builtins
from uuid import uuid4

from app.domain.metadata_evolution import prepare_update
from app.domain.metadata_normalizer import data_asset_key, normalize_asset_data
from app.domain.versioning import validate_next_contract_version, version_parts
from app.exceptions.domain import DomainError
from app.models.metadata import (
    MetadataCreate,
    MetadataOut,
    MetadataReplace,
    MetadataUpdate,
)
from app.repositories.protocols import MetadataRepositoryProtocol
from app.services.metadata_history import (
    build_history_entry,
    normalize_history,
    now_utc,
    to_response,
)
from app.validators.metadata_validator import MetadataValidator


class MetadataService:
    """Orchestrates metadata use cases through the repository abstraction."""

    def __init__(self, repository: MetadataRepositoryProtocol):
        self.repository = repository

    def create(self, payload: MetadataCreate, changed_by: str = "system") -> MetadataOut:
        data = normalize_asset_data(payload.model_dump(by_alias=True))
        MetadataValidator.validate(MetadataCreate.model_validate(data))
        data["data_asset_key"] = data_asset_key(data)
        if data.get("contract_version") is not None:
            version_parts(data["contract_version"])

        current = self.repository.get_by_data_asset_key(data["data_asset_key"])
        if current is not None:
            if not data.get("contract_version"):
                raise DomainError("Já existe um metadado para essa tabela.")
            validate_next_contract_version(
                current.get("contract_version"),
                data["contract_version"],
                data["data_asset_key"],
            )
            data.pop("data_asset_key")
            result = self.update(current["_id"], MetadataUpdate(**data), changed_by, replace=True)
            if result is None:
                raise DomainError(
                    "Metadado alterado simultaneamente. Consulte novamente e tente outra vez."
                )
            return result

        now = now_utc()
        data.update(_id=str(uuid4()), version=1, created_at=now, updated_at=now)
        document = self.repository.create(data)
        self.repository.create_history_entry(build_history_entry(data, changed_by, "CREATE"))
        return to_response(document)

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        domain: str | None = None,
        owner: str | None = None,
        table_name: str | None = None,
    ) -> tuple[builtins.list[MetadataOut], int]:
        filters = {
            key: value
            for key, value in {
                "domain": domain,
                "ownership.owner": owner,
                "table_name": table_name,
            }.items()
            if value is not None
        }
        documents = self.repository.list(filters, (page - 1) * page_size, page_size)
        return [to_response(document) for document in documents], self.repository.count(filters)

    def get_by_id(self, metadata_id: str) -> MetadataOut | None:
        document = self.repository.get_by_id(metadata_id)
        return to_response(document) if document is not None else None

    def replace(
        self, metadata_id: str, payload: MetadataReplace, changed_by: str
    ) -> MetadataOut | None:
        return self.update(
            metadata_id,
            MetadataUpdate(**payload.model_dump(by_alias=True)),
            changed_by,
            replace=True,
        )

    def patch(
        self, metadata_id: str, payload: MetadataUpdate, changed_by: str
    ) -> MetadataOut | None:
        return self.update(metadata_id, payload, changed_by)

    def update(
        self,
        metadata_id: str,
        payload: MetadataUpdate,
        changed_by: str,
        replace: bool = False,
    ) -> MetadataOut | None:
        current = self.repository.get_by_id(metadata_id)
        if current is None:
            return None

        merged = prepare_update(current, payload, replace=replace)
        merged.update(version=current["version"] + 1, updated_at=now_utc())
        updated = self.repository.update(metadata_id, merged)
        if updated is None:
            return None

        self.repository.create_history_entry(build_history_entry(updated, changed_by, "UPDATE"))
        return to_response(updated)

    def list_history(self, metadata_id: str) -> builtins.list:
        return normalize_history(self.repository.list_history(metadata_id))

    def list_all_history(self) -> builtins.list:
        return normalize_history(self.repository.list_all_history())

    def delete(self, metadata_id: str, deleted_by: str = "system") -> bool:
        current = self.repository.get_by_id(metadata_id)
        if current is None:
            return False

        deleted = {
            **current,
            "version": current["version"] + 1,
            "updated_at": now_utc(),
        }
        self.repository.create_history_entry(build_history_entry(deleted, deleted_by, "DELETE"))
        return self.repository.delete(metadata_id)
