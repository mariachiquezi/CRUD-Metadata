from datetime import UTC, datetime
from typing import Any, Literal

from app.models.metadata import MetadataOut, MetadataVersionEntry

ChangeType = Literal["CREATE", "UPDATE", "DELETE"]


def now_utc() -> datetime:
    return datetime.now(UTC)


def to_utc(value: datetime | str) -> datetime:
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


def build_history_entry(data: dict[str, Any], actor: str, change_type: ChangeType) -> dict:
    values = {key: value for key, value in data.items() if key != "_id"}
    values.update(
        metadata_id=data["_id"],
        changed_at=data["updated_at"],
        changed_by=actor,
        change_type=change_type,
    )
    if change_type == "DELETE":
        values.update(deleted=True, deleted_at=data["updated_at"], deleted_by=actor)
    return MetadataVersionEntry.model_validate(values).model_dump(by_alias=True)


def normalize_history(documents: list[dict[str, Any]]) -> list[MetadataVersionEntry]:
    result = []
    for source in documents:
        document = dict(source)
        for field in ("changed_at", "deleted_at"):
            if document.get(field) is not None:
                document[field] = to_utc(document[field])
        document.setdefault("changed_by", "system")
        result.append(MetadataVersionEntry.model_validate(document))
    return result


def to_response(document: dict[str, Any]) -> MetadataOut:
    data = {**document, "id": str(document["_id"])}
    for field in ("created_at", "updated_at"):
        data[field] = to_utc(data[field])
    return MetadataOut.model_validate(data)
