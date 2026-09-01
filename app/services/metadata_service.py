from datetime import datetime, timezone
from typing import List, Optional

from app.models.metadata import (
    MetadataCreate,
    MetadataOut,
    MetadataUpdate,
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

    def create(self, payload: MetadataCreate) -> MetadataOut:
        data = payload.model_dump()
        MetadataValidator.validate(data)

        now = datetime.now(timezone.utc)
        data["created_at"] = now
        data["updated_at"] = now

        document = self.repository.create(data)
        return self._to_response(document)

    def list(self) -> List[MetadataOut]:
        documents = self.repository.list()
        return [self._to_response(document) for document in documents]

    def get_by_id(self, metadata_id: str) -> Optional[MetadataOut]:

        document = self.repository.get_by_id(metadata_id)
        if document is None:
            return None
        return self._to_response(document)

    def update(
        self, metadata_id: str, payload: MetadataUpdate
    ) -> Optional[MetadataOut]:

        current = self.repository.get_by_id(metadata_id)

        if current is None:
            return None

        update_data = payload.model_dump(exclude_unset=True)

        merged = {**current, **update_data}

        MetadataValidator.validate(merged)

        update_data["updated_at"] = datetime.now(timezone.utc)

        updated = self.repository.update(metadata_id, update_data)

        return self._to_response(updated)

    def delete(self, metadata_id: str) -> bool:

        return self.repository.delete(metadata_id)

    @staticmethod
    def _to_response(document) -> MetadataOut:

        return MetadataOut(
            id=str(document["_id"]),
            table_name=document["table_name"],
            description=document.get("description"),
            business_domain=document.get("business_domain"),
            domain=document.get("domain"),
            schema=document.get("schema", []),
            tags=document.get("tags", []),
            created_at=document["created_at"],
            updated_at=document["updated_at"],
            owner_info=document.get("owner_info"),
            source_system=document.get("source_system"),
            source_type=document.get("source_type"),
            freshness=document.get("freshness"),
            refresh_frequency=document.get("refresh_frequency"),
        )
