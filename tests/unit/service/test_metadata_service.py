import pytest

from app.exceptions.domain import (
    ContractAlreadyExistsError,
    IncompatibleSchemaError,
    InvalidContractVersionError,
)
from app.models.metadata import MetadataCreate, MetadataUpdate
from app.services.metadata_service import MetadataService
from tests.support.fakes import FakeRepository


def make_service():
    return MetadataService(FakeRepository())


def make_payload(**values):
    data = {
        "data_asset": {"name": "orders", "type": "table"},
        "domain": "commerce",
        "ownership": {"owner": "commerce"},
        "source": {"system": "shop", "type": "database"},
        "schema": [{"name": "order_id", "type": "string"}],
    }
    data.update(values)
    return MetadataCreate(**data)


def test_create_persists_identity_and_history():
    service = make_service()

    result = service.create(make_payload(domain="commerce"), changed_by="admin")

    assert result.data_asset_key == "commerce.orders"
    assert len(service.repository.documents) == 1
    assert service.repository.history[0]["change_type"] == "CREATE"


def test_contract_version_update_reuses_document_and_history():
    service = make_service()
    first = service.create(make_payload(version="1.0"))

    second = service.create(make_payload(version="2.0"))

    assert second.id == first.id
    assert second.version == 2
    assert second.contract_version == "2.0"
    assert len(service.repository.history) == 2


def test_contract_version_rejects_duplicate_or_downgrade():
    service = make_service()
    service.create(make_payload(version="1.2"))

    with pytest.raises((ContractAlreadyExistsError, InvalidContractVersionError)):
        service.create(make_payload(version="1.1"))
    with pytest.raises(ContractAlreadyExistsError):
        service.create(make_payload(version="1.2"))


def test_patch_schema_merges_fields_without_replacing_existing_columns():
    service = make_service()
    created = service.create(
        make_payload(
            schema=[
                {"name": "order_id", "type": "string"},
                {"name": "total", "type": "decimal", "description": "Old"},
            ]
        )
    )

    result = service.patch(
        created.id,
        MetadataUpdate(schema=[{"name": "total", "type": "decimal", "description": "New"}]),
        "editor",
    )

    assert {field.name for field in result.schema_} == {"order_id", "total"}
    assert next(field for field in result.schema_ if field.name == "total").description == "New"


def test_minor_version_rejects_breaking_schema_change():
    service = make_service()
    service.create(make_payload(version="1.0", schema=[{"name": "id", "type": "string"}]))

    with pytest.raises(IncompatibleSchemaError):
        service.create(make_payload(version="1.1", schema=[{"name": "id", "type": "uuid"}]))


def test_major_version_allows_type_change():
    service = make_service()
    first = service.create(make_payload(version="1.0", schema=[{"name": "id", "type": "string"}]))

    updated = service.create(make_payload(version="2.0", schema=[{"name": "id", "type": "uuid"}]))

    assert updated.id == first.id
    assert updated.schema_[0].type == "uuid"


def test_delete_preserves_delete_history():
    service = make_service()
    created = service.create(make_payload())

    assert service.delete(created.id, deleted_by="admin") is True
    assert service.get_by_id(created.id) is None
    assert service.repository.history[-1]["change_type"] == "DELETE"


def test_quality_freshness_updates_as_a_nested_field():
    service = make_service()
    item = service.create(make_payload(quality={"freshness": {"max_delay": "1h"}}))

    updated = service.patch(
        item.id,
        MetadataUpdate(quality={"freshness": {"max_delay": "2h"}}),
        "editor",
    )

    assert updated.quality.freshness.max_delay == "2h"
