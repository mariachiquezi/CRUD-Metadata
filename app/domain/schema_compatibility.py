from collections.abc import Mapping
from typing import Any

from app.exceptions.domain import IncompatibleSchemaError


class SchemaCompatibilityPolicy:
    """Define quais mudanças de schema podem evoluir um contrato."""

    def validate(
        self,
        current: Mapping[str, Any],
        requested: Mapping[str, Any],
        *,
        allow_type_change: bool = False,
    ) -> None:
        current_schema = {field.get("name"): field for field in current.get("schema", [])}
        requested_schema = {field.get("name"): field for field in requested.get("schema", [])}
        current_fields = set(current_schema)
        requested_fields = set(requested_schema)

        for field_name in requested_fields - current_fields:
            if not requested_schema[field_name].get("nullable", True):
                raise IncompatibleSchemaError(field_name, "foi adicionado como obrigatório")

        removed_fields = current_fields - requested_fields
        if removed_fields:
            raise IncompatibleSchemaError(sorted(removed_fields)[0])

        for field_name in current_fields & requested_fields:
            current_field = current_schema[field_name]
            requested_field = requested_schema[field_name]
            if not current_field.get("unique", False) and requested_field.get("unique", False):
                raise IncompatibleSchemaError(field_name, "passou a exigir unicidade")
            if not allow_type_change and current_field.get("type") != requested_field.get("type"):
                raise IncompatibleSchemaError(
                    field_name,
                    current_type=current_field.get("type"),
                    requested_type=requested_field.get("type"),
                )
            if current_field.get("nullable", True) and not requested_field.get("nullable", True):
                raise IncompatibleSchemaError(field_name, "deixou de aceitar nulos")
