from ...shared import DocumentId, DocumentTypeId, Event, Guard, ImmutableCheck
from .constants import FILE_ERROR_STATUSES
from .error import Error, ErrorFactory
from .file_id import FileId
from .file_status_updated import BatchFileStatusUpdated
from .processing_parameters import ProcessingParameters, ProcessingParametersDict
from .status import FileStatus

__all__ = ["File"]


class File:
    id = Guard[FileId](FileId, ImmutableCheck())
    name = Guard[str](str, ImmutableCheck())
    file_path = Guard[str](str, ImmutableCheck())
    processing_params = Guard[ProcessingParameters](ProcessingParameters, ImmutableCheck())
    status = Guard[FileStatus](FileStatus)
    document_id = Guard[DocumentId](DocumentId)
    document_type_id = Guard[DocumentTypeId](DocumentTypeId)
    error = Guard[Error](Error)

    def __init__(
        self,
        name: str,
        file_path: str,
        processing_params: ProcessingParametersDict,
        id_: str | None = None,
        status: FileStatus = FileStatus.NEW,
        document_id: str | None = None,
        document_type_id: str | None = None,
        error: Error | None = None,
    ) -> None:
        self.id = FileId(id_) if id_ is not None else FileId()
        self.name = name
        self.file_path = file_path
        self.processing_params = ProcessingParameters(**processing_params)
        self.status = status

        if document_id:
            self.document_id = DocumentId(document_id)
        if document_type_id:
            self.document_type_id = DocumentTypeId(document_type_id)
        if error:
            self.error = error

        self._update_status_methods = {
            FileStatus.PROCESSING: self._set_processing_state,
            FileStatus.COMPLETED: self._set_completed_state,
            FileStatus.EXPORTED: self._set_exported_state,
            FileStatus.REVIEW: self._set_review_state,
            FileStatus.ABORTED: self._set_aborted_state,
        }
        self.events: list[Event] = []
        self._error_factory: ErrorFactory = ErrorFactory()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.id == self.id

    def __repr__(self) -> str:
        return " ".join(
            (
                f"{self.__class__.__name__}(id_={self.id}",
                f"name={self.name!r},",
                f"file_path={self.file_path!r},",
                f"processing_params={self.processing_params},",
                f"status={self.status},",
                f"document_id={self.document_id},",
                f"document_type_id={self.document_type_id},",
                f"error={self.error})",
            ),
        )

    @property
    def is_new(self) -> bool:
        return self.status == FileStatus.NEW

    @property
    def is_aborted(self) -> bool:
        return self.status == FileStatus.ABORTED

    @property
    def error_message(self) -> str | None:
        if self.status in FILE_ERROR_STATUSES:
            return f"File {self.name} is {self.status.value}. Reason: {self.error.message}"

        return None

    def _set_aborted_state(self) -> None:
        self.error = self._error_factory.create_aborted()
        self.status = FileStatus.ABORTED

    def _set_review_state(self) -> None:
        self.status = FileStatus.REVIEW

    def _set_failed_state(self, document_state: str | None = None) -> None:
        self.error = self._error_factory.create_for_document_state(document_state)
        self.status = FileStatus.FAILED

    def _set_completed_state(self) -> None:
        self.status = FileStatus.COMPLETED

    def _set_exported_state(self) -> None:
        self.status = FileStatus.EXPORTED

    def _set_processing_state(self) -> None:
        self.status = FileStatus.PROCESSING

    def add_document_id(self, id_: str) -> None:
        self.document_id = DocumentId(id_)

    def update_status(self, status: FileStatus, error_in_state: str | None = None) -> None:
        if self.status == status:
            return

        self._clear_error()

        if status == FileStatus.FAILED:
            self._set_failed_state(error_in_state)
        else:
            self._update_status_methods[status]()

        self.events.append(BatchFileStatusUpdated(file_id=self.id(), status=status))

    def assign_document_type(self, document_type_id: str) -> None:
        self.document_type_id = DocumentTypeId(document_type_id)

    def _clear_error(self) -> None:
        self._error = None
