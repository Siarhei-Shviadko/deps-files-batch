from typing import TypedDict

__all__ = ["PaginatedResultMetadataInfo"]


class PaginatedResultMetadataInfo(TypedDict):
    size: int
    total: int
