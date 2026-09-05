from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.database.mongodb import mongo_database


class MetadataRepository:

    metadata_collection_name = "metadata"
    history_collection_name = "metadata_history"

    def __init__(self):
        self.metadata_collection = mongo_database.get_collection(
            self.metadata_collection_name
        )
        self.history_collection = mongo_database.get_collection(self.history_collection_name)

    def create_indexes(self) -> None:
        self.metadata_collection.create_index(
            [("contract_name", 1), ("contract_version", 1)], unique=True
        )
        self.history_collection.create_index(
            [("metadata_id", 1), ("version", 1)], unique=True
        )
        self.metadata_collection.create_index("domain")
        self.metadata_collection.create_index("table_name")
        self.metadata_collection.create_index("owner_info.team")

    def create(self, document: Dict[str, Any]) -> Dict[str, Any]:
        document.setdefault("_id", str(uuid4()))
        document.setdefault("version", 1)

        self.metadata_collection.insert_one(document)

        return document

    def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        cursor = self.metadata_collection.find(filters or {}).skip(skip)
        if limit is not None:
            cursor = cursor.limit(limit)
        return list(cursor)

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        return self.metadata_collection.count_documents(filters or {})

    def get_by_id(self, metadata_id: str) -> Optional[Dict[str, Any]]:
        return self.metadata_collection.find_one({"_id": metadata_id})

    def update(
        self, metadata_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:

        result = self.metadata_collection.find_one_and_update(
            {"_id": metadata_id},
            {"$set": data},
            return_document=True,
        )

        return result

    def create_history_entry(self, document: Dict[str, Any]) -> Dict[str, Any]:
        self.history_collection.insert_one(document)
        return document

    def list_history(self, metadata_id: str) -> List[Dict[str, Any]]:
        return list(self.history_collection.find({"metadata_id": metadata_id}).sort("version", -1))

    def list_all_history(self) -> List[Dict[str, Any]]:
        return list(
            self.history_collection.find({}).sort(
                [("metadata_id", 1), ("version", -1)]
            )
        )

    def delete(self, metadata_id: str, deleted_by: str) -> bool:
        result = self.metadata_collection.delete_one({"_id": metadata_id})
        if result.deleted_count == 0:
            return False

        now = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
        self.history_collection.update_many(
            {"metadata_id": metadata_id},
            {"$set": {"deleted": True, "deleted_at": now, "deleted_by": deleted_by}},
        )

        return True
