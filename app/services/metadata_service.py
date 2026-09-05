from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from app.models.metadata import (
    MetadataCreate,
    MetadataOut,
    MetadataUpdate,
    MetadataVersionEntry,
)

from app.repositories.metadata_repository import (
    MetadataRepository,
)

from app.validators.metadata_validator import (
    MetadataValidator,
)

class MetadataService:

    def __init__(self):
        self.repository = MetadataRepository()

    @staticmethod
    def _now_utc() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _to_utc(dt: datetime) -> datetime:
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    @staticmethod
    def _data_asset_key(data: dict) -> Optional[str]:
        if data.get("data_asset_key"):
            return str(data["data_asset_key"])

        asset = data.get("data_asset") or {}
        asset_name = asset.get("name") or data.get("table_name")
        domain = data.get("business_domain") or data.get("domain")
        if not asset_name:
            return None
        return f"{domain}.{asset_name}" if domain else str(asset_name)

    @staticmethod
    def _normalize_asset_data(data: dict) -> dict:
        ownership = data.get("ownership")
        if ownership and not data.get("owner_info"):
            data["owner_info"] = {
                "team": ownership["owner"],
                "email": None,
            }

        source = data.get("source")
        if source:
            if not data.get("source_system"):
                data["source_system"] = source["system"]
            if not data.get("source_type"):
                data["source_type"] = source["type"]

        asset = data.get("data_asset")
        if asset and not data.get("table_name"):
            data["table_name"] = asset["name"]
        elif data.get("table_name") and not asset:
            data["data_asset"] = {
                "name": data["table_name"],
                "type": "table",
            }
        return data

    def create(self, payload: MetadataCreate, changed_by: str = "system") -> MetadataOut:
        data = self._normalize_asset_data(payload.model_dump(by_alias=True))
        data["data_asset_key"] = self._data_asset_key(data)

        if data["data_asset_key"]:
            find_by_asset = getattr(self.repository, "get_by_data_asset_key", None)
            current = (
                find_by_asset(data["data_asset_key"])
                if find_by_asset is not None
                else None
            )
        else:
            current = None
        if current is None and payload.contract_name:
            current = self.repository.get_by_contract_name(payload.contract_name)
        if current is not None:
            data.pop("data_asset_key", None)
            update_payload = MetadataUpdate(**data)
            return self.update(current["_id"], update_payload, changed_by)

        MetadataValidator.validate(data)

        now = self._now_utc()
        data["created_at"] = now
        data["updated_at"] = now
        data["version"] = int(data.get("version", 1) or 1)

        history_entry = MetadataVersionEntry(
            version=int(data.get("version", 1) or 1),
            metadata_id=str(uuid4()),
            data_asset=data.get("data_asset"),
            data_asset_key=data.get("data_asset_key"),
            table_name=data.get("table_name"),
            description=data.get("description"),
            schema=data.get("schema", []),
            tags=data.get("tags", []),
            owner_info=data.get("owner_info"),
            source_system=data.get("source_system"),
            source_type=data.get("source_type"),
            freshness=data.get("freshness"),
            refresh_frequency=data.get("refresh_frequency"),
            contract_name=data.get("contract_name"),
            contract_version=data.get("contract_version"),
            quality=data.get("quality"),
            classification=data.get("classification"),
            lifecycle=data.get("lifecycle"),
            changed_at=self._to_utc(now),
            changed_by=changed_by,
            change_type="CREATE",
        )

        document = self.repository.create(
            {**data, "_id": history_entry.metadata_id}
        )
        self.repository.create_history_entry(history_entry.model_dump(by_alias=True))

        return self._to_response(document)

    def create_or_update_contract(
        self, payload: MetadataCreate, changed_by: str = "system"
    ) -> MetadataOut:
        return self.create(payload, changed_by)

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        domain: Optional[str] = None,
        owner: Optional[str] = None,
        table_name: Optional[str] = None,
        source_system: Optional[str] = None,
    ) -> tuple[List[MetadataOut], int]:
        filters = {
            key: value
            for key, value in {
                "domain": domain,
                "owner_info.team": owner,
                "table_name": table_name,
                "source_system": source_system,
            }.items()
            if value is not None
        }
        skip = (page - 1) * page_size
        documents = self.repository.list(filters, skip, page_size)
        return [self._to_response(document) for document in documents], self.repository.count(filters)

    def get_by_id(self, metadata_id: str) -> Optional[MetadataOut]:

        document = self.repository.get_by_id(metadata_id)
        if document is None:
            return None
        return self._to_response(document)

    def update(
        self,
        metadata_id: str,
        payload: MetadataUpdate,
        changed_by: str,
        replace: bool = False,
    ) -> Optional[MetadataOut]:

        current = self.repository.get_by_id(metadata_id)

        if current is None:
            return None

        update_data = payload.model_dump(
            by_alias=True, exclude={"version"}, exclude_unset=not replace
        )
        update_data = self._normalize_asset_data(update_data)

        merged = {**current, **update_data}
        merged["data_asset_key"] = self._data_asset_key(merged)
        MetadataValidator.validate(merged)

        current_version = int(current.get("version", 0) or 0)
        next_version = current_version + 1

        history_entry = MetadataVersionEntry(
            version=next_version,
            metadata_id=metadata_id,
            data_asset=merged.get("data_asset"),
            data_asset_key=merged.get("data_asset_key"),
            table_name=merged.get("table_name"),
            description=merged.get("description"),
            schema=merged.get("schema", []),
            tags=merged.get("tags", []),
            owner_info=merged.get("owner_info"),
            source_system=merged.get("source_system"),
            source_type=merged.get("source_type"),
            freshness=merged.get("freshness"),
            refresh_frequency=merged.get("refresh_frequency"),
            contract_name=merged.get("contract_name"),
            contract_version=merged.get("contract_version"),
            quality=merged.get("quality"),
            classification=merged.get("classification"),
            lifecycle=merged.get("lifecycle"),
            changed_at=self._to_utc(self._now_utc()),
            changed_by=changed_by,
            change_type="UPDATE",
        )
        self.repository.create_history_entry(history_entry.model_dump(by_alias=True))

        update_data["version"] = next_version
        update_data["data_asset_key"] = merged["data_asset_key"]
        update_data["updated_at"] = self._now_utc()

        updated = self.repository.update(metadata_id, update_data)

        return self._to_response(updated)

    def list_history(self, metadata_id: str) -> List[MetadataVersionEntry]:
        documents = self.repository.list_history(metadata_id)
        return self._normalize_history(documents)

    def list_all_history(self) -> List[MetadataVersionEntry]:
        documents = self.repository.list_all_history()
        return self._normalize_history(documents)

    def _normalize_history(
        self, documents: List[dict]
    ) -> List[MetadataVersionEntry]:
        normalized = []
        for source_document in documents:
            document = dict(source_document)
            if document.get("changed_at") is not None:
                document["changed_at"] = self._to_utc(document["changed_at"])
            if document.get("deleted_at") is not None:
                document["deleted_at"] = self._to_utc(document["deleted_at"])
            document.setdefault("changed_by", "system")
            normalized.append(MetadataVersionEntry.model_validate(document))
        return normalized

    def delete(self, metadata_id: str, deleted_by: str = "system") -> bool:
        current = self.repository.get_by_id(metadata_id)
        if current is None:
            return False

        now = self._now_utc()
        deletion_entry = MetadataVersionEntry(
            version=int(current.get("version", 0) or 0) + 1,
            metadata_id=metadata_id,
            data_asset=current.get("data_asset"),
            data_asset_key=current.get("data_asset_key"),
            table_name=current.get("table_name"),
            description=current.get("description"),
            schema=current.get("schema", []),
            tags=current.get("tags", []),
            owner_info=current.get("owner_info"),
            source_system=current.get("source_system"),
            source_type=current.get("source_type"),
            freshness=current.get("freshness"),
            refresh_frequency=current.get("refresh_frequency"),
            contract_name=current.get("contract_name"),
            contract_version=current.get("contract_version"),
            quality=current.get("quality"),
            classification=current.get("classification"),
            lifecycle=current.get("lifecycle"),
            deleted=True,
            deleted_at=now,
            deleted_by=deleted_by,
            changed_at=now,
            changed_by=deleted_by,
            change_type="DELETE",
        )
        self.repository.create_history_entry(deletion_entry.model_dump(by_alias=True))
        return self.repository.delete(metadata_id, deleted_by)

    @staticmethod
    def _to_response(document) -> MetadataOut:

        return MetadataOut(
            id=str(document["_id"]),
            version=int(document.get("version", 1) or 1),
            data_asset=document.get("data_asset"),
            data_asset_key=document.get("data_asset_key"),
            table_name=document["table_name"],
            description=document.get("description"),
            business_domain=document.get("business_domain"),
            domain=document.get("domain"),
            schema=document.get("schema", []),
            tags=document.get("tags", []),
            created_at=MetadataService._to_utc(document["created_at"]),
            updated_at=MetadataService._to_utc(document["updated_at"]),
            owner_info=document.get("owner_info"),
            source_system=document.get("source_system"),
            source_type=document.get("source_type"),
            freshness=document.get("freshness"),
            refresh_frequency=document.get("refresh_frequency"),
            contract_name=document.get("contract_name"),
            contract_version=document.get("contract_version"),
            data_product=document.get("data_product"),
            quality=document.get("quality"),
            classification=document.get("classification"),
            lifecycle=document.get("lifecycle"),
        )
