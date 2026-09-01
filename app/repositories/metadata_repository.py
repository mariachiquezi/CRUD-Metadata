from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.database.mongodb import mongo_database


class MetadataRepository:

    collection_name = "metadata"

    def __init__(self):
        self.collection = mongo_database.get_collection(self.collection_name)

        self.collection.create_index(
            [("contract_name", 1), ("contract_version", 1)], unique=True
        )

    def create(self, document: Dict[str, Any]) -> Dict[str, Any]:
        document["_id"] = str(uuid4())

        self.collection.insert_one(document)

        return document

    def list(self) -> List[Dict[str, Any]]:
        return list(self.collection.find({}))

    def get_by_id(self, metadata_id: str) -> Optional[Dict[str, Any]]:
        return self.collection.find_one({"_id": metadata_id})

    def update(
        self, metadata_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:

        result = self.collection.find_one_and_update(
            {"_id": metadata_id},
            {"$set": data},
            return_document=True,
        )

        return result

    def delete(self, metadata_id: str) -> bool:
        result = self.collection.delete_one({"_id": metadata_id})

        return result.deleted_count > 0
