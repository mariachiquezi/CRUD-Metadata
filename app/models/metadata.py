from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SchemaField(BaseModel):
    name: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)
    nullable: bool = True
    unique: bool = False
    description: Optional[str] = None


class OwnerInfo(BaseModel):
    team: str = Field(..., min_length=1)
    email: Optional[str] = None


class DataProduct(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None


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
    table_name: str = Field(..., min_length=1)
    description: Optional[str] = None
    business_domain: Optional[str] = None
    domain: Optional[str] = None
    schema: List[SchemaField] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    owner_info: OwnerInfo
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

    table_name: Optional[str] = None

    description: Optional[str] = None

    business_domain: Optional[str] = None

    domain: Optional[str] = None

    schema: Optional[List[SchemaField]] = None

    tags: Optional[List[str]] = None

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


class MetadataOut(BaseModel):
    id: str
    table_name: str
    description: Optional[str] = None
    business_domain: Optional[str] = None
    domain: Optional[str] = None
    schema: List[SchemaField] = Field(default_factory=list)
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


class SchemaHistoryEntry(BaseModel):

    version: int

    metadata_id: str

    table_name: Optional[str]

    description: Optional[str]

    schema: List[SchemaField]

    tags: List[str]

    owner_info: Optional[OwnerInfo]

    source_system: Optional[str]

    source_type: Optional[str]

    freshness: Optional[str]

    refresh_frequency: Optional[str]

    contract_name: Optional[str]

    contract_version: Optional[str]

    quality: Optional[Quality]

    classification: Optional[Classification]

    lifecycle: Optional[Lifecycle]

    changed_at: datetime

    changed_by: str
