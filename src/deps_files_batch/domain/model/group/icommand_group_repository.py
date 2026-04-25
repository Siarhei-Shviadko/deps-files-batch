from typing import Protocol

from .group import Group

__all__ = ["ICommandGroupRepository"]


class ICommandGroupRepository(Protocol):
    def group_of_id(self, group_id: str, tenant_id: str) -> Group | None:
        pass

    def save_all(self, groups: list[Group]) -> None:
        pass

    def save(self, group: Group) -> None:
        pass

    def delete(self, group: Group) -> None:
        pass

    def save_document_types(self, document_type_ids: list[str]) -> None:
        pass

    def delete_document_type(self, document_type_id: str) -> None:
        pass
