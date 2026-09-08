from pathlib import Path

import pytest

from app.services.contract_service import ContractService
from app.services.metadata_service import MetadataService
from app.utils.contract_parser import ContractParser
from tests.support.fakes import FakeRepository


def test_sample_contract_preserves_governance_fields():
    repository = FakeRepository()
    service = ContractService(MetadataService(repository))
    content = (Path(__file__).resolve().parents[3] / "contracts" / "orders.yaml").read_text(
        encoding="utf-8"
    )
    contract = ContractParser.parse(content).contract
    result = service.process(content, "editor")
    assert result.data_asset.name == contract.data_asset.name
    assert result.ownership.steward
    assert result.source == contract.source
    assert result.tags == contract.tags
    assert result.quality.freshness.max_delay == contract.quality.freshness.max_delay
    assert repository.history[0]["data_product"] == result.data_product.model_dump()


def test_invalid_yaml_is_rejected():
    with pytest.raises(ValueError):
        ContractParser.parse("[")


def test_repeated_yaml_key_is_rejected_before_overwriting_value():
    with pytest.raises(ValueError, match="Chave duplicada"):
        ContractParser.parse("contract:\n  version: '1.0'\n  version: '2.0'\n")


def test_missing_ownership_example_is_rejected():
    content = (
        Path(__file__).resolve().parents[3] / "contracts" / "invalid-missing-ownership.yaml"
    ).read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="ownership"):
        ContractParser.parse(content)


def test_asset_description_is_not_replaced_with_product_description():
    repository = FakeRepository()
    service = ContractService(MetadataService(repository))
    content = """
contract:
  data_asset: {name: orders}
  version: "1.0"
  description: Context of this table
  data_product: {name: commerce, description: Context of the product}
  ownership: {owner: commerce}
  source: {system: shop, type: database}
  domain: commerce
  tags: [sales]
  schema:
    - {name: id, type: string}
"""

    result = service.process(content, "editor")

    assert result.description == "Context of this table"
    assert result.data_product.description == "Context of the product"
