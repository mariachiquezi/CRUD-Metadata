from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from app.auth.security import get_current_user, require_roles
from app.dependencies import metadata_service
from app.models.metadata import (
    MetadataCreate,
    MetadataListResponse,
    MetadataOut,
    MetadataReplace,
    MetadataUpdate,
    MetadataVersionEntry,
)

router = APIRouter(prefix="/metadata")

service = metadata_service


def get_metadata_service():
    return service


@router.post(
    "",
    tags=["metadata"],
    response_model=MetadataOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin", "editor"))],
)
def create_metadata(
    payload: MetadataCreate,
    current_user: dict = Depends(get_current_user),
    catalog=Depends(get_metadata_service),
):
    return catalog.create(payload, current_user["username"])


@router.get(
    "",
    tags=["metadata"],
    response_model=MetadataListResponse,
    dependencies=[Depends(require_roles("admin", "editor", "viewer"))],
)
def list_metadata(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    domain: str | None = None,
    owner: str | None = None,
    asset_name: str | None = None,
    catalog=Depends(get_metadata_service),
):
    items, total = catalog.list(page, page_size, domain, owner, asset_name)

    return MetadataListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get(
    "/history",
    tags=["metadata-history"],
    response_model=list[MetadataVersionEntry],
    dependencies=[Depends(require_roles("admin", "editor", "viewer"))],
)
def list_all_metadata_history(catalog=Depends(get_metadata_service)):
    return catalog.list_all_history()


@router.get(
    "/{metadata_id}",
    tags=["metadata"],
    response_model=MetadataOut,
    dependencies=[Depends(require_roles("admin", "editor", "viewer"))],
)
def get_metadata(metadata_id: str, catalog=Depends(get_metadata_service)):
    item = catalog.get_by_id(metadata_id)

    if item is None:
        raise HTTPException(status_code=404, detail="Metadado não encontrado.")

    return item


@router.get(
    "/{metadata_id}/history",
    tags=["metadata-history"],
    response_model=list[MetadataVersionEntry],
    dependencies=[Depends(require_roles("admin", "editor", "viewer"))],
)
def get_metadata_history(metadata_id: str, catalog=Depends(get_metadata_service)):
    history = catalog.list_history(metadata_id)

    if not history and catalog.get_by_id(metadata_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Metadado não encontrado.",
        )

    return history


@router.put(
    "/{metadata_id}",
    tags=["metadata"],
    response_model=MetadataOut,
    dependencies=[Depends(require_roles("admin", "editor"))],
)
def update_metadata(
    metadata_id: str,
    payload: MetadataReplace,
    current_user: dict = Depends(get_current_user),
    catalog=Depends(get_metadata_service),
):
    item = catalog.replace(
        metadata_id,
        payload,
        current_user["username"],
    )

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Metadado não encontrado.",
        )

    return item


@router.patch(
    "/{metadata_id}",
    tags=["metadata"],
    response_model=MetadataOut,
    dependencies=[Depends(require_roles("admin", "editor"))],
)
def patch_metadata(
    metadata_id: str,
    payload: MetadataUpdate,
    current_user: dict = Depends(get_current_user),
    catalog=Depends(get_metadata_service),
):
    item = catalog.patch(
        metadata_id,
        payload,
        current_user["username"],
    )

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Metadado não encontrado.",
        )

    return item


@router.delete(
    "/{metadata_id}",
    tags=["metadata"],
    dependencies=[Depends(require_roles("admin"))],
)
def delete_metadata(
    metadata_id: str,
    current_user: dict = Depends(get_current_user),
    catalog=Depends(get_metadata_service),
):
    deleted = catalog.delete(metadata_id, current_user["username"])

    if not deleted:
        raise HTTPException(status_code=404, detail="Metadado não encontrado.")

    return {
        "deleted": True,
        "mensagem": "Metadado removido do catálogo principal. O histórico foi preservado.",
    }
