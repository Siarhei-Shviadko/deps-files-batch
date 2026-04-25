from more_itertools.more import first
from sqlalchemy.orm import Session

from deps_files_batch.domain.model import Batch, ICommandBatchRepository

from ..tables import BatchTable, FileTable
from .command_query_factory import BatchCommandRepoQueryFactory
from .mappers import BatchMapper

__all__ = ["UoWCommandBatchRepository"]


class UoWCommandBatchRepository(ICommandBatchRepository):
    def __init__(self, connection: Session) -> None:
        self._connection = connection
        self._query_factory = BatchCommandRepoQueryFactory()

    def save(self, batch: Batch) -> None:
        self._save_batch(batch)
        self._save_files(batch)

    def delete_all(self, batches: list[Batch]) -> None:
        tenant_id = first(batches).tenant_id()
        batch_ids = {b.id() for b in batches}
        query = self._query_factory.delete_all(batch_ids=batch_ids, tenant_id=tenant_id)
        self._connection.execute(query)

    def batch_of_id(self, batch_id: str, tenant_id: str) -> Batch | None:
        query = self._query_factory.select_query(batch_id, tenant_id)
        result = self._connection.execute(query).fetchall()
        if not result:
            return None
        return first(BatchMapper.parse_rows_to_batches(result))

    def batches_of_ids(self, ids: set[str], tenant_id: str) -> list[Batch]:
        query = self._query_factory.select_several_query(batch_ids=ids, tenant_id=tenant_id)
        result = self._connection.execute(query).fetchall()
        return BatchMapper.parse_rows_to_batches(result)

    def _save_batch(self, batch: Batch) -> None:
        query = self._query_factory.insert_batch_query(BatchTable.from_domain(batch))
        self._connection.execute(query)

    def _save_files(self, batch: Batch) -> None:
        current_file_ids = [file.id() for file in batch.files]
        file_tables = [FileTable.from_domain(batch_id=batch.id(), file=file) for file in batch.files]
        save_files = self._query_factory.insert_files_query(file_tables)
        delete_unmatched_files = self._query_factory.delete_unmatched_files_query(batch.id(), current_file_ids)

        self._connection.execute(save_files)
        self._connection.execute(delete_unmatched_files)
