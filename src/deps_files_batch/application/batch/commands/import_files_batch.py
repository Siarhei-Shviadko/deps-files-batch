from dataclasses import dataclass, field
from typing import Any

from deps_message_flow.commands.common import Command

from deps_files_batch.domain.model import FileCreationData, FileCreationDataDict

__all__ = ["ImportFilesBatch", "ImportFilesBatchReply"]


@dataclass(slots=True)
class ImportFilesBatch(Command):
    name: str
    file_params: list[FileCreationData]
    metadata: dict[str, Any] = field(default_factory=dict)
    group_id: str | None = None

    def __init__(
        self,
        name: str,
        file_params: list[FileCreationDataDict],
        group_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.group_id = group_id
        self.metadata = metadata or {}
        self.file_params = [
            FileCreationData(
                name=fp["name"],
                file_path=fp["file_path"],
                processing_params=fp["processing_params"],
                document_type_id=fp["document_type_id"],
            )
            for fp in file_params
        ]

    def validate(self) -> None:
        if self.group_id is None and any(fp.document_type_id is None for fp in self.file_params):
            raise ValueError("Group or all file document types should be provided")


@dataclass(slots=True)
class ImportFilesBatchReply(Command):
    batch_id: str | None = None
