from datetime import datetime

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path, Response
from fastapi import status as http_status
from fastapi.params import Query

from deps_files_batch.application import BatchService, QueryBatchService
from deps_files_batch.constants import DEFAULT_PAGE, DEFAULT_PER_PAGE
from deps_files_batch.containers import Containers
from deps_files_batch.domain.model import BatchSortBy, BatchSortOrder

from ...auth import get_current_user_tenant
from ...endpoint_marker import MarkerRoute
from ...endpoint_visibility import Visibility
from ...serializers import (
    AddBatchFilesRequest,
    BatchCreateResponse,
    BatchRequestSerializer,
    BatchUpdateRequest,
    GetBatchesResponse,
    SerializedBatchInfo,
)

__all__ = ["batch_router"]

batch_router = APIRouter(prefix="/batches", tags=["Batches"], route_class=MarkerRoute)


@batch_router.post(
    "",
    status_code=http_status.HTTP_201_CREATED,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_model=BatchCreateResponse,
)
@inject
def create_batch(
    create_batch_request: BatchRequestSerializer,
    current_tenant: str = Depends(get_current_user_tenant),
    batch_service: BatchService = Depends(Provide[Containers.batch_service]),
):
    batch = batch_service.create_batch(
        batch_name=create_batch_request.name,
        tenant_id=current_tenant,
        group_id=create_batch_request.group_id,
        batch_metadata=create_batch_request.metadata,
        file_params=create_batch_request.file_parameters,
    )
    return BatchCreateResponse(batch_id=batch.id())


@batch_router.get(
    "",
    status_code=http_status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_model=GetBatchesResponse,
)
@inject
def get_batches(
    tenant_id: str = Depends(get_current_user_tenant),
    status: list[str] | None = Query(default=None),
    name: str | None = Query(default=None),
    group: str | None = Query(default=None),
    date_start: datetime | None = Query(default=None, alias="dateStart"),
    date_end: datetime | None = Query(default=None, alias="dateEnd"),
    page: int = Query(default=DEFAULT_PAGE, ge=0),
    per_page: int = Query(default=DEFAULT_PER_PAGE, alias="perPage", ge=0),
    sort_by: BatchSortBy = Query(default=BatchSortBy.CREATED_AT, alias="sortBy"),
    sort_order: BatchSortOrder = Query(default=BatchSortOrder.DESC, alias="sortOrder"),
    query_batch_service: QueryBatchService = Depends(Provide[Containers.query_batch_service]),
):
    return GetBatchesResponse(
        **query_batch_service.find_all_with(
            tenant_id=tenant_id,
            name=name,
            status=status,
            group=group,
            date_start=date_start,
            date_end=date_end,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
        ),
    )


@batch_router.get(
    "/{batchId}",
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_model=SerializedBatchInfo,
)
@inject
def get_batch_info(
    batch_id: str = Path(..., alias="batchId"),
    current_tenant: str = Depends(get_current_user_tenant),
    batch_service: QueryBatchService = Depends(Provide[Containers.query_batch_service]),
) -> SerializedBatchInfo:
    return SerializedBatchInfo(**batch_service.find_batch(batch_id=batch_id, tenant_id=current_tenant))


@batch_router.patch(
    "/{batchId}",
    status_code=http_status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_class=Response,
)
@inject
def rename_batch(
    update_request: BatchUpdateRequest,
    batch_id: str = Path(..., alias="batchId"),
    current_tenant: str = Depends(get_current_user_tenant),
    batch_service: BatchService = Depends(Provide[Containers.batch_service]),
):
    batch_service.rename_batch(batch_id=batch_id, tenant_id=current_tenant, new_name=update_request.name)


@batch_router.delete(
    "",
    status_code=http_status.HTTP_204_NO_CONTENT,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def delete_batches(
    ids: set[str] = Query(...),
    current_tenant: str = Depends(get_current_user_tenant),
    batch_service: BatchService = Depends(Provide[Containers.batch_service]),
):
    batch_service.delete_batches(ids=ids, tenant_id=current_tenant)


@batch_router.delete(
    "/with-documents",
    status_code=http_status.HTTP_204_NO_CONTENT,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def delete_batches_with_documents(
    ids: set[str] = Query(...),
    current_tenant: str = Depends(get_current_user_tenant),
    batch_service: BatchService = Depends(Provide[Containers.batch_service]),
):
    batch_service.delete_batches_with_documents(ids=ids, tenant_id=current_tenant)


@batch_router.delete(
    "/{batchId}/files",
    status_code=http_status.HTTP_204_NO_CONTENT,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def delete_files(
    batch_id: str = Path(..., alias="batchId"),
    file_ids: list[str] = Query(..., alias="ids"),
    current_tenant: str = Depends(get_current_user_tenant),
    batch_service: BatchService = Depends(Provide[Containers.batch_service]),
):
    batch_service.delete_files(batch_id=batch_id, file_ids=file_ids, tenant_id=current_tenant)


@batch_router.delete(
    "/{batchId}/files/with-documents",
    status_code=http_status.HTTP_204_NO_CONTENT,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def delete_files_with_documents(
    batch_id: str = Path(..., alias="batchId"),
    file_ids: list[str] = Query(..., alias="ids"),
    current_tenant: str = Depends(get_current_user_tenant),
    batch_service: BatchService = Depends(Provide[Containers.batch_service]),
):
    batch_service.delete_files_with_documents(batch_id=batch_id, file_ids=file_ids, tenant_id=current_tenant)


@batch_router.post(
    "/{batchId}/files",
    status_code=http_status.HTTP_201_CREATED,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_class=Response,
)
@inject
def add_files(
    add_batch_files_request: AddBatchFilesRequest,
    batch_id: str = Path(..., alias="batchId"),
    current_tenant: str = Depends(get_current_user_tenant),
    batch_service: BatchService = Depends(Provide[Containers.batch_service]),
):
    batch_service.add_files(
        batch_id=batch_id,
        tenant_id=current_tenant,
        file_params=add_batch_files_request.files_parameters,
    )
