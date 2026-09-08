from typing import Any, Literal

from pydantic import Field, model_validator

from app.domain.versioning import ContractVersionPolicy
from app.models.data_asset import (
    Classification,
    DataAsset,
    DataProduct,
    InputModel,
    Lifecycle,
    Ownership,
    Quality,
    SchemaField,
    Source,
    Tag,
)
from app.models.metadata import MetadataOut
from app.validators.schema_validator import validate_schema


class ContractDefinition(InputModel):
    data_asset: DataAsset
    version: str = Field(min_length=1)
    description: str | None = None
    data_product: DataProduct | None = None
    ownership: Ownership
    source: Source
    domain: str = Field(min_length=1)
    schema_: list[SchemaField] = Field(alias="schema")
    tags: list[Tag] = Field(default_factory=list)
    refresh_frequency: str | None = None
    quality: Quality | None = None
    classification: Classification | None = None
    lifecycle: Lifecycle | None = None

    @model_validator(mode="after")
    def validate_definition(self):
        ContractVersionPolicy().parse(self.version)
        validate_schema(self.schema_, self.quality)
        return self


class DataContract(InputModel):
    contract: ContractDefinition


class ContractBulkItem(InputModel):
    filename: str | None = None
    status: Literal["success", "error"]
    status_code: int
    metadata: MetadataOut | None = None
    detail: Any | None = None


class ContractBulkResponse(InputModel):
    items: list[ContractBulkItem]
    total: int
