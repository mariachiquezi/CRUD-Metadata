from pymongo import MongoClient

from app.config.settings import settings


class MongoDatabase:
    def __init__(self):
        self.client: MongoClient = MongoClient(
            settings.mongodb_uri,
            connect=False,
            tz_aware=True,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=10000,
        )
        self.database = self.client[settings.mongodb_db_name]

    def get_collection(self, collection_name: str):
        return self.database[collection_name]

    def ping(self) -> None:
        self.client.admin.command("ping")

    def close(self) -> None:
        self.client.close()


mongo_database = MongoDatabase()
