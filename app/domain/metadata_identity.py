from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DataAssetIdentity:
    """Value object que identifica um ativo de dados no catálogo."""

    name: str
    domain: str | None = None

    @classmethod
    def from_document(cls, data: dict[str, Any]) -> "DataAssetIdentity":
        asset = data["data_asset"]
        return cls(name=asset["name"], domain=data.get("domain"))

    @property
    def key(self) -> str:
        return f"{self.domain}.{self.name}" if self.domain else self.name
