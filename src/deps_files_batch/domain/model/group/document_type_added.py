from dataclasses import dataclass

from ..shared import Event

__all__ = ["DocumentTypesAdded"]


@dataclass
class DocumentTypesAdded(Event):
    id: str
    tenant_id: str
    document_type_ids: list[str]
