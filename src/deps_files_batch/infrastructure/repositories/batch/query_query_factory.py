from functools import cached_property
from types import MappingProxyType as ImmutableDict
from typing import Callable

from sqlalchemy import (  # noqa: WPS235
    Column,
    Join,
    Select,
    asc,
    desc,
    distinct,
    func,
    outerjoin,
    select,
)

from deps_files_batch.domain.model import (
    BatchFiltering,
    BatchSortBy,
    BatchSorting,
    BatchSortOrder,
    Pagination,
)

from ..tables import BatchTable, FileTable, group_table

__all__ = ["BatchQueryRepoQueryFactory"]


class BatchQueryRepoQueryFactory:
    SORTING_FIELD_MAP: ImmutableDict[BatchSortBy, tuple[Column, ...]] = ImmutableDict(
        {
            BatchSortBy.CREATED_AT: (BatchTable.created_at,),
            BatchSortBy.NAME: (BatchTable.name,),
            BatchSortBy.STATUS: (BatchTable.status, BatchTable.created_at),
            BatchSortBy.GROUP: (group_table.c.name, BatchTable.created_at),
        },
    )
    SORTING_ORDER_MAP: ImmutableDict[BatchSortOrder, Callable] = ImmutableDict(
        {BatchSortOrder.ASC: asc, BatchSortOrder.DESC: desc},
    )

    def find_batch(self, batch_id: str, tenant_id: str) -> Select:
        return self.base_select_query.where(BatchTable.id == batch_id).where(BatchTable.tenant_id == tenant_id)

    def filtered_batch_ids(self, filtering: BatchFiltering, sorting: BatchSorting, pagination: Pagination) -> Select:
        query = self.base_cte_query
        query = self._apply_filters(query, filtering)
        query = self._apply_sorting(query, sorting)
        return self._apply_pagination(query, pagination)

    def find_all_with(self, cte_query: Select, sorting: BatchSorting) -> Select:
        cte_query = cte_query.cte("batches_to_select")

        query = self.base_select_list_query.join(cte_query, BatchTable.id == cte_query.c.cte_batch_id)
        return self._apply_sorting(query, sorting)

    def count_batch_query_result(self, query: Select) -> Select:
        return (
            query.with_only_columns(func.count(distinct(BatchTable.id)))
            .order_by(None)
            .limit(None)
            .offset(None)
            .group_by(None)
        )

    @cached_property
    def joined_batch_and_file(self) -> Join:
        return outerjoin(BatchTable, FileTable, BatchTable.id == FileTable.batch_id)

    @cached_property
    def joined_tables_with_groups(self) -> Join:
        return outerjoin(self.joined_batch_and_file, group_table, BatchTable.group_id == group_table.c.group_id)

    @cached_property
    def base_select_query(self) -> Select:
        return select(
            BatchTable,
            FileTable,
            group_table.c.name.label("group_name"),
            group_table.c.group_id.label("group_id"),
        ).select_from(
            self.joined_tables_with_groups,
        )

    @cached_property
    def base_select_list_query(self) -> Select:
        return select(
            BatchTable,
            FileTable.id,
            FileTable.name,
            FileTable.file_path,
            FileTable.status.label("file_status"),
            FileTable.error,
            group_table.c.name.label("group_name"),
            group_table.c.group_id.label("group_id"),
        ).select_from(
            self.joined_tables_with_groups,
        )

    @cached_property
    def base_cte_query(self):
        return select(distinct(BatchTable.id).label("cte_batch_id")).select_from(self.joined_tables_with_groups)

    def _apply_filters(self, query: Select, filtering: BatchFiltering) -> Select:
        query = query.where(BatchTable.tenant_id == filtering.tenant_id)

        if filtering.group:
            query = query.where(group_table.c.name.ilike(f"%{filtering.group}%"))
        if filtering.name:
            query = query.where(BatchTable.name.ilike(f"%{filtering.name}%"))
        if filtering.status:
            query = query.where(BatchTable.status.in_(filtering.status))
        if filtering.date_start:
            query = query.where(BatchTable.created_at >= filtering.date_start)
        if filtering.date_end:
            query = query.where(BatchTable.created_at <= filtering.date_end)
        return query

    def _apply_pagination(self, query: Select, pagination: Pagination) -> Select:
        limit = pagination.per_page
        offset = pagination.page * pagination.per_page
        return query.offset(offset).limit(limit)

    def _apply_sorting(self, query: Select, sorting: BatchSorting) -> Select:
        sort_columns = self.SORTING_FIELD_MAP[sorting.sort_by]
        sort_expression = [self.SORTING_ORDER_MAP[sorting.sort_order](sc).nulls_last() for sc in sort_columns]
        for index, column in enumerate(sort_columns):
            # it doesn't work with distinct otherwise
            query = query.add_columns(column.label(f"useless_column_{index}"))
        return query.order_by(*sort_expression)
