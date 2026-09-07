import re
from typing import Any

from app.exceptions.domain import (
    ContractAlreadyExistsError,
    InvalidContractVersionError,
)


def version_parts(version: Any) -> tuple[int, ...]:
    if not re.fullmatch(r"\d+(?:\.\d+)*", str(version)):
        raise InvalidContractVersionError("0.0", str(version))
    try:
        parts = tuple(int(part) for part in str(version).split("."))
    except (AttributeError, ValueError):
        raise InvalidContractVersionError("0.0", str(version)) from None
    if not parts or any(part < 0 for part in parts):
        raise InvalidContractVersionError("0.0", str(version))
    while len(parts) > 1 and parts[-1] == 0:
        parts = parts[:-1]
    return parts


def validate_next_contract_version(
    current_version: Any,
    requested_version: Any,
    data_asset_key: str,
) -> None:
    if requested_version is None or current_version is None:
        return

    current = str(current_version)
    requested = str(requested_version)
    current_parts = version_parts(current)
    requested_parts = version_parts(requested)

    if requested_parts == current_parts:
        raise ContractAlreadyExistsError(data_asset_key, requested)
    if requested_parts <= current_parts:
        raise InvalidContractVersionError(current, requested)


def is_major_version_upgrade(current_version: Any, requested_version: Any) -> bool:
    """Return whether the requested contract version changes the major number."""
    if current_version is None or requested_version is None:
        return False
    return version_parts(requested_version)[0] > version_parts(current_version)[0]
