from typing import Protocol

__all__ = ["IQueryGroupRepository"]


class IQueryGroupRepository(Protocol):
    def exists_group_of_id(self, group_id: str, tenant_id: str) -> bool:
        pass
