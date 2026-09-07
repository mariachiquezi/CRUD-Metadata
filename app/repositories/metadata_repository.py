import builtins
from typing import Any
from uuid import uuid4

from app.database.mongodb import mongo_database


class MetadataRepository:
    metadata_collection_name = "metadata"
    history_collection_name = "metadata_history"

    def __init__(self, database=None):
        database = database if database is not None else mongo_database
        self.metadata_collection = database.get_collection(self.metadata_collection_name)
        self.history_collection = database.get_collection(self.history_collection_name)

    def create_indexes(self) -> None:
        self.metadata_collection.create_index(
            "data_asset_key",
            unique=True,
            partialFilterExpression={"data_asset_key": {"$exists": True}},
        )
        self.history_collection.create_index(
            [("metadata_id", 1), ("version", 1)],
            unique=True,
        )
        self.metadata_collection.create_index("domain")
        self.metadata_collection.create_index("table_name")
        self.metadata_collection.create_index("ownership.owner")

    def list(
        self,
        filters: dict[str, Any] | None = None,
        skip: int = 0,
        limit: int | None = None,
    ) -> builtins.list[dict[str, Any]]:
        cursor = self.metadata_collection.find(filters or {}).sort("_id", 1).skip(skip)

        if limit is not None:
            cursor = cursor.limit(limit)

        return list(cursor)

    def count(self, filters: dict[str, Any] | None = None) -> int:
        return self.metadata_collection.count_documents(filters or {})

    def get_by_id(self, metadata_id: str) -> dict[str, Any] | None:
        return self.metadata_collection.find_one({"_id": metadata_id})

    def get_by_data_asset_key(
        self,
        data_asset_key: str,
    ) -> dict[str, Any] | None:
        return self.metadata_collection.find_one({"data_asset_key": data_asset_key})

    def list_history(
        self,
        metadata_id: str,
    ) -> builtins.list[dict[str, Any]]:
        return list(self.history_collection.find({"metadata_id": metadata_id}).sort("version", -1))

    def list_all_history(self) -> builtins.list[dict[str, Any]]:
        return list(self.history_collection.find({}).sort([("metadata_id", 1), ("version", -1)]))

    def create(self, document: dict[str, Any]) -> dict[str, Any]:
        document.setdefault("_id", str(uuid4()))
        document.setdefault("version", 1)
        self.metadata_collection.insert_one(document)
        return document

    def update(self, metadata_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        changes = {key: value for key, value in data.items() if key != "_id"}
        return self.metadata_collection.find_one_and_update(
            {"_id": metadata_id},
            {"$set": changes},
            return_document=True,
        )

    def create_history_entry(self, document: dict[str, Any]) -> dict[str, Any]:
        self.history_collection.insert_one(document)
        return document

    def delete(self, metadata_id: str) -> bool:
        result = self.metadata_collection.delete_one({"_id": metadata_id})
        return result.deleted_count > 0
