from typing import List

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.models.metadata import (
    MetadataCreate,
    MetadataListResponse,
    MetadataOut,
    MetadataUpdate,
)

from app.services.metadata_service import (
    MetadataService,
)

router = APIRouter(prefix="/metadata", tags=["metadata"])

service = MetadataService()


@router.post(
    "",
    response_model=MetadataOut,
    status_code=status.HTTP_201_CREATED,
)
def create_metadata(payload: MetadataCreate):

    return service.create(payload)


@router.get("", response_model=MetadataListResponse)
def list_metadata():

    items = service.list()

    return MetadataListResponse(items=items, total=len(items))


@router.get("/{metadata_id}", response_model=MetadataOut)
def get_metadata(metadata_id: str):

    item = service.get_by_id(metadata_id)

    if item is None:

        raise HTTPException(status_code=404, detail="Metadata not found")

    return item


@router.put("/{metadata_id}", response_model=MetadataOut)
def update_metadata(metadata_id: str, payload: MetadataUpdate):

    item = service.update(metadata_id, payload)

    if item is None:

        raise HTTPException(status_code=404, detail="Metadata not found")

    return item


@router.delete("/{metadata_id}")
def delete_metadata(metadata_id: str):

    deleted = service.delete(metadata_id)

    if not deleted:

        raise HTTPException(status_code=404, detail="Metadata not found")

    return {"deleted": True}
