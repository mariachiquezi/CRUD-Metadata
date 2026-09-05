from datetime import datetime
import re
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


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
    version: int = 1
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
    version: int = 1
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
    page: int = 1
    page_size: int = 0


class MetadataVersionEntry(BaseModel):
    version: int
    metadata_id: str
    table_name: Optional[str] = None
    description: Optional[str] = None
    schema: List[SchemaField] = Field(default_factory=list)
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
