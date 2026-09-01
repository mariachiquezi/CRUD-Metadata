from pymongo import MongoClient

from app.config.settings import settings


class MongoDatabase:

    def __init__(self):
        self.client = MongoClient(settings.mongodb_uri)
        self.database = self.client[settings.mongodb_db_name]

    def get_collection(self, collection_name: str):
        return self.database[collection_name]


mongo_database = MongoDatabase()
