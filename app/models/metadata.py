from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.data_asset import (
    Classification,
    DataAsset,
    DataProduct,
    InputModel,
    Lifecycle,
    OwnerInfo,
    Ownership,
    Quality,
    SchemaField,
    Source,
    SourceType,
    Tag,
)


class MetadataCreate(InputModel):
    data_asset: DataAsset | None = None
    table_name: str | None = Field(default=None, min_length=1)
    description: str | None = None
    business_domain: str | None = None
    domain: str | None = None
    schema_: list[SchemaField] = Field(default_factory=list, alias="schema")
    tags: list[Tag] = Field(default_factory=list)
    ownership: Ownership | None = None
    owner_info: OwnerInfo | None = None
    source: Source | None = None
    source_system: str | None = None
    source_type: SourceType | None = None
    freshness: str | None = None
    refresh_frequency: str | None = None
    contract_name: str | None = None
    contract_version: str | None = None
    data_product: DataProduct | None = None
    quality: Quality | None = None
    classification: Classification | None = None
    lifecycle: Lifecycle | None = None


class MetadataUpdate(InputModel):
    data_asset: DataAsset | None = None
    table_name: str | None = Field(default=None, min_length=1)
    description: str | None = None
    business_domain: str | None = None
    domain: str | None = None
    schema_: list[SchemaField] | None = Field(default=None, alias="schema")
    tags: list[Tag] | None = None
    ownership: Ownership | None = None
    owner_info: OwnerInfo | None = None
    source: Source | None = None
    source_system: str | None = None
    source_type: SourceType | None = None
    freshness: str | None = None
    refresh_frequency: str | None = None
    contract_name: str | None = None
    contract_version: str | None = None
    data_product: DataProduct | None = None
    quality: Quality | None = None
    classification: Classification | None = None
    lifecycle: Lifecycle | None = None


class MetadataReplace(MetadataCreate):
    @model_validator(mode="after")
    def require_complete_metadata(self):
        if self.data_asset is None and self.table_name is None:
            raise ValueError("PUT exige data_asset ou table_name.")
        if self.ownership is None and self.owner_info is None:
            raise ValueError("PUT exige ownership ou owner_info.")
        if self.source is None and (not self.source_system or not self.source_type):
            raise ValueError("PUT exige source ou source_system/source_type.")
        if not self.schema_:
            raise ValueError("PUT exige um schema não vazio.")
        return self


class MetadataOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    metadata_version: int = Field(default=1, alias="version")
    data_asset: DataAsset | None = None
    data_asset_key: str | None = None
    table_name: str
    description: str | None = None
    business_domain: str | None = None
    domain: str | None = None
    schema_: list[SchemaField] = Field(default_factory=list, alias="schema")
    tags: list[Tag] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    owner_info: OwnerInfo | None = None
    ownership: Ownership | None = None
    source: Source | None = None
    source_system: str | None = None
    source_type: SourceType | None = None
    freshness: str | None = None
    refresh_frequency: str | None = None
    contract_name: str | None = None
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
    data_asset: DataAsset | None = None
    data_asset_key: str | None = None
    table_name: str | None = None
    description: str | None = None
    domain: str | None = None
    business_domain: str | None = None
    data_product: DataProduct | None = None
    ownership: Ownership | None = None
    source: Source | None = None
    schema_: list[SchemaField] = Field(default_factory=list, alias="schema")
    tags: list[Tag] = Field(default_factory=list)
    owner_info: OwnerInfo | None = None
    source_system: str | None = None
    source_type: SourceType | None = None
    freshness: str | None = None
    refresh_frequency: str | None = None
    contract_name: str | None = None
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
