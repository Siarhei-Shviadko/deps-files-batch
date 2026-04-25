from dataclasses import dataclass

from ...shared import Event

__all__ = ["BatchProcessed", "ProcessedFile"]


@dataclass(slots=True)
class ProcessedFile:
    id: str
    status: str
    document_id: str | None = None


@dataclass(slots=True)
class BatchProcessed(Event):
    id: str
    status: str
    error_message: str | None
    files: list[ProcessedFile]
