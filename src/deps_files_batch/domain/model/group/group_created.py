from dataclasses import dataclass

from ..shared import Event

__all__ = ["GroupCreated"]


@dataclass
class GroupCreated(Event):
    id: str
    tenant_id: str
    name: str
    document_type_ids: list[str]
