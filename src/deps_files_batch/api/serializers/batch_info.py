from datetime import datetime
from typing import Any

from pydantic import Field

from deps_files_batch.domain.model import ErrorInfo

from .configured_base_serializer import ConfiguredSerializer

__all__ = ["SerializedBatchInfo", "SerializedFileInfo"]


class SerializedGroupInfo(ConfiguredSerializer):
    id: str
    name: str


class SerializedFileInfo(ConfiguredSerializer):
    id: str
    name: str
    status: str
    document_id: str | None = Field(default=None, alias="documentId")
    document_type_id: str | None = Field(default=None, alias="documentTypeId")
    engine: str | None
    llm_type: str | None = Field(default=None, alias="llmType")
    parsing_features: list[str] | None = Field(default=None, alias="parsingFeatures")
    error: ErrorInfo | None = None


class SerializedBatchInfo(ConfiguredSerializer):
    id: str
    name: str
    status: str
    group: SerializedGroupInfo | None
    created_at: datetime = Field(..., alias="createdAt")
    files: list[SerializedFileInfo]
    metadata: dict[str, Any]
    source_file_id: str | None = Field(default=None, alias="sourceFileId")
