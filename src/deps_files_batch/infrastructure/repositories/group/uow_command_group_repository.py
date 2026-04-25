from sqlalchemy import delete
from sqlalchemy.orm import Session

from deps_files_batch.domain.model import Group, ICommandGroupRepository

from ..tables import group_table
from .group_mapper import GroupMapper
from .query_factory import CommandGroupRepositoryQueryFactory

__all__ = ["UoWCommandGroupRepository"]


class UoWCommandGroupRepository(ICommandGroupRepository):
    def __init__(self, connection: Session) -> None:
        self._connection = connection
        self._query_factory = CommandGroupRepositoryQueryFactory()

    def group_of_id(self, group_id: str, tenant_id: str) -> Group | None:
        query = self._query_factory.group_of_id(group_id=group_id, tenant_id=tenant_id)
        rows = self._connection.execute(query)

        if rows.rowcount < 1:
            return None
        return GroupMapper.from_row(rows.fetchone())

    def save_all(self, groups: list[Group]) -> None:
        if not groups:
            return

        for group in groups:
            self.save(group)

    def save(self, group: Group) -> None:
        self._save_group(group)
        self._save_document_types(group)

    def delete(self, group: Group) -> None:
        self.save(group)

    def erase_all_groups(self) -> None:
        self._connection.execute(delete(group_table))

    def save_document_types(self, document_type_ids: list[str]) -> None:
        query = self._query_factory.save_doc_types(document_type_ids)
        self._connection.execute(query)

    def delete_document_type(self, document_type_id: str) -> None:
        query = self._query_factory.delete_document_type(document_type_id)
        self._connection.execute(query)

    def _save_group(self, group: Group) -> None:
        save_command = self._query_factory.save_group_fields(group=group)
        self._connection.execute(save_command)

    def _save_document_types(self, group: Group) -> None:
        if not group.document_types:
            query = self._query_factory.delete_all_doc_types_from_group(group_id=group.id())
            self._connection.execute(query)
            return
        document_type_ids = [dt() for dt in group.document_types]
        save_document_types = self._query_factory.save_doc_types(document_type_ids)
        save_document_types_to_group = self._query_factory.save_doc_types_to_group(
            group_id=group.id(),
            document_type_ids=document_type_ids,
        )
        delete_extra_document_types = self._query_factory.delete_unmatched_doc_types_from_group(
            group_id=group.id(),
            document_type_ids=document_type_ids,
        )
        self._connection.execute(save_document_types)
        self._connection.execute(save_document_types_to_group)
        self._connection.execute(delete_extra_document_types)
