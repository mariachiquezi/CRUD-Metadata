from datetime import datetime
import re
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SchemaField(BaseModel):
    name: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)
    nullable: bool = True
    unique: bool = False
    description: Optional[str] = None


class OwnerInfo(BaseModel):
    team: str = Field(..., min_length=1)
    email: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("email invalido")
        return value


class DataProduct(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None


class DataAsset(BaseModel):
    name: str = Field(..., min_length=1)
    type: str = Field(default="table", min_length=1)


class Ownership(BaseModel):
    owner: str = Field(..., min_length=1)
    steward: Optional[str] = None


class Source(BaseModel):
    system: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)
    database: Optional[str] = None
    table: Optional[str] = None


class Freshness(BaseModel):
    max_delay: str = Field(..., min_length=1)


class CompletenessRule(BaseModel):
    field: str = Field(..., min_length=1)
    threshold: float = Field(..., ge=0, le=100)


class Quality(BaseModel):
    freshness: Optional[Freshness] = None
    completeness: List[CompletenessRule] = Field(default_factory=list)


class Classification(BaseModel):
    data_classification: str = Field(..., min_length=1)


class Lifecycle(BaseModel):
    status: str = Field(..., min_length=1)


class MetadataCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    version: int = 1
    data_asset: Optional[DataAsset] = None
    data_asset_key: Optional[str] = None
    table_name: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    business_domain: Optional[str] = None
    domain: Optional[str] = None
    schema_: List[SchemaField] = Field(default_factory=list, alias="schema")
    tags: List[str] = Field(default_factory=list)
    ownership: Optional[Ownership] = None
    owner_info: Optional[OwnerInfo] = None
    source: Optional[Source] = None
    source_system: Optional[str] = None
    source_type: Optional[str] = None
    freshness: Optional[str] = None
    refresh_frequency: Optional[str] = None
    contract_name: Optional[str] = None
    contract_version: Optional[str] = None
    data_product: Optional[DataProduct] = None
    quality: Optional[Quality] = None
    classification: Optional[Classification] = None
    lifecycle: Optional[Lifecycle] = None


class MetadataUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    data_asset: Optional[DataAsset] = None
    data_asset_key: Optional[str] = None
    table_name: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    business_domain: Optional[str] = None
    domain: Optional[str] = None
    schema_: Optional[List[SchemaField]] = Field(default=None, alias="schema")
    tags: Optional[List[str]] = None
    ownership: Optional[Ownership] = None
    owner_info: Optional[OwnerInfo] = None
    source: Optional[Source] = None
    source_system: Optional[str] = None
    source_type: Optional[str] = None
    freshness: Optional[str] = None
    refresh_frequency: Optional[str] = None
    contract_name: Optional[str] = None
    contract_version: Optional[str] = None
    data_product: Optional[DataProduct] = None
    quality: Optional[Quality] = None
    classification: Optional[Classification] = None
    lifecycle: Optional[Lifecycle] = None


class MetadataOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    version: int = 1
    data_asset: Optional[DataAsset] = None
    data_asset_key: Optional[str] = None
    table_name: str
    description: Optional[str] = None
    business_domain: Optional[str] = None
    domain: Optional[str] = None
    schema_: List[SchemaField] = Field(default_factory=list, alias="schema")
    tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    owner_info: Optional[OwnerInfo] = None
    source_system: Optional[str] = None
    source_type: Optional[str] = None
    freshness: Optional[str] = None
    refresh_frequency: Optional[str] = None
    contract_name: Optional[str] = None
    contract_version: Optional[str] = None
    data_product: Optional[DataProduct] = None
    quality: Optional[Quality] = None
    classification: Optional[Classification] = None
    lifecycle: Optional[Lifecycle] = None


class MetadataListResponse(BaseModel):
    items: List[MetadataOut]
    total: int
    page: int = 1
    page_size: int = 0


class MetadataVersionEntry(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    version: int
    metadata_id: str
    data_asset: Optional[DataAsset] = None
    data_asset_key: Optional[str] = None
    table_name: Optional[str] = None
    description: Optional[str] = None
    schema_: List[SchemaField] = Field(default_factory=list, alias="schema")
    tags: List[str] = Field(default_factory=list)
    owner_info: Optional[OwnerInfo] = None
    source_system: Optional[str] = None
    source_type: Optional[str] = None
    freshness: Optional[str] = None
    refresh_frequency: Optional[str] = None
    contract_name: Optional[str] = None
    contract_version: Optional[str] = None
    quality: Optional[Quality] = None
    classification: Optional[Classification] = None
    lifecycle: Optional[Lifecycle] = None
    deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None
    changed_at: datetime
    changed_by: str
    change_type: str = "UPDATE"


class SchemaHistoryEntry(MetadataVersionEntry):
    pass
