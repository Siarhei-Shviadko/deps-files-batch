from typing import Any

from pydantic import Field, root_validator

from deps_files_batch.domain.model import (
    MAX_BATCH_NAME_LENGTH,
    FileCreationData,
    ParsingFeature,
)

from .configured_base_serializer import ConfiguredSerializer

__all__ = [
    "FileRequestSerializer",
    "BatchRequestSerializer",
    "BatchCreateResponse",
    "ProcessingParametersSerializer",
    "BatchUpdateRequest",
    "BatchCreateFromFileResponse",
]


class ProcessingParametersSerializer(ConfiguredSerializer):
    engine: str | None = Field(None)
    language: str | None = Field(None)
    llm_type: str | None = Field(None, alias="llmType")
    parsing_features: list[ParsingFeature] | None = Field(None, alias="parsingFeatures")


class FileRequestSerializer(ConfiguredSerializer):
    name: str = Field(..., min_length=1)
    path: str = Field(..., min_length=1)
    document_type_id: str | None = Field(None, alias="documentTypeId")
    processing_params: ProcessingParametersSerializer = Field(..., alias="processingParams")


class BatchRequestSerializer(ConfiguredSerializer):
    name: str = Field(max_length=MAX_BATCH_NAME_LENGTH, min_length=1)
    group_id: str | None = Field(None, alias="groupId")
    metadata: dict[str, Any] | None = Field(None)
    files: list[FileRequestSerializer] = Field(..., min_items=1)

    @property
    def file_parameters(self):
        return [
            FileCreationData(
                name=fp.name,
                file_path=fp.path,
                processing_params=fp.processing_params.dict(by_alias=False),
                document_type_id=fp.document_type_id,
            )
            for fp in self.files
        ]

    @root_validator
    @classmethod
    def validate_group_or_document_types_existence(cls, values: dict[str, Any]):
        if values["group_id"] is None and any(f.document_type_id is None for f in values["files"]):
            raise ValueError("Group or all file document types should be provided")

        return values


class BatchCreateResponse(ConfiguredSerializer):
    batch_id: str


class BatchCreateFromFileResponse(ConfiguredSerializer):
    batch_id: str = Field(..., alias="batchId")
    batch_name: str = Field(..., alias="batchName")


class BatchUpdateRequest(ConfiguredSerializer):
    name: str = Field(max_length=MAX_BATCH_NAME_LENGTH, min_length=1)
