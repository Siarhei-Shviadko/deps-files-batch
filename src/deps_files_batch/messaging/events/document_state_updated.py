from dataclasses import dataclass
from typing import Any

from deps_message_flow.events.common import DomainEvent

__all__ = ["DocumentStateUpdated"]


@dataclass
class DocumentStateUpdated(DomainEvent):
    document_id: str
    state: str
    metadata: dict[str, Any]
    error_in_state: str | None = None
