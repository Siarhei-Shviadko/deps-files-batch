from dataclasses import dataclass

from ..shared import Event

__all__ = ["DocumentTypesRemoved"]


@dataclass
class DocumentTypesRemoved(Event):
    id: str
    tenant_id: str
    document_type_ids: list[str]
