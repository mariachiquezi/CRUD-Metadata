import re
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

SourceType = Literal["database", "api", "file", "stream"]
Tag = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class InputModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid", populate_by_name=True)


class SchemaField(InputModel):
    name: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)
    nullable: bool = True
    unique: bool = False
    description: str | None = None


class DataProduct(InputModel):
    name: str = Field(..., min_length=1)
    description: str | None = None


class DataAsset(InputModel):
    name: str = Field(..., min_length=1)
    type: str = Field(default="table", min_length=1)


class Ownership(InputModel):
    owner: str = Field(..., min_length=1)
    steward: str | None = None
    email: str | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is not None and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("email invalido")
        return value


class Source(InputModel):
    system: str = Field(..., min_length=1)
    type: SourceType
    database: str | None = None
    table: str | None = None
    location: str | None = Field(default=None, min_length=1)


class Freshness(InputModel):
    max_delay: str = Field(..., pattern=r"^[1-9][0-9]*(s|m|h|d)$")


class CompletenessRule(InputModel):
    field: str = Field(..., min_length=1)
    threshold: float = Field(..., ge=0, le=100, allow_inf_nan=False)


class Quality(InputModel):
    freshness: Freshness | None = None
    completeness: list[CompletenessRule] = Field(default_factory=list)


class Classification(InputModel):
    data_classification: str = Field(..., min_length=1)


class Lifecycle(InputModel):
    status: Literal["active", "deprecated", "draft"]
