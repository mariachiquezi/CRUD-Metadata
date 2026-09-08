import pytest

from app.domain.metadata_identity import DataAssetIdentity
from app.domain.schema_compatibility import SchemaCompatibilityPolicy
from app.domain.versioning import ContractVersionPolicy
from app.exceptions.domain import ContractAlreadyExistsError, IncompatibleSchemaError


def test_data_asset_identity_builds_a_stable_key():
    identity = DataAssetIdentity.from_document(
        {"data_asset": {"name": "orders"}, "domain": "commerce"}
    )

    assert identity.key == "commerce.orders"


def test_contract_version_policy_normalizes_and_detects_major_upgrade():
    policy = ContractVersionPolicy()

    assert policy.parse("1.0.0") == (1,)
    assert policy.is_major_upgrade("1.2", "2.0") is True
    with pytest.raises(ContractAlreadyExistsError):
        policy.validate_next("1.2", "1.2", "commerce.orders")


def test_schema_policy_rejects_a_breaking_type_change():
    policy = SchemaCompatibilityPolicy()
    current = {"schema": [{"name": "id", "type": "string"}]}
    requested = {"schema": [{"name": "id", "type": "uuid"}]}

    with pytest.raises(IncompatibleSchemaError):
        policy.validate(current, requested)
