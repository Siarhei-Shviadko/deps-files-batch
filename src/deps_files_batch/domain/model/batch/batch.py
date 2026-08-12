from datetime import datetime, timezone
from typing import Any, Iterator, cast

from more_itertools import first

from deps_files_batch.domain.exceptions import FileNotFound, IllegalArgument

from ..group import GroupId
from ..shared import Command, Event, Guard, ImmutableCheck, LengthCheck, TenantId
from .batch_id import BatchId
from .constants import (
    END_STATUSES,
    ERROR_STATUSES,
    MAX_BATCH_NAME_LENGTH,
    MIN_BATCH_FILES_AMOUNT,
)
from .events import BatchProcessed, BatchStatusUpdated, ProcessedFile
from .file import (
    FILE_ERROR_STATUSES,
    File,
    FileId,
    FileStatus,
    ProcessingParametersDict,
)
from .file.builder import FileBuilder
from .limited_storage import LimitedFilesDict
from .state_manager import StateManager
from .status import BatchStatus

__all__ = ["Batch"]


class Batch:
    id = Guard[BatchId](BatchId, ImmutableCheck())
    tenant_id = Guard[TenantId](TenantId, ImmutableCheck())
    group_id = Guard[GroupId](GroupId, ImmutableCheck())
    name = Guard[str](str, LengthCheck(max_length=MAX_BATCH_NAME_LENGTH))
    status = Guard[BatchStatus](BatchStatus)
    metadata = Guard[dict[str, Any]](dict, ImmutableCheck())
    created_at = Guard[datetime](datetime, ImmutableCheck())
    updated_at = Guard[datetime](datetime)
    source_file_id = Guard[str](str, ImmutableCheck())
    file_storage = Guard[LimitedFilesDict](
        LimitedFilesDict,
        ImmutableCheck(),
        LengthCheck(min_length=MIN_BATCH_FILES_AMOUNT),
    )

    def __init__(
        self,
        tenant_id: str,
        name: str,
        files: list[File],
        status: BatchStatus = BatchStatus.NEW,
        id_: str | None = None,
        metadata: dict[str, Any] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        group_id: str | None = None,
        source_file_id: str | None = None,
        *,
        events: list[Event] | None = None,
        commands: list[Command] | None = None,
    ) -> None:
        self.id = BatchId(id_) if id_ is not None else BatchId()
        self.tenant_id = TenantId(tenant_id)
        self.name = name
        self.status = status
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now(timezone.utc)
        self.events = events or []
        self.commands = commands or []
        self.file_storage = cast(dict[FileId, File], LimitedFilesDict({file.id: file for file in files}))

        self._file_builder = FileBuilder
        self._state_manager = StateManager(batch=self, new_status_setter=self._set_new_status)

        if updated_at:
            self.updated_at = updated_at
        if group_id:
            self.group_id = GroupId(group_id)
        if source_file_id:
            self.source_file_id = source_file_id

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.id == self.id

    def __repr__(self) -> str:
        return "\n".join(
            (
                f"{self.__class__.__name__}(",
                f"id_={self.id},",
                f"tenant_id={self.tenant_id},",
                f"name={self.name!r},",
                f"status={self.status},",
                f"files={self.files},",
                f"metadata={self.metadata},",
                f"created_at={self.created_at!r},",
                f"updated_at={self.updated_at!r},",
                f"group_id={self.group_id},",
                f"source_file_id={self.source_file_id},",
                f"events={self.events},",
                f"commands={self.commands})",
            ),
        )

    def __iter__(self) -> Iterator[File]:
        return iter(self.files)

    @property
    def files(self) -> list[File]:
        return list(self.file_storage.values())

    @property
    def files_with_document_type(self) -> list[File]:
        return [file for file in self.files if file.document_type_id is not None]

    @property
    def files_without_document_type(self) -> list[File]:
        return [file for file in self.files if file.document_type_id is None]

    @property
    def new_files(self) -> list[File]:
        return [f for f in self.file_storage.values() if f.is_new]

    @property
    def document_ids(self) -> list[str]:
        return [file.document_id() for file in self if file.document_id]

    @property
    def error_message(self) -> str | None:
        if self.status in ERROR_STATUSES:
            message = f"Batch is {self.status.value}. Reason:\n"
            file_error_messages = [file.error_message for file in self if file.status in FILE_ERROR_STATUSES]

            return message + "\n".join(file_error_messages)

        return None

    def add_file(
        self,
        file_name: str,
        file_path: str,
        processing_params: ProcessingParametersDict,
        document_type_id: str | None,
    ) -> File:
        file = (
            self._file_builder()
            .with_name(file_name)
            .with_path(path=file_path)
            .with_processing_params(processing_params)
            .with_document_type_id(document_type_id)
            .build()
        )
        self.file_storage[file.id] = file
        self._validate()
        self._synchronize_status()

        return file

    def file_has_different_status(self, file_id: str, file_status: FileStatus) -> bool:
        file = self.file_of_id(FileId(file_id))

        return file.status != file_status

    def update_file_status(self, file_id: str, file_status: FileStatus, error_in_state: str | None = None) -> None:
        file = self.file_of_id(FileId(file_id))
        file.update_status(status=file_status, error_in_state=error_in_state)

        if file.events:
            self._register_enriched(first(file.events), batch_id=self.id())

        self._synchronize_status()

    def file_of_id(self, id_: FileId) -> File:
        if file := self.file_storage.get(id_):
            return file

        raise FileNotFound(id_())

    def add_document_id(self, file_id: str, document_id: str) -> None:
        file = self.file_of_id(FileId(file_id))
        file.add_document_id(document_id)

        self._synchronize_status()

    def add_classification_result(self, file_id: str, document_id: str, document_type_id: str) -> None:
        file = self.file_of_id(FileId(file_id))
        file.add_document_id(document_id)
        file.assign_document_type(document_type_id)

        self._synchronize_status()

    def add_document_creation_error(self, file_id: str):
        self.update_file_status(file_id=file_id, file_status=FileStatus.ABORTED)

    def delete_file(self, file_id: str) -> File:
        file = self.file_of_id(FileId(file_id))
        self._delete_file_from_storage(file.id)

        self._synchronize_status()

        return file

    def assign_document_type_to_file(self, file_id: str, document_type_id: str) -> None:
        file = self.file_of_id(FileId(file_id))
        file.assign_document_type(document_type_id=document_type_id)

    def rename(self, new_name: str) -> None:
        self.name = new_name

    def _synchronize_status(self) -> None:
        self._state_manager.analyze()

    def _delete_file_from_storage(self, file_id: FileId) -> None:
        del self.file_storage[file_id]

    def _set_new_status(self, status: BatchStatus) -> None:
        self.status = status
        self.events.append(BatchStatusUpdated(id=self.id(), status=status))

        if status in END_STATUSES:
            self.events.append(
                BatchProcessed(
                    id=self.id(),
                    status=status,
                    error_message=self.error_message,
                    files=[
                        ProcessedFile(
                            id=file.id(),
                            status=file.status,
                            document_id=(document_id := file.document_id) and document_id(),
                        )
                        for file in self
                    ],
                ),
            )

    def _register_enriched(self, event: Event, **enrichment_kwargs: Any) -> None:
        self.events.append(event.recreate_enriched(**enrichment_kwargs))

    def _validate(self) -> None:
        if self.group_id is None and any(f.document_type_id is None for f in self.files):
            raise IllegalArgument("Group or all file document types should be provided")
