from datetime import datetime
from typing import TypedDict

from ..shared import ErrorInfo, PaginatedResultMetadataInfo
from .batch import Batch
from .file import File

__all__ = ["ListBatchUnit", "ListBatchFileInfo", "ListBatchInfo", "ListBatchGroupInfo"]


class ListBatchGroupInfo(TypedDict):
    id: str
    name: str


class ListBatchFileInfo(TypedDict):
    name: str
    status: str
    error: ErrorInfo | None


class ListBatchUnit(TypedDict):
    id: str
    name: str
    group: ListBatchGroupInfo | None
    status: str
    created_at: datetime
    files: list[ListBatchFileInfo]


class ListBatchInfo(TypedDict):
    batches: list[ListBatchUnit]
    metadata: PaginatedResultMetadataInfo
