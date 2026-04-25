from dataclasses import dataclass

from deps_files_batch.domain.model.shared import ExtendedEnum

__all__ = ["BatchSortBy", "BatchSorting", "BatchSortOrder"]


class BatchSortOrder(ExtendedEnum):
    ASC = "asc"
    DESC = "desc"


class BatchSortBy(ExtendedEnum):
    CREATED_AT = "createdAt"
    NAME = "name"
    STATUS = "status"
    GROUP = "group"


@dataclass
class BatchSorting:
    sort_by: BatchSortBy = BatchSortBy.CREATED_AT
    sort_order: BatchSortOrder = BatchSortOrder.DESC
