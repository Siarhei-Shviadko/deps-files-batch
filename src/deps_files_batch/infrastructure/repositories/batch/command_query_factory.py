from functools import cached_property
from typing import Collection

from sqlalchemy import Delete, Insert, Join, Select, delete, join, select
from sqlalchemy.dialects.postgresql import insert

from ..tables import BatchTable, FileTable

__all__ = ["BatchCommandRepoQueryFactory"]


class BatchCommandRepoQueryFactory:
    def insert_files_query(self, file_tables: list[FileTable]) -> Insert:
        values_list = [file_table.values for file_table in file_tables]
        updatable_keys = next(file_table.updatable_values for file_table in file_tables).keys()
        insert_query = insert(FileTable).values(values_list)
        return insert_query.on_conflict_do_update(
            index_elements=[FileTable.id],
            set_={key: insert_query.excluded[key] for key in updatable_keys},
        )

    def insert_batch_query(self, batch_table: BatchTable) -> Insert:
        return (
            insert(BatchTable)
            .values(batch_table.values)
            .on_conflict_do_update(index_elements=[BatchTable.id], set_=batch_table.updatable_values)
        )

    def delete_unmatched_files_query(self, batch_id: str, current_file_ids: list[str]):
        return delete(FileTable).where(FileTable.batch_id == batch_id).where(FileTable.id.notin_(current_file_ids))

    def delete_all(self, batch_ids: Collection[str], tenant_id: str) -> Delete:
        return delete(BatchTable).where(BatchTable.id.in_(batch_ids)).where(BatchTable.tenant_id == tenant_id)

    def select_query(self, batch_id: str, tenant_id: str) -> Select:
        return self.base_select_query.where(BatchTable.id == batch_id).where(BatchTable.tenant_id == tenant_id)

    def select_several_query(self, batch_ids: Collection[str], tenant_id: str) -> Select:
        return self.base_select_query.where(BatchTable.id.in_(batch_ids)).where(BatchTable.tenant_id == tenant_id)

    @cached_property
    def base_select_query(self) -> Select:
        return select(BatchTable, FileTable).select_from(self.joined_batch_and_file)

    @cached_property
    def joined_batch_and_file(self) -> Join:
        return join(BatchTable, FileTable, BatchTable.id == FileTable.batch_id)
