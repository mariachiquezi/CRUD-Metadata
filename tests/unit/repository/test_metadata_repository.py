from app.repositories.metadata_repository import MetadataRepository


class FakeCursor:
    def __init__(self, documents):
        self.documents = documents

    def skip(self, amount):
        # usado para paginação
        self.documents = self.documents[amount:]
        return self

    def limit(self, amount):
        self.documents = self.documents[:amount]
        return self

    def sort(self, field_or_fields, direction=None):
        # ordenação 
        # O valor 1 representa ordem crescente. -1 decrescente
        if isinstance(field_or_fields, list):
            for field, order in reversed(field_or_fields):
                self.documents.sort(key=lambda item: item.get(field, 0), reverse=order < 0)
        else:
            self.documents.sort(
                key=lambda item: item.get(field_or_fields, 0), reverse=direction < 0
            )
        return self

    def __iter__(self):
        return iter(self.documents)


class FakeCollection:
    def __init__(self):
        self.documents = []
        self.indexes = []
        self.last_update = None

    def create_index(self, key, **options):
        self.indexes.append((key, options))

    def insert_one(self, document, **kwargs):
        self.documents.append(document.copy())

    def find(self, filters):
        documents = [
            document.copy()
            for document in self.documents
            if all(document.get(key) == value for key, value in filters.items())
        ]
        return FakeCursor(documents)

    def count_documents(self, filters):
        return len(list(self.find(filters)))

    def find_one(self, filters):
        return next(iter(self.find(filters)), None)

    def find_one_and_update(self, filters, update, **kwargs):
        self.last_update = update
        if self.find_one(filters) is None:
            return None
        document = self.find_one(filters)
        document.update(update["$set"])
        self.documents = [
            document if item.get("_id") == document["_id"] else item for item in self.documents
        ]
        return document

    def delete_one(self, filters, **kwargs):
        before = len(self.documents)
        self.documents = [
            item for item in self.documents if not all(item.get(k) == v for k, v in filters.items())
        ]

        class Result:
            deleted_count = before - len(self.documents)

        return Result()


def make_repository():
    repository = MetadataRepository.__new__(MetadataRepository)
    repository.metadata_collection = FakeCollection()
    repository.history_collection = FakeCollection()
    return repository


def test_indexes_and_pagination_are_configured():
    # criar index
    repository = make_repository()
    repository.create_indexes()
    repository.metadata_collection.insert_one({"_id": "1", "domain": "commerce"})
    repository.metadata_collection.insert_one({"_id": "2", "domain": "commerce"})

    assert len(repository.metadata_collection.indexes) == 4
    assert repository.metadata_collection.indexes[0][1]["unique"] is True
    assert repository.count({"domain": "commerce"}) == 2
    assert [item["_id"] for item in repository.list({}, skip=1, limit=1)] == ["2"]


def test_update_does_not_modify_id():
    # update description
    repository = make_repository()
    repository.metadata_collection.insert_one({"_id": "1", "description": "old"})

    result = repository.update("1", {"_id": "1", "description": "new"})

    assert result["description"] == "new"
    assert repository.metadata_collection.last_update == {"$set": {"description": "new"}}


def test_history_is_sorted_and_delete_preserves_it():
    # deletar do original porem manter no historico
    repository = make_repository()
    repository.metadata_collection.insert_one({"_id": "1", "version": 1})
    repository.history_collection.insert_one({"metadata_id": "1", "version": 1})
    repository.history_collection.insert_one({"metadata_id": "1", "version": 2})

    assert [item["version"] for item in repository.list_history("1")] == [2, 1]
    assert repository.delete("1") is True
    assert repository.get_by_id("1") is None
    assert repository.history_collection.documents
