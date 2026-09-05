from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from app.auth.security import get_current_user, require_roles

from app.models.metadata import (
    MetadataCreate,
    MetadataListResponse,
    MetadataOut,
    MetadataUpdate,
    MetadataVersionEntry,
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
    dependencies=[Depends(require_roles("admin", "editor"))],
)
def create_metadata(
    payload: MetadataCreate, current_user: dict = Depends(get_current_user)
):

    return service.create(payload, current_user["username"])


@router.get("", response_model=MetadataListResponse, dependencies=[Depends(require_roles("admin", "editor", "viewer"))])
def list_metadata(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    domain: str | None = None,
    owner: str | None = None,
    table_name: str | None = None,
    source_system: str | None = None,
):

    items, total = service.list(
        page, page_size, domain, owner, table_name, source_system
    )

    return MetadataListResponse(
        items=items, total=total, page=page, page_size=page_size
    )


@router.get("/history", response_model=list[MetadataVersionEntry], dependencies=[Depends(require_roles("admin", "editor", "viewer"))])
def list_all_metadata_history():
    return service.list_all_history()


@router.get("/{metadata_id}", response_model=MetadataOut, dependencies=[Depends(require_roles("admin", "editor", "viewer"))])
def get_metadata(metadata_id: str):

    item = service.get_by_id(metadata_id)

    if item is None:
        raise HTTPException(status_code=404, detail="Metadado não encontrado.")

    return item


@router.get("/{metadata_id}/history", response_model=list[MetadataVersionEntry], dependencies=[Depends(require_roles("admin", "editor", "viewer"))])
def get_metadata_history(metadata_id: str):
    history = service.list_history(metadata_id)

    if not history and service.get_by_id(metadata_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Metadado não encontrado.",
        )

    return history


@router.put("/{metadata_id}", response_model=MetadataOut, dependencies=[Depends(require_roles("admin", "editor"))])
def update_metadata(
    metadata_id: str,
    payload: MetadataCreate,
    current_user: dict = Depends(get_current_user),
):

    item = service.update(
        metadata_id, payload, current_user["username"], replace=True
    )

    if item is None:
        raise HTTPException(status_code=404, detail="Metadado não encontrado.")
    return item


@router.patch("/{metadata_id}", response_model=MetadataOut, dependencies=[Depends(require_roles("admin", "editor"))])
def patch_metadata(
    metadata_id: str,
    payload: MetadataUpdate,
    current_user: dict = Depends(get_current_user),
):
    item = service.update(metadata_id, payload, current_user["username"])

    if item is None:
        raise HTTPException(status_code=404, detail="Metadado não encontrado.")
    return item


@router.delete("/{metadata_id}", dependencies=[Depends(require_roles("admin"))])
def delete_metadata(metadata_id: str, current_user: dict = Depends(get_current_user)):

    deleted = service.delete(metadata_id, current_user["username"])

    if not deleted:
        raise HTTPException(status_code=404, detail="Metadado não encontrado.")

    return {
        "deleted": True,
        "mensagem": "Metadado removido do catálogo principal. O histórico foi preservado.",
    }
