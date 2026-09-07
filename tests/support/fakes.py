class FakeRepository:
    """Repository em memória usado pelos testes unitários e de API."""

    def __init__(self):
        self.documents = {}
        self.history = []

    def create(self, document):
        self.documents[document["_id"]] = document
        return document

    def create_history_entry(self, document):
        self.history.append(document)
        return document

    def get_by_id(self, metadata_id):
        return self.documents.get(metadata_id)

    def get_by_data_asset_key(self, data_asset_key):
        return next(
            (
                document
                for document in self.documents.values()
                if document.get("data_asset_key") == data_asset_key
            ),
            None,
        )

    def update(self, metadata_id, data):
        self.documents[metadata_id].update(data)
        return self.documents[metadata_id]

    def list(self, filters=None, skip=0, limit=None):
        values = list(self.documents.values())
        return values[skip:][:limit]

    def count(self, filters=None):
        return len(self.documents)

    def list_history(self, metadata_id):
        return [item for item in self.history if item["metadata_id"] == metadata_id]

    def list_all_history(self):
        return self.history

    def delete(self, metadata_id):
        return self.documents.pop(metadata_id, None) is not None
