from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from deps_files_batch.application import BatchService
from deps_files_batch.containers import Containers

from ..auth import get_current_user_tenant
from ..serializers import BatchCreateFromFileResponse, BatchRequestSerializer

__all__ = ["internal_router"]

internal_router = APIRouter(prefix="/batches")


@internal_router.post(
    "/from-file",
    status_code=HTTPStatus.CREATED,
    response_model=BatchCreateFromFileResponse,
)
@inject
def create_batch_from_file(
    create_batch_request: BatchRequestSerializer,
    current_tenant: str = Depends(get_current_user_tenant),
    batch_service: BatchService = Depends(Provide[Containers.batch_service]),
) -> BatchCreateFromFileResponse:
    batch = batch_service.create_batch(
        batch_name=create_batch_request.name,
        tenant_id=current_tenant,
        group_id=create_batch_request.group_id,
        batch_metadata=create_batch_request.metadata,
        file_params=create_batch_request.file_parameters,
    )
    return BatchCreateFromFileResponse(batch_id=batch.id(), batch_name=batch.name)
