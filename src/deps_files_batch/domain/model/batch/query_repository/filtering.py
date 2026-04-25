from dataclasses import dataclass
from datetime import datetime

__all__ = ["BatchFiltering"]


@dataclass
class BatchFiltering:
    tenant_id: str
    name: str | None = None
    status: list[str] | None = None
    group: str | None = None
    date_start: datetime | None = None
    date_end: datetime | None = None
