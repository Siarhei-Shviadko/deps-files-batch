import pytest

from deps_files_batch.application import DocumentStateCaster
from deps_files_batch.domain.model import DocumentState, FileStatus


@pytest.mark.parametrize(
    "document_state,expected_file_state",
    [
        (DocumentState.PREPROCESSING, FileStatus.PROCESSING),
        (DocumentState.IDENTIFICATION, FileStatus.PROCESSING),
        (DocumentState.DATA_EXTRACTION, FileStatus.PROCESSING),
        (DocumentState.VALIDATION, FileStatus.PROCESSING),
        (DocumentState.IN_REVIEW, FileStatus.REVIEW),
        (DocumentState.FAILED, FileStatus.FAILED),
        (DocumentState.COMPLETED, FileStatus.COMPLETED),
        (DocumentState.EXPORTED, FileStatus.EXPORTED),
        (DocumentState.UNIFICATION, FileStatus.PROCESSING),
        (DocumentState.IMAGE_PREPROCESSING, FileStatus.PROCESSING),
        (DocumentState.PARSING, FileStatus.PROCESSING),
        (DocumentState.VERSION_IDENTIFICATION, FileStatus.PROCESSING),
        (DocumentState.POSTPROCESSING, FileStatus.PROCESSING),
        (DocumentState.NEEDS_REVIEW, FileStatus.REVIEW),
        (DocumentState.EXPORTING, FileStatus.PROCESSING),
        (DocumentState.EXCEPTIONAL_QUEUE, FileStatus.FAILED),
        (DocumentState.POSTPONED, FileStatus.FAILED),
    ],
)
def test_cast_into_file_status__ok(document_state, expected_file_state):
    file_state = DocumentStateCaster().cast_into_file_status(document_state)

    assert file_state == expected_file_state


def test_cast_into_file_status__unknown_file_state__error():
    with pytest.raises(RuntimeError):
        DocumentStateCaster().cast_into_file_status("unknown_document_state")
