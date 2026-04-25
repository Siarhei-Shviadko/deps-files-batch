from typing import Any

from sqlalchemy import Row

from deps_files_batch.domain.model import Group

__all__ = ["GroupMapper"]


class GroupMapper:
    @staticmethod
    def to_dict(group: Group) -> dict[str, Any]:
        return {
            "group_id": group.id(),
            "tenant_id": group.tenant_id(),
            "is_deleted": group.is_deleted,
            "name": group.name,
        }

    @staticmethod
    def from_row(group_data: Row) -> Group:
        return Group(
            id_=group_data.group_id,
            tenant_id=group_data.tenant_id,
            name=group_data.name,
            is_deleted=group_data.is_deleted,
            document_types=group_data.document_type_ids,
        )
