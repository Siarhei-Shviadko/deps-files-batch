from dataclasses import dataclass
from typing import Any

from deps_message_flow.commands.common import Command

from deps_files_batch.constants import METADATA_BATCH_FILE_ID_KEY, METADATA_BATCH_ID_KEY
from deps_files_batch.domain.model import Batch, File

__all__ = ["ClassifyBatchFile", "ClassifyBatchFileReply"]


@dataclass
class ClassifyBatchFile(Command):
    batch_id: str
    file_id: str
    file_name: str
    file_path: str
    group_id: str
    engine: str | None = None
    language: str | None = None
    parsing_features: list[str] | None = None
    llm_type: str | None = None
    needs_unifier: bool = False
    needs_extraction: bool = False
    assigned_to_me: bool = False
    metadata: dict[str, Any] | None = None
    start_processing: bool = False

    @classmethod
    def for_file(cls, batch: Batch, file: File) -> "ClassifyBatchFile":
        processing_parameters = file.processing_params

        return cls(
            batch_id=batch.id(),
            file_id=file.id(),
            file_name=file.name,
            file_path=file.file_path,
            group_id=batch.group_id(),
            engine=processing_parameters.engine,
            language=processing_parameters.language,
            parsing_features=sorted(pfs) if (pfs := processing_parameters.parsing_features) is not None else pfs,
            llm_type=processing_parameters.llm_type,
            needs_unifier=True,
            needs_extraction=True,
            assigned_to_me=False,
            metadata={METADATA_BATCH_ID_KEY: batch.id(), METADATA_BATCH_FILE_ID_KEY: file.id(), **batch.metadata},
            start_processing=False,
        )


@dataclass
class ClassifyBatchFileReply(Command):
    batch_id: str
    file_id: str
    document_id: str | None = None
    document_type_id: str | None = None
    error_type: str | None = None
    error_message: str | None = None
