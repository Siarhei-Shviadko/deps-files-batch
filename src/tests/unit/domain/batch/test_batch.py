from unittest.mock import ANY

import pytest
from more_itertools import last

from deps_files_batch.domain.exceptions import FileNotFound
from deps_files_batch.domain.model import (
    ABORTED_ERROR_CODE,
    ABORTED_ERROR_MESSAGE,
    Batch,
    BatchFileStatusUpdated,
    BatchProcessed,
    BatchStatus,
    BatchStatusUpdated,
    FileLimitViolated,
    FileStatus,
    ProcessedFile,
    ProcessingParameters,
)
from tests.factories import BatchFactory


def test_add_file__added(batch, file_path, processing_params, document_type_id, file_name):
    batch.add_file(
        file_name=file_name,
        file_path=file_path,
        processing_params=processing_params,
        document_type_id=document_type_id(),
    )

    file = last(batch.files)
    assert file.id
    assert file.name == file_name
    assert file.file_path == file_path
    assert file.processing_params == ProcessingParameters(**processing_params)
    assert file.status == FileStatus.NEW
    assert file.document_id is None
    assert file.error is None


def test_add_file__status_changed(batch, file_id, file_path, processing_params, document_type_id, file_name):
    batch.update_file_status(file_id(), FileStatus.COMPLETED)

    batch.add_file(
        file_name=file_name,
        file_path=file_path,
        processing_params=processing_params,
        document_type_id=document_type_id(),
    )

    assert batch.status == BatchStatus.PROCESSING


def test_add_document_id__no_file__not_found(batch, document_id):
    with pytest.raises(FileNotFound):
        batch.add_document_id(file_id="wrong file id", document_id=document_id())


def test_add_document_id__file_exists__added(batch, file_id, document_id):
    batch.add_document_id(file_id=file_id(), document_id=document_id())

    [file] = batch.files
    assert file.document_id == document_id
    assert file.is_new


def test_add_document_creation_error__no_file__not_found(batch):
    with pytest.raises(FileNotFound):
        batch.add_document_creation_error(file_id="wrong file id")


def test_add_document_creation_error__file__exists__added(batch, file_id):
    batch.add_document_creation_error(file_id=file_id())

    [file] = batch.files
    assert file.error.code == ABORTED_ERROR_CODE
    assert file.error.message == ABORTED_ERROR_MESSAGE
    assert file.is_aborted


def test_new_files__with_new_file__ok(batch):
    assert batch.new_files


def test_new_files__without_new_file__empty_list(aborted_batch):
    assert not aborted_batch.new_files


@pytest.mark.parametrize(
    "new_file_status,expected_file_status,expected_batch_status",
    [
        (FileStatus.PROCESSING, FileStatus.PROCESSING, BatchStatus.PROCESSING),
        (FileStatus.COMPLETED, FileStatus.COMPLETED, BatchStatus.COMPLETED),
        (FileStatus.EXPORTED, FileStatus.EXPORTED, BatchStatus.EXPORTED),
        (FileStatus.REVIEW, FileStatus.REVIEW, BatchStatus.REVIEW),
        (FileStatus.FAILED, FileStatus.FAILED, BatchStatus.FAILED),
    ],
)
def test_update_file_status__batch_and_file_statuses_updated(
    file,
    batch: Batch,
    new_file_status,
    expected_file_status,
    expected_batch_status,
):
    batch.update_file_status(file_id=file.id(), file_status=new_file_status)

    assert batch.status == expected_batch_status
    assert file.status == expected_file_status


def test_document_ids_property__ok():
    batch: Batch = BatchFactory()
    expected_document_ids = [file.document_id() for file in batch if file.document_id]

    actual_document_ids = batch.document_ids

    assert actual_document_ids == expected_document_ids


def test_delete_file__one_file__limit_error(batch, file_id):
    with pytest.raises(FileLimitViolated):
        batch.delete_file(file_id())


def test_delete_aborted_file__batch_status_changed(aborted_batch, file_id, faker):
    aborted_batch.add_file(
        file_name=faker.file_name(),
        file_path=faker.file_path(),
        processing_params={},
        document_type_id=None,
    )

    aborted_batch.delete_file(file_id())

    assert aborted_batch.status == BatchStatus.NEW


def test_update_file_status__status_updated_event_added(file_id, batch: Batch):
    batch.update_file_status(file_id=file_id(), file_status=FileStatus.PROCESSING)

    assert BatchStatusUpdated(batch.id(), status=BatchStatus.PROCESSING) in batch.events


@pytest.mark.parametrize(
    "file_status,batch_status",
    [
        (FileStatus.COMPLETED, BatchStatus.COMPLETED),
        (FileStatus.EXPORTED, BatchStatus.EXPORTED),
        (FileStatus.FAILED, BatchStatus.FAILED),
        (FileStatus.ABORTED, BatchStatus.ABORTED),
    ],
)
def test_update_file_status__end_statuses__events_added(
    file_id,
    batch,
    file_status,
    batch_status,
    tenant_id,
):
    batch.update_file_status(file_id=file_id(), file_status=file_status)

    assert BatchStatusUpdated(batch.id(), status=batch_status) in batch.events
    assert BatchFileStatusUpdated(file_id=file_id(), batch_id=batch.id(), status=file_status) in batch.events
    assert (
        BatchProcessed(
            batch.id(),
            status=batch_status,
            files=[
                ProcessedFile(
                    id=file.id(),
                    status=file.status,
                    document_id=(document_id := file.document_id) and document_id(),
                )
                for file in batch
            ],
            error_message=ANY,
        )
        in batch.events
    )


def test_rename_batch__renamed(batch: Batch, faker):
    expected_name = faker.word()
    batch.rename(expected_name)
    assert batch.name == expected_name


def test_error_message__aborted_batch__ok(aborted_batch):
    assert aborted_batch.error_message


def test_error_message__failed_batch__ok(failed_batch):
    assert failed_batch.error_message


def test_error_message__batch_not_in_error_state__none(batch):
    assert batch.error_message is None


def test_assign_document_type_to_file__file_exists__assigned(batch, file_id, document_type_id):
    batch.assign_document_type_to_file(file_id=file_id(), document_type_id=document_type_id())

    [file] = batch.files
    assert file.document_type_id == document_type_id
