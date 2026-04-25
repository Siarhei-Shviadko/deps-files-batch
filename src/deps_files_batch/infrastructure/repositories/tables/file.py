from functools import cached_property
from typing import Any

from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from deps_files_batch.domain.model import File, FileStatus, ProcessingParametersDict

from .base import Base
from .constants import UUID_LENGTH

__all__ = ["FileTable"]

FILEPATH_MAX_LENGTH = 255


class FileTable(Base):
    __tablename__ = "file"
    id: Mapped[str] = mapped_column(String(UUID_LENGTH), primary_key=True)
    batch_id: Mapped[str] = mapped_column(
        String(UUID_LENGTH),
        ForeignKey("batch.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[str] = mapped_column(String(UUID_LENGTH), nullable=True, index=True)
    document_type_id: Mapped[str] = mapped_column(
        String(UUID_LENGTH),
        ForeignKey("document_type.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(FILEPATH_MAX_LENGTH), nullable=False)
    file_path: Mapped[str] = mapped_column(String(FILEPATH_MAX_LENGTH), nullable=False)
    status: Mapped[FileStatus] = mapped_column(Enum(FileStatus), nullable=False)
    error: Mapped[dict] = mapped_column(JSON, nullable=True)
    processing_parameters: Mapped[ProcessingParametersDict] = mapped_column(JSON, nullable=False)

    @cached_property
    def values(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @cached_property
    def updatable_values(self) -> dict[str, Any]:
        not_updatable_columns = {"id", "batch_id"}
        return {k: v for k, v in self.values.items() if k not in not_updatable_columns}

    @classmethod
    def from_domain(cls, *, batch_id: str, file: File) -> "FileTable":
        processing_parameters = {
            "engine": file.processing_params.engine,
            "language": file.processing_params.language,
            "llm_type": file.processing_params.llm_type,
            "parsing_features": (parsing_features := file.processing_params.parsing_features) and [*parsing_features],
        }
        error = file.error and {"code": file.error.code, "message": file.error.message}
        return cls(
            id=file.id(),
            name=file.name,
            batch_id=batch_id,
            document_id=(did := file.document_id) and did(),
            document_type_id=(dtid := file.document_type_id) and dtid(),
            file_path=file.file_path,
            status=file.status(),
            processing_parameters=processing_parameters,
            error=error,
        )
