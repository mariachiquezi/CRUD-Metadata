from __future__ import annotations

import builtins
from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from app.domain.schema_compatibility import validate_schema_compatibility
from app.domain.versioning import (
    is_major_version_upgrade,
    validate_next_contract_version,
    version_parts,
)
from app.exceptions.domain import DomainError
from app.models.metadata import (
    MetadataCreate,
    MetadataOut,
    MetadataReplace,
    MetadataUpdate,
    MetadataVersionEntry,
)
from app.repositories.protocols import MetadataRepositoryProtocol
from app.validators.metadata_validator import MetadataValidator


class MetadataService:
    """Application use cases with an injected Repository abstraction."""

    def __init__(self, repository: MetadataRepositoryProtocol):
        self.repository = repository

    @staticmethod
    def _now_utc() -> datetime:
        return datetime.now(UTC)

    @staticmethod
    def _to_utc(value: datetime | str) -> datetime:
        if isinstance(value, str):
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)

    @staticmethod
    def _normalize_asset_data(data: dict) -> dict:
        pairs = [
            ("data_asset", "name", "table_name"),
            ("source", "system", "source_system"),
            ("source", "type", "source_type"),
        ]
        for nested, key, flat in pairs:
            if data.get(nested):
                value = data[nested][key]
                if data.get(flat) and data[flat] != value:
                    raise ValueError(f"{nested}.{key} e {flat} devem ser iguais.")
                data[flat] = value
        if data.get("table_name") and not data.get("data_asset"):
            data["data_asset"] = {"name": data["table_name"], "type": "table"}
        ownership, owner = data.get("ownership"), data.get("owner_info")
        if ownership and owner and ownership["owner"] != owner["team"]:
            raise ValueError("ownership.owner e owner_info.team devem ser iguais.")
        if ownership and not owner:
            data["owner_info"] = {"team": ownership["owner"], "email": None}
        elif owner and not ownership:
            data["ownership"] = {"owner": owner["team"], "steward": None}
        if data.get("domain") is not None:
            data["business_domain"] = data["domain"]
        elif data.get("business_domain") is not None:
            data["domain"] = data["business_domain"]
        quality = data.get("quality")
        freshness = quality.get("freshness") if quality else None
        if freshness:
            if data.get("freshness") and data["freshness"] != freshness["max_delay"]:
                raise ValueError("freshness e quality.freshness.max_delay devem ser iguais.")
            data["freshness"] = freshness["max_delay"]
        elif "quality" in data and not data.get("freshness"):
            data["freshness"] = None
        return data

    @staticmethod
    def _data_asset_key(data: dict) -> str:
        name = data["table_name"]
        domain = data.get("domain") or data.get("business_domain")
        return f"{domain}.{name}" if domain else name

    def _history(
        self, data: dict, actor: str, change_type: Literal["CREATE", "UPDATE", "DELETE"]
    ) -> dict:
        values = {key: value for key, value in data.items() if key != "_id"}
        values.update(
            metadata_id=data["_id"],
            changed_at=data["updated_at"],
            changed_by=actor,
            change_type=change_type,
        )
        if change_type == "DELETE":
            values.update(deleted=True, deleted_at=data["updated_at"], deleted_by=actor)
        return MetadataVersionEntry.model_validate(values).model_dump(by_alias=True)

    def create(self, payload: MetadataCreate, changed_by: str = "system") -> MetadataOut:
        data = self._normalize_asset_data(payload.model_dump(by_alias=True))
        MetadataValidator.validate(MetadataCreate.model_validate(data))
        data["data_asset_key"] = self._data_asset_key(data)
        if data.get("contract_version") is not None:
            version_parts(data["contract_version"])
        current = self.repository.get_by_data_asset_key(data["data_asset_key"])
        if current is not None:
            if not data.get("contract_version"):
                raise DomainError("Já existe um metadado para essa tabela.")
            validate_next_contract_version(
                current.get("contract_version"), data["contract_version"], data["data_asset_key"]
            )
            data.pop("data_asset_key")
            result = self.update(current["_id"], MetadataUpdate(**data), changed_by, replace=True)
            if result is None:
                raise DomainError(
                    "Metadado alterado simultaneamente. Consulte novamente e tente outra vez."
                )
            return result
        now = self._now_utc()
        data.update(_id=str(uuid4()), version=1, created_at=now, updated_at=now)
        document = self.repository.create(data)
        self.repository.create_history_entry(self._history(data, changed_by, "CREATE"))
        return self._to_response(document)

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
                "owner_info.team": owner,
                "table_name": table_name,
            }.items()
            if value is not None
        }
        documents = self.repository.list(filters, (page - 1) * page_size, page_size)
        return [self._to_response(document) for document in documents], self.repository.count(
            filters
        )

    def get_by_id(self, metadata_id: str) -> MetadataOut | None:
        document = self.repository.get_by_id(metadata_id)
        return self._to_response(document) if document is not None else None

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
        self, metadata_id: str, payload: MetadataUpdate, changed_by: str, replace: bool = False
    ) -> MetadataOut | None:
        current = self.repository.get_by_id(metadata_id)
        if current is None:
            return None
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
        data = self._normalize_asset_data(data)
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
        merged["data_asset_key"] = self._data_asset_key(merged)
        if merged["data_asset_key"] != current["data_asset_key"]:
            raise DomainError("A identidade da tabela é imutável; cadastre outro metadado.")
        if current.get("contract_version") and merged.get("contract_version") is None:
            raise ValueError("contract_version não pode ser removida de um contrato versionado.")
        if merged.get("contract_version") is not None:
            version_parts(merged["contract_version"])
        if "contract_version" in data and data["contract_version"] != current.get(
            "contract_version"
        ):
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
        merged.update(version=current["version"] + 1, updated_at=self._now_utc())
        updated = self.repository.update(metadata_id, merged)
        if updated is None:
            return None
        self.repository.create_history_entry(self._history(updated, changed_by, "UPDATE"))
        return self._to_response(updated)

    def list_history(self, metadata_id: str) -> builtins.list[MetadataVersionEntry]:
        return self._normalize_history(self.repository.list_history(metadata_id))

    def list_all_history(self) -> builtins.list[MetadataVersionEntry]:
        return self._normalize_history(self.repository.list_all_history())

    def _normalize_history(
        self, documents: builtins.list[dict]
    ) -> builtins.list[MetadataVersionEntry]:
        result = []
        for source in documents:
            document = dict(source)
            for field in ("changed_at", "deleted_at"):
                if document.get(field) is not None:
                    document[field] = self._to_utc(document[field])
            document.setdefault("changed_by", "system")
            result.append(MetadataVersionEntry.model_validate(document))
        return result

    def delete(self, metadata_id: str, deleted_by: str = "system") -> bool:
        current = self.repository.get_by_id(metadata_id)
        if current is None:
            return False
        deleted = {**current, "version": current["version"] + 1, "updated_at": self._now_utc()}
        self.repository.create_history_entry(self._history(deleted, deleted_by, "DELETE"))
        return self.repository.delete(metadata_id)

    @staticmethod
    def _to_response(document: dict) -> MetadataOut:
        data = {**document, "id": str(document["_id"])}
        for field in ("created_at", "updated_at"):
            data[field] = MetadataService._to_utc(data[field])
        return MetadataOut.model_validate(data)
