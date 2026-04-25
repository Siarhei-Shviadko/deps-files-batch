from typing import Iterable

from ..shared import EntityId, Guard, ImmutableCheck, TenantId
from .group_id import GroupId

__all__ = ["Group"]


class Group:
    id = Guard[GroupId](GroupId, ImmutableCheck())
    tenant_id = Guard[TenantId](TenantId, ImmutableCheck())
    name = Guard[str](str, ImmutableCheck())
    document_types = Guard[list[EntityId]](list, ImmutableCheck())
    is_deleted = Guard[bool](bool)

    def __init__(
        self,
        id_: str,
        tenant_id: str,
        name: str,
        document_types: list[str],
        *,
        is_deleted: bool = False,
    ) -> None:
        self.id = GroupId(id_)
        self.tenant_id = TenantId(tenant_id)
        self.name = name
        self.document_types = [EntityId(document_type) for document_type in document_types]

        self.is_deleted = is_deleted

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.id == self.id

    def __repr__(self) -> str:
        return " ".join(
            (
                f"{self.__class__.__name__}(id_={self.id},",
                f"tenant_id={self.tenant_id},",
                f"document_types={self.document_types},",
                f"is_deleted={self.is_deleted})",
            ),
        )

    def delete(self) -> None:
        self.is_deleted = True

    def add_document_types(self, document_types_ids: list[str]) -> None:
        for document_type_id in document_types_ids:
            if (entity_id := EntityId(document_type_id)) in self.document_types:
                continue

            self.document_types.append(entity_id)

    def remove_document_types(self, document_types_ids: list[str]) -> None:
        for document_type_id in document_types_ids:
            if (entity_id := EntityId(document_type_id)) in self.document_types:
                self.document_types.remove(entity_id)

    def contains_document_types(self, document_type_ids: Iterable[str | None]) -> bool:
        current_document_types = {dt() for dt in self.document_types}
        document_type_ids_with_values = {*filter(bool, document_type_ids)}  # noqa: WPS356
        return current_document_types.issuperset(document_type_ids_with_values)
