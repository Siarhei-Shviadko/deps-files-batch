from datetime import datetime
from functools import cached_property
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from deps_files_batch.domain.model import Batch, BatchStatus

from .base import Base
from .constants import UUID_LENGTH

__all__ = ["BatchTable"]


NAME_LENGTH = 255


class BatchTable(Base):
    __tablename__ = "batch"

    id: Mapped[str] = mapped_column(String(UUID_LENGTH), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(UUID_LENGTH), nullable=False)
    group_id: Mapped[str] = mapped_column(ForeignKey("group.group_id", ondelete="SET NULL"), nullable=True, index=True)
    source_file_id: Mapped[str] = mapped_column(String(UUID_LENGTH), nullable=True)
    name: Mapped[str] = mapped_column(String(NAME_LENGTH), nullable=False, index=True)
    status: Mapped[BatchStatus] = mapped_column(Enum(BatchStatus), nullable=False, default=BatchStatus.NEW)
    batch_metadata: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    @cached_property
    def values(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @cached_property
    def updatable_values(self) -> dict[str, Any]:
        not_updatable_columns = {"id", "tenant_id"}
        return {k: v for k, v in self.values.items() if k not in not_updatable_columns}

    @classmethod
    def from_domain(cls, batch: Batch) -> "BatchTable":
        return cls(
            id=batch.id(),
            tenant_id=batch.tenant_id(),
            group_id=(gid := batch.group_id) and gid(),
            source_file_id=batch.source_file_id,
            name=batch.name,
            status=batch.status(),
            batch_metadata=batch.metadata,
            created_at=batch.created_at,
            updated_at=batch.updated_at,
        )
