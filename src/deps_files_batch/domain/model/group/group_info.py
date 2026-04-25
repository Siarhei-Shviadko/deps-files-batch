from typing import TypedDict

__all__ = ["GroupInfo"]


class GroupInfo(TypedDict):
    id: str
    tenant_id: str
    name: str
    document_type_ids: list[str]
