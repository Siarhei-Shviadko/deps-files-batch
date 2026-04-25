from dataclasses import dataclass

from ..shared import Event

__all__ = ["GroupDeleted"]


@dataclass
class GroupDeleted(Event):
    id: str
    tenant_id: str
