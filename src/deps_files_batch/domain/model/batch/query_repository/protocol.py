from typing import Protocol

from ..batch_info import BatchInfo
from ..batch_list_info import ListBatchInfo
from .filtering import BatchFiltering
from .pagination import Pagination
from .sorting import BatchSorting

__all__ = ["IQueryBatchRepository"]


class IQueryBatchRepository(Protocol):
    def find_all_with(
        self,
        filtering: BatchFiltering,
        sorting: BatchSorting,
        pagination: Pagination,
    ) -> ListBatchInfo:
        pass

    def find_batch(self, batch_id: str, tenant_id: str) -> BatchInfo | None:
        pass
