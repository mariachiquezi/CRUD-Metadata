import pytest

from app.models.metadata import MetadataCreate
from app.validators.metadata_validator import MetadataValidator


def payload():
    return {
        "data_asset": {"name": "orders", "type": "table"},
        "domain": "commerce",
        "ownership": {"owner": "commerce"},
        "source": {"system": "shop", "type": "database"},
        "schema": [{"name": "order_id", "type": "string"}],
    }


def test_json_metadata_uses_the_same_quality_reference_rule_as_yaml():
    data = payload()
    data["quality"] = {"completeness": [{"field": "missing", "threshold": 99}]}
    with pytest.raises(ValueError, match="campo inexistente"):
        MetadataValidator.validate(MetadataCreate.model_validate(data))


@pytest.mark.parametrize("field", ["data_asset", "domain", "ownership", "source"])
def test_required_metadata_structure_is_rejected(field):
    data = payload()
    data.pop(field)
    with pytest.raises(ValueError):
        MetadataCreate.model_validate(data)


@pytest.mark.parametrize(
    "legacy_field",
    ["table_name", "business_domain", "source_system", "source_type", "freshness"],
)
def test_legacy_flattened_fields_are_rejected(legacy_field):
    data = payload()
    data[legacy_field] = "legacy"

    with pytest.raises(ValueError):
        MetadataCreate.model_validate(data)
