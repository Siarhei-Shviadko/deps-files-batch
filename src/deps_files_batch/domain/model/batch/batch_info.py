from datetime import datetime
from typing import TypedDict

from ..shared import ErrorInfo

__all__ = ["BatchInfo", "GroupInfo", "FileInfo"]


class GroupInfo(TypedDict):
    id: str
    name: str


class FileInfo(TypedDict):
    id: str
    name: str
    status: str
    engine: str | None
    document_id: str | None
    document_type_id: str | None
    llm_type: str | None
    parsing_features: list[str] | None
    error: ErrorInfo | None


class BatchInfo(TypedDict):
    id: str
    name: str
    group: GroupInfo | None
    status: str
    created_at: datetime
    files: list[FileInfo]
    metadata: dict
