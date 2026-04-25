from datetime import datetime

from deps_files_batch.domain.exceptions import BatchNotFound
from deps_files_batch.domain.model import (
    BatchFiltering,
    BatchInfo,
    BatchSortBy,
    BatchSorting,
    BatchSortOrder,
    IQueryBatchRepository,
    ListBatchInfo,
    Pagination,
)

__all__ = ["QueryBatchService"]


class QueryBatchService:
    def __init__(self, query_batch_repository: IQueryBatchRepository) -> None:
        self._query_batch_repository = query_batch_repository

    def find_batch(self, batch_id: str, tenant_id: str) -> BatchInfo:
        if batch := self._query_batch_repository.find_batch(batch_id=batch_id, tenant_id=tenant_id):
            return batch

        raise BatchNotFound(batch_id)

    def find_all_with(
        self,
        tenant_id: str,
        name: str | None,
        status: list[str] | None,
        group: str | None,
        date_start: datetime | None,
        date_end: datetime | None,
        page: int,
        per_page: int,
        sort_by: BatchSortBy,
        sort_order: BatchSortOrder,
    ) -> ListBatchInfo:
        return self._query_batch_repository.find_all_with(
            filtering=BatchFiltering(
                tenant_id=tenant_id,
                name=name,
                status=status,
                group=group,
                date_start=date_start,
                date_end=date_end,
            ),
            sorting=BatchSorting(sort_by=sort_by, sort_order=sort_order),
            pagination=Pagination(page=page, per_page=per_page),
        )
