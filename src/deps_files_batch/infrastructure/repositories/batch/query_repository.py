from more_itertools import first

from deps_files_batch.domain.model import (
    BatchFiltering,
    BatchInfo,
    BatchSorting,
    IQueryBatchRepository,
    ListBatchInfo,
    Pagination,
)
from deps_files_batch.extras import DatabaseSession

from .mappers import BatchInfoMapper, BatchListMapper
from .query_query_factory import BatchQueryRepoQueryFactory

__all__ = ["QueryBatchRepository"]


class QueryBatchRepository(IQueryBatchRepository):
    def __init__(self, database: DatabaseSession) -> None:
        self._db = database
        self._query_factory = BatchQueryRepoQueryFactory()

    def find_batch(self, batch_id: str, tenant_id: str) -> BatchInfo | None:
        query = self._query_factory.find_batch(batch_id=batch_id, tenant_id=tenant_id)
        with self._db.connection() as conn:
            rows = conn.execute(query).fetchall()
            if not rows:
                return None
            return first(BatchInfoMapper.parse_rows_to_batch_infos(rows))

    def find_all_with(
        self,
        filtering: BatchFiltering,
        sorting: BatchSorting,
        pagination: Pagination,
    ) -> ListBatchInfo:
        valid_batches_query = self._query_factory.filtered_batch_ids(
            filtering=filtering,
            sorting=sorting,
            pagination=pagination,
        )
        query = self._query_factory.find_all_with(valid_batches_query, sorting=sorting)
        count_query = self._query_factory.count_batch_query_result(valid_batches_query)
        with self._db.connection() as conn:
            records = conn.execute(query).fetchall()
            total = conn.execute(count_query).scalar()
            return BatchListMapper.parse_rows_to_batch_infos(records, total)
