from copy import deepcopy

import pytest

from app.models.contract import DataContract


def definition():
    return {
        "data_asset": {"name": "orders", "type": "table"},
        "version": "1.0",
        "ownership": {"owner": "commerce-platform"},
        "source": {"system": "ecommerce", "type": "database"},
        "domain": "commerce",
        "schema": [{"name": "order_id", "type": "string"}],
    }


def test_contract_preserves_identity_and_native_column_type():
    data = definition()
    data["schema"][0]["type"] = "decimal(18,2)"

    contract = DataContract(contract=data).contract

    assert contract.data_asset.name == "orders"
    # validar tipos aceitos no schema
    assert contract.schema_[0].type == "decimal(18,2)"

# executar a mesma função varias vezes
@pytest.mark.parametrize(
    "changes",
    [
        {"schema": []},
        {"source": {"system": "ecommerce", "type": "spreadsheet"}},
        {"ownership": {"owner": " "}},
        {"unexpected": "must not be ignored"},
    ],
)
def test_invalid_contract_structure_is_rejected(changes):
    with pytest.raises(ValueError):
        DataContract(contract={**definition(), **deepcopy(changes)})


def test_quality_cannot_reference_unknown_column():
    data = definition()
    data["quality"] = {"completeness": [{"field": "missing", "threshold": 99}]}

    with pytest.raises(ValueError, match="campo inexistente"):
        DataContract(contract=data)


def test_outer_contract_rejects_unknown_fields():
    with pytest.raises(ValueError):
        DataContract.model_validate({"contract": definition(), "unexpected": True})
