from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

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


class MetadataCreate(InputModel):
    """Formato oficial para cadastrar um metadado."""

    data_asset: DataAsset
    domain: str = Field(min_length=1)
    description: str | None = None
    schema_: list[SchemaField] = Field(alias="schema", min_length=1)
    tags: list[Tag] = Field(default_factory=list)
    ownership: Ownership
    source: Source
    refresh_frequency: str | None = None
    contract_version: str | None = Field(
        default=None,
        validation_alias="version",
        serialization_alias="contract_version",
    )
    data_product: DataProduct | None = None
    quality: Quality | None = None
    classification: Classification | None = None
    lifecycle: Lifecycle | None = None


class MetadataUpdate(InputModel):
    """Campos oficiais aceitos em uma atualização parcial (PATCH)."""

    data_asset: DataAsset | None = None
    domain: str | None = Field(default=None, min_length=1)
    description: str | None = None
    schema_: list[SchemaField] | None = Field(default=None, alias="schema")
    tags: list[Tag] | None = None
    ownership: Ownership | None = None
    source: Source | None = None
    refresh_frequency: str | None = None
    contract_version: str | None = Field(
        default=None,
        validation_alias="version",
        serialization_alias="contract_version",
    )
    data_product: DataProduct | None = None
    quality: Quality | None = None
    classification: Classification | None = None
    lifecycle: Lifecycle | None = None


class MetadataReplace(MetadataCreate):
    """Representa a substituição completa de um metadado. (PUT)"""


class MetadataOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    metadata_version: int = Field(default=1, alias="version")
    data_asset: DataAsset
    data_asset_key: str | None = None
    description: str | None = None
    domain: str
    schema_: list[SchemaField] = Field(alias="schema")
    tags: list[Tag] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    ownership: Ownership
    source: Source
    refresh_frequency: str | None = None
    contract_version: str | None = None
    data_product: DataProduct | None = None
    quality: Quality | None = None
    classification: Classification | None = None
    lifecycle: Lifecycle | None = None

    @property
    def version(self) -> int:
        return self.metadata_version


class MetadataListResponse(BaseModel):
    items: list[MetadataOut]
    total: int
    page: int = 1
    page_size: int = 0


class MetadataVersionEntry(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    metadata_version: int = Field(..., alias="version")
    metadata_id: str
    data_asset: DataAsset
    data_asset_key: str | None = None
    description: str | None = None
    domain: str
    data_product: DataProduct | None = None
    ownership: Ownership
    source: Source
    schema_: list[SchemaField] = Field(alias="schema")
    tags: list[Tag] = Field(default_factory=list)
    refresh_frequency: str | None = None
    contract_version: str | None = None
    quality: Quality | None = None
    classification: Classification | None = None
    lifecycle: Lifecycle | None = None
    deleted: bool = False
    deleted_at: datetime | None = None
    deleted_by: str | None = None
    changed_at: datetime
    changed_by: str
    change_type: Literal["CREATE", "UPDATE", "DELETE"] = "UPDATE"

    @property
    def version(self) -> int:
        return self.metadata_version
