from pymongo import MongoClient

from app.config.settings import settings


class MongoDatabase:
    def __init__(self):
        self.client: MongoClient = MongoClient(
            settings.mongodb_uri,
            connect=False,  # Impede que o MongoClient tente conectar imediatamente ao criar o objeto.
            tz_aware=True,  # Faz o PyMongo preservar informações de fuso horário nos valores datetime
            serverSelectionTimeoutMS=5000,  # Tempo para encontrar um servidor disponível
            connectTimeoutMS=5000,  # Tempo para abrir a conexão
            socketTimeoutMS=10000,  # Tempo para operações de leitura e escrita
        )
        self.database = self.client[settings.mongodb_db_name]

    def get_collection(self, collection_name: str):
        return self.database[collection_name]

    def ping(self) -> None:
        self.client.admin.command("ping")

    def close(self) -> None:
        self.client.close()


mongo_database = MongoDatabase()
