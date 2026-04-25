from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from deps_files_batch.api.endpoint_marker import MarkerRoute
from deps_files_batch.api.endpoint_visibility import Visibility
from deps_files_batch.containers import Datasources
from deps_files_batch.extras import DatabaseSession

__all__ = ["healthcheck_router"]

healthcheck_router = APIRouter(route_class=MarkerRoute)


@healthcheck_router.get(
    "/healthcheck",
    tags=["Debug"],
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def service_healthcheck(datasource: DatabaseSession = Depends(Provide[Datasources.postgres_session])):
    """Check connection to database."""
    try:
        datasource.healthcheck()
    except Exception:
        return JSONResponse(content={}, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return JSONResponse(content={}, status_code=status.HTTP_200_OK)
