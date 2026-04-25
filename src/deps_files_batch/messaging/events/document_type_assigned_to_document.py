from dataclasses import dataclass
from typing import Any

from deps_message_flow.events.common import DomainEvent

__all__ = ["DocumentTypeAssignedToDocument"]


@dataclass
class DocumentTypeAssignedToDocument(DomainEvent):
    document_id: str
    document_type_id: str
    metadata: dict[str, Any]
