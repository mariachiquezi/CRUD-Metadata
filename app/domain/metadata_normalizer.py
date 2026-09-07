from typing import Any


def normalize_asset_data(data: dict[str, Any]) -> dict[str, Any]:
    """Keep canonical and legacy metadata fields consistent."""
    normalized = dict(data)
    pairs = [
        ("data_asset", "name", "table_name"),
        ("source", "system", "source_system"),
        ("source", "type", "source_type"),
    ]
    for nested, key, flat in pairs:
        if normalized.get(nested):
            value = normalized[nested][key]
            if normalized.get(flat) and normalized[flat] != value:
                raise ValueError(f"{nested}.{key} e {flat} devem ser iguais.")
            normalized[flat] = value

    if normalized.get("table_name") and not normalized.get("data_asset"):
        normalized["data_asset"] = {"name": normalized["table_name"], "type": "table"}

    if normalized.get("domain") is not None:
        normalized["business_domain"] = normalized["domain"]
    elif normalized.get("business_domain") is not None:
        normalized["domain"] = normalized["business_domain"]

    quality = normalized.get("quality")
    freshness = quality.get("freshness") if quality else None
    if freshness:
        if normalized.get("freshness") and normalized["freshness"] != freshness["max_delay"]:
            raise ValueError("freshness e quality.freshness.max_delay devem ser iguais.")
        normalized["freshness"] = freshness["max_delay"]
    elif "quality" in normalized and not normalized.get("freshness"):
        normalized["freshness"] = None

    return normalized


def data_asset_key(data: dict[str, Any]) -> str:
    name = data["table_name"]
    domain = data.get("domain") or data.get("business_domain")
    return f"{domain}.{name}" if domain else name
