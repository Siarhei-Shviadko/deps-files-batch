from functools import cached_property

from sqlalchemy import (  # noqa: WPS235
    BinaryExpression,
    Column,
    Delete,
    Insert,
    Join,
    Select,
    delete,
    func,
    select,
)
from sqlalchemy.dialects.postgresql import insert

from deps_files_batch.domain.model import Group

from ..tables import DocumentTypeTable
from ..tables import group_document_types_table as junction_table
from ..tables import group_table
from .group_mapper import GroupMapper

__all__ = ["CommandGroupRepositoryQueryFactory"]


class CommandGroupRepositoryQueryFactory:
    @cached_property
    def group_columns(self) -> list[Column]:
        return group_table.columns

    @cached_property
    def joined_tables(self) -> Join:
        return group_table.outerjoin(junction_table, group_table.c.group_id == junction_table.c.group_id)

    @cached_property
    def gathered_document_type_ids(self) -> Column:
        return func.array_agg(junction_table.c.document_type_id).label("document_type_ids")

    @cached_property
    def group_is_not_deleted(self) -> BinaryExpression:
        return group_table.c.is_deleted.is_(False)

    def group_of_id(self, group_id: str, tenant_id: str) -> Select:
        return (
            select(*self.group_columns, self.gathered_document_type_ids)
            .select_from(self.joined_tables)
            .where(group_table.c.group_id == group_id)
            .where(group_table.c.tenant_id == tenant_id)
            .where(self.group_is_not_deleted)
            .group_by(group_table.c.group_id)
        )

    def save_group_fields(self, group: Group) -> Insert:
        data = GroupMapper.to_dict(group)
        return (
            insert(group_table).on_conflict_do_update(index_elements=[group_table.c.group_id], set_=data).values(**data)
        )

    def save_doc_types(self, document_type_ids: list[str]) -> Insert:
        values = [{"id": dt_id} for dt_id in document_type_ids]
        return insert(DocumentTypeTable).values(values).on_conflict_do_nothing()

    def delete_all_doc_types_from_group(self, group_id: str) -> Delete:
        return delete(junction_table).where(junction_table.c.group_id == group_id)

    def delete_unmatched_doc_types_from_group(self, group_id: str, document_type_ids: list[str]) -> Delete:
        return (
            delete(junction_table)
            .where(junction_table.c.group_id == group_id)
            .where(junction_table.c.document_type_id.notin_(document_type_ids))
        )

    def save_doc_types_to_group(self, group_id: str, document_type_ids: list[str]) -> Insert:
        values = [{"group_id": group_id, "document_type_id": dt_id} for dt_id in document_type_ids]
        return insert(junction_table).on_conflict_do_nothing().values(values)

    def delete_document_type(self, document_type_id: str) -> Delete:
        return delete(DocumentTypeTable).where(DocumentTypeTable.id == document_type_id)
