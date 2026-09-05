from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List


class ContractField(BaseModel):
    name: str
    type: str
    nullable: bool = True
    unique: bool = False
    description: Optional[str] = None


class Ownership(BaseModel):
    owner: str
    steward: Optional[str] = None


class DataProduct(BaseModel):
    name: str
    description: Optional[str] = None


class DataAsset(BaseModel):
    name: str
    type: str = "table"


class Source(BaseModel):
    system: str
    type: str
    database: Optional[str] = None
    table: Optional[str] = None


class Freshness(BaseModel):
    max_delay: str


class CompletenessRule(BaseModel):
    field: str
    threshold: float = Field(ge=0, le=100)


class Quality(BaseModel):
    freshness: Optional[Freshness] = None
    completeness: List[CompletenessRule] = Field(default_factory=list)


class Classification(BaseModel):
    data_classification: str


class Lifecycle(BaseModel):
    status: str


class ContractDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    data_asset: Optional[DataAsset] = None
    name: Optional[str] = None
    version: str
    data_product: Optional[DataProduct] = None
    ownership: Ownership
    source: Source
    domain: str
    schema_: List[ContractField] = Field(..., alias="schema")
    quality: Optional[Quality] = None
    classification: Optional[Classification] = None
    lifecycle: Optional[Lifecycle] = None


class DataContract(BaseModel):
    contract: ContractDefinition
