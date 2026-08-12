from datetime import datetime

from pydantic import Field

from deps_files_batch.domain.model import ErrorInfo

from .configured_base_serializer import ConfiguredSerializer
from .paginated_result_metadata_serializer import PaginatedResultMetadataSerializer

__all__ = ["GetBatchesResponse", "SerializedListBatchFileInfo", "SerializedListBatchInfo"]


class SerializedListGroupInfo(ConfiguredSerializer):
    id: str
    name: str


class SerializedListBatchFileInfo(ConfiguredSerializer):
    name: str
    status: str
    error: ErrorInfo | None


class SerializedListBatchInfo(ConfiguredSerializer):
    id: str
    name: str
    group: SerializedListGroupInfo | None
    status: str
    files: list[SerializedListBatchFileInfo]
    created_at: datetime = Field(..., alias="createdAt")
    source_file_id: str | None = Field(default=None, alias="sourceFileId")


class GetBatchesResponse(ConfiguredSerializer):
    metadata: PaginatedResultMetadataSerializer = Field(..., alias="meta")
    batches: list[SerializedListBatchInfo] = Field(..., alias="result")
