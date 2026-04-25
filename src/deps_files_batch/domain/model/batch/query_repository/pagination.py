from dataclasses import dataclass

__all__ = ["Pagination"]


@dataclass
class Pagination:
    page: int
    per_page: int
