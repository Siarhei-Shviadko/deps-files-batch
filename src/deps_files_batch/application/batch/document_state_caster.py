from deps_files_batch.domain.model import DocumentState, FileStatus

__all__ = ["DocumentStateCaster"]


class DocumentStateCaster:
    def __init__(self) -> None:
        self.statuses_mapping: dict[FileStatus, set[DocumentState]] = {
            FileStatus.PROCESSING: {
                DocumentState.PREPROCESSING,
                DocumentState.IDENTIFICATION,
                DocumentState.DATA_EXTRACTION,
                DocumentState.VALIDATION,
                DocumentState.UNIFICATION,
                DocumentState.IMAGE_PREPROCESSING,
                DocumentState.PARSING,
                DocumentState.VERSION_IDENTIFICATION,
                DocumentState.POSTPROCESSING,
                DocumentState.EXPORTING,
            },
            FileStatus.FAILED: {DocumentState.FAILED, DocumentState.EXCEPTIONAL_QUEUE, DocumentState.POSTPONED},
            FileStatus.REVIEW: {DocumentState.IN_REVIEW, DocumentState.NEEDS_REVIEW},
            FileStatus.COMPLETED: {DocumentState.COMPLETED},
            FileStatus.EXPORTED: {DocumentState.EXPORTED},
        }

    def cast_into_file_status(self, document_state: str) -> FileStatus:
        for file_status, document_states in self.statuses_mapping.items():
            if document_state in document_states:
                return file_status

        raise RuntimeError(f"Unknown document state: {document_state}")
