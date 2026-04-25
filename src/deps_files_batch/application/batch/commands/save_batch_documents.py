from dataclasses import dataclass
from typing import Any, TypedDict

from deps_message_flow.commands.common import Command

from deps_files_batch.constants import METADATA_BATCH_FILE_ID_KEY, METADATA_BATCH_ID_KEY
from deps_files_batch.domain.model import (
    Batch,
    ErrorInfo,
    File,
    ProcessingParametersDict,
)

__all__ = ["SaveBatchDocuments", "SaveBatchDocumentsReply", "DocumentCreationResult", "FileData"]


class FileData(TypedDict):
    id: str
    path: str
    name: str
    document_type_id: str
    processing_params: ProcessingParametersDict
    metadata: dict[str, Any]


@dataclass(slots=True)
class SaveBatchDocuments(Command):
    batch_id: str
    group_id: str
    files: list[FileData]

    @classmethod
    def for_files(cls, batch: Batch, files: list[File]) -> "SaveBatchDocuments":
        return cls(
            batch_id=batch.id(),
            group_id=batch.group_id and batch.group_id(),
            files=cls._build_files_data(metadata=cls._init_metadata(batch), files=files),
        )

    @staticmethod
    def _build_files_data(files: list[File], metadata: dict[str, Any]) -> list[FileData]:
        files_data = []
        for file in files:
            processing_params_vo = file.processing_params
            processing_params_dict: ProcessingParametersDict = {
                "engine": processing_params_vo.engine,
                "language": processing_params_vo.language,
                "llm_type": processing_params_vo.llm_type,
                "parsing_features": processing_params_vo.parsing_features
                and sorted(pf.value for pf in processing_params_vo.parsing_features),
            }
            files_data.append(
                FileData(
                    id=file.id(),
                    path=file.file_path,
                    name=file.name,
                    document_type_id=file.document_type_id(),
                    processing_params=processing_params_dict,
                    metadata={METADATA_BATCH_FILE_ID_KEY: file.id(), **metadata},
                ),
            )

        return files_data

    @staticmethod
    def _init_metadata(batch: Batch) -> dict[str, Any]:
        return {METADATA_BATCH_ID_KEY: batch.id()} | batch.metadata


class DocumentCreationResult(TypedDict):
    id: str
    document_id: str | None
    error: ErrorInfo | None


@dataclass(slots=True)
class SaveBatchDocumentsReply(Command):
    batch_id: str
    files: list[DocumentCreationResult]
