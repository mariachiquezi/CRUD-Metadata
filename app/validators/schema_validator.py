from app.models.data_asset import Quality, SchemaField


def validate_schema(fields: list[SchemaField], quality: Quality | None = None) -> None:
    """Cross-field rules shared by JSON metadata and YAML contracts."""
    if not fields:
        raise ValueError("O schema deve possuir pelo menos um campo.")

    names: set[str] = set()
    for field in fields:
        if field.name in names:
            raise ValueError(f"Campo duplicado no schema: {field.name}")
        names.add(field.name)

    if quality is not None:
        completeness_fields: set[str] = set()
        for rule in quality.completeness:
            if rule.field not in names:
                raise ValueError(
                    f"Regra de completeness referencia campo inexistente: {rule.field}"
                )
            if rule.field in completeness_fields:
                raise ValueError(f"Regra de completeness duplicada para o campo: {rule.field}")
            completeness_fields.add(rule.field)
