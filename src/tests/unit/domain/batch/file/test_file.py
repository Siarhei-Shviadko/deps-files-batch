import pytest

from deps_files_batch.domain.model import (
    ABORTED_ERROR_CODE,
    ABORTED_ERROR_MESSAGE,
    DATA_EXTRACTION_ERROR_CODE,
    DATA_EXTRACTION_ERROR_MESSAGE,
    DEFAULT_ERROR_CODE,
    DEFAULT_ERROR_MESSAGE,
    EXPORTING_ERROR_CODE,
    EXPORTING_ERROR_MESSAGE,
    IDENTIFICATION_ERROR_CODE,
    IDENTIFICATION_ERROR_MESSAGE,
    IMAGE_PREPROCESSING_ERROR_CODE,
    IMAGE_PREPROCESSING_ERROR_MESSAGE,
    PARSING_ERROR_CODE,
    PARSING_ERROR_MESSAGE,
    POSTPROCESSING_ERROR_CODE,
    POSTPROCESSING_ERROR_MESSAGE,
    PREPROCESSING_ERROR_CODE,
    PREPROCESSING_ERROR_MESSAGE,
    UNIFICATION_ERROR_CODE,
    UNIFICATION_ERROR_MESSAGE,
    VALIDATION_ERROR_CODE,
    VALIDATION_ERROR_MESSAGE,
    VERSION_IDENTIFICATION_ERROR_CODE,
    VERSION_IDENTIFICATION_ERROR_MESSAGE,
    BatchFileStatusUpdated,
    DocumentState,
    Error,
    FileStatus,
)


def test_is_new__ok(file):
    assert file.is_new


def test_set_aborted__ok(file):
    file._set_aborted_state()

    assert file.status == FileStatus.ABORTED
    assert file.error == Error(code=ABORTED_ERROR_CODE, message=ABORTED_ERROR_MESSAGE)


def test_set_failed__ok(file):
    file._set_failed_state()

    assert file.status == FileStatus.FAILED
    assert file.error == Error(code=DEFAULT_ERROR_CODE, message=DEFAULT_ERROR_MESSAGE)


def test_set_review__ok(file):
    file._set_review_state()

    assert file.status == FileStatus.REVIEW


def test_set_completed__ok(file):
    file._set_completed_state()

    assert file.status == FileStatus.COMPLETED


def test_set_exported__ok(file):
    file._set_exported_state()

    assert file.status == FileStatus.EXPORTED


def test_set_processing__ok(file):
    file._set_processing_state()

    assert file.status == FileStatus.PROCESSING


def test_is_aborted__ok(file):
    file._set_aborted_state()

    assert file.is_aborted


def test_add_document_id__ok(file, document_id):
    file.add_document_id(document_id())

    assert file.document_id == document_id


@pytest.mark.parametrize(
    "status",
    [FileStatus.PROCESSING, FileStatus.COMPLETED, FileStatus.EXPORTED, FileStatus.REVIEW, FileStatus.FAILED],
)
def test_update_status__ok(file, status):
    file.update_status(status)

    assert file.status == status


@pytest.mark.parametrize(
    "document_state,error_code,error_message",
    [
        (DocumentState.PREPROCESSING, PREPROCESSING_ERROR_CODE, PREPROCESSING_ERROR_MESSAGE),
        (DocumentState.IDENTIFICATION, IDENTIFICATION_ERROR_CODE, IDENTIFICATION_ERROR_MESSAGE),
        (DocumentState.DATA_EXTRACTION, DATA_EXTRACTION_ERROR_CODE, DATA_EXTRACTION_ERROR_MESSAGE),
        (DocumentState.VALIDATION, VALIDATION_ERROR_CODE, VALIDATION_ERROR_MESSAGE),
        (DocumentState.UNIFICATION, UNIFICATION_ERROR_CODE, UNIFICATION_ERROR_MESSAGE),
        (DocumentState.IMAGE_PREPROCESSING, IMAGE_PREPROCESSING_ERROR_CODE, IMAGE_PREPROCESSING_ERROR_MESSAGE),
        (DocumentState.PARSING, PARSING_ERROR_CODE, PARSING_ERROR_MESSAGE),
        (DocumentState.VERSION_IDENTIFICATION, VERSION_IDENTIFICATION_ERROR_CODE, VERSION_IDENTIFICATION_ERROR_MESSAGE),
        (DocumentState.POSTPROCESSING, POSTPROCESSING_ERROR_CODE, POSTPROCESSING_ERROR_MESSAGE),
        (DocumentState.EXPORTING, EXPORTING_ERROR_CODE, EXPORTING_ERROR_MESSAGE),
        ("new_document_state", DEFAULT_ERROR_CODE, DEFAULT_ERROR_MESSAGE),
    ],
)
def test_update_status__error_added(file, document_state, error_code, error_message):
    status = FileStatus.FAILED
    file.update_status(status=status, error_in_state=document_state)

    assert file.status == status
    assert file.error == Error(code=error_code, message=error_message)


def test_update_status__new_status__event_added(file):
    new_status = FileStatus.PROCESSING

    file.update_status(new_status)

    assert BatchFileStatusUpdated(file_id=file.id(), status=new_status) in file.events


def test_update_status__same_status__event_not_added(file):
    file.update_status(FileStatus.NEW)

    assert not file.events


def test_update_status__error_cleared(file):
    file.update_status(FileStatus.FAILED)

    file.update_status(FileStatus.COMPLETED)

    assert file.error is None


def test_assign_document_type__ok(file, document_type_id):
    file.assign_document_type(document_type_id())

    assert file.document_type_id == document_type_id


def test_error_message__aborted__ok(aborted_file):
    assert aborted_file.error_message


def test_error_message__failed__ok(failed_file):
    assert failed_file.error_message


def test_error_message__file_not_in_error_state__none(file):
    assert file.error_message is None
