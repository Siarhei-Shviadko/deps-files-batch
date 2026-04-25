from typing import Optional

from deps_files_batch.domain.model import (
    Batch,
    BatchFiltering,
    BatchInfo,
    BatchSortBy,
    BatchSorting,
    BatchSortOrder,
    IQueryBatchRepository,
    ListBatchInfo,
    Pagination,
)

from .batch_info_mapper import BatchInfoMapper
from .batch_list_mapper import ListBatchInfoMapper

__all__ = ["FakeQueryBatchRepository"]

BatchIdTenantId = tuple[str, str]


class FakeQueryBatchRepository(IQueryBatchRepository):
    def __init__(self):
        self._storage: dict[BatchIdTenantId, Batch] = {}

    def find_all_with(
        self,
        filtering: BatchFiltering,
        sorting: BatchSorting,
        pagination: Pagination,
    ) -> ListBatchInfo:
        all_batches = self._find_all()

        filtered_batches = self._apply_filters(all_batches, filtering)
        sorted_batches = self._sort_batches(filtered_batches, sorting)
        total = len(sorted_batches)

        paginated_batches = self._apply_pagination(sorted_batches, pagination)

        return ListBatchInfoMapper.from_models(
            batches=paginated_batches, total=total, group_names=["" for _ in paginated_batches]
        )

    def batch_of_id(self, batch_id: str, tenant_id: str) -> Optional[Batch]:
        return self._storage.get((batch_id, tenant_id))

    def save(self, batch: Batch) -> None:
        self._storage[(batch.id(), batch.tenant_id())] = batch

    def _find_all(self) -> list[Batch]:
        return list(self._storage.values())

    def _apply_filters(self, batches: list[Batch], filter_: BatchFiltering) -> list[Batch]:
        batches = [batch for batch in batches if self._accept_value(batch, filter_)]
        return batches

    def _accept_value(self, batch: Batch, filter_: BatchFiltering) -> bool:
        accept = True

        if filter_.tenant_id is not None:
            accept = accept and batch.tenant_id() == filter_.tenant_id

        if filter_.group is not None:
            accept = accept and batch.group_id and batch.group_id.value == filter_.group

        if filter_.name is not None:
            accept = accept and filter_.name.lower() in batch.name.lower()

        if filter_.status is not None:
            accept = accept and batch.status in filter_.status

        if filter_.date_start is not None:
            accept = accept and filter_.date_start <= batch.created_at

        if filter_.date_end is not None:
            accept = accept and filter_.date_end >= batch.created_at

        return accept

    @staticmethod
    def _sort_batches(batches: list[Batch], sorting: BatchSorting) -> list[Batch]:
        def _key(batch):
            if sorting.sort_by == BatchSortBy.NAME:
                return batch.name
            elif sorting.sort_by == BatchSortBy.STATUS:
                return batch.status
            return batch.created_at

        return sorted(batches, key=_key, reverse=sorting.sort_order == BatchSortOrder.ASC)

    @staticmethod
    def _apply_pagination(batches: list[Batch], pagination: Pagination) -> list[Batch]:
        start_index = min(pagination.per_page * pagination.page, len(batches))
        end_index = min(pagination.per_page * (pagination.page + 1), len(batches))
        return batches[start_index:end_index]

    def find_batch(self, batch_id: str, tenant_id: str) -> BatchInfo | None:
        if batch := self._storage.get((batch_id, tenant_id)):
            return BatchInfoMapper.from_model(batch=batch, group_name="a")
        return None
