import re
from typing import Any

from app.exceptions.domain import (
    ContractAlreadyExistsError,
    InvalidContractVersionError,
)


class ContractVersionPolicy:
    """Aplica as regras de evolução da versão de um contrato."""

    def parse(self, version: Any) -> tuple[int, ...]:
        text = str(version)
        if not re.fullmatch(r"\d+(?:\.\d+)*", text):
            raise InvalidContractVersionError("0.0", text)
        try:
            parts = tuple(int(part) for part in text.split("."))
        except (AttributeError, ValueError):
            raise InvalidContractVersionError("0.0", text) from None
        if not parts or any(part < 0 for part in parts):
            raise InvalidContractVersionError("0.0", text)
        while len(parts) > 1 and parts[-1] == 0:
            parts = parts[:-1]
        return parts

    def validate_next(
        self,
        current_version: Any,
        requested_version: Any,
        data_asset_key: str,
    ) -> None:
        if requested_version is None or current_version is None:
            return

        current = str(current_version)
        requested = str(requested_version)
        current_parts = self.parse(current)
        requested_parts = self.parse(requested)

        if requested_parts == current_parts:
            raise ContractAlreadyExistsError(data_asset_key, requested)
        if requested_parts <= current_parts:
            raise InvalidContractVersionError(current, requested)

    def is_major_upgrade(self, current_version: Any, requested_version: Any) -> bool:
        if current_version is None or requested_version is None:
            return False
        return self.parse(requested_version)[0] > self.parse(current_version)[0]
