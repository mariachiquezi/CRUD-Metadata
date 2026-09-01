from pydantic import BaseModel, Field
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
    completeness: List[CompletenessRule] = []


class Classification(BaseModel):
    data_classification: str


class Lifecycle(BaseModel):
    status: str


class ContractDefinition(BaseModel):
    name: str
    version: str

    data_product: Optional[DataProduct] = None

    ownership: Ownership

    source: Source

    domain: str

    schema: List[ContractField]

    quality: Optional[Quality] = None

    classification: Optional[Classification] = None

    lifecycle: Optional[Lifecycle] = None


class DataContract(BaseModel):
    contract: ContractDefinition
