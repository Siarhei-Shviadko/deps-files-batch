from uuid import uuid4

import pytest

from deps_files_batch.domain.model import FileStatus
from deps_files_batch.messaging.handlers import (
    document_state_updated_handler,
    document_type_assigned_to_document_handler,
)


def test_handler__no_batch__no_error(document_state_updated_dee, document_type_assigned_to_document_dee):
    document_state_updated_handler(document_state_updated_dee)
    document_type_assigned_to_document_handler(document_type_assigned_to_document_dee)


def test_handler__empty_metadata__no_error(
    document_state_updated_dee_with_empty_metadata, document_type_assigned_to_document_dee_with_empty_metadata
):
    document_state_updated_handler(document_state_updated_dee_with_empty_metadata)
    document_type_assigned_to_document_handler(document_type_assigned_to_document_dee_with_empty_metadata)


@pytest.mark.usefixtures("save_batch")
def test_handler__batch_exists__no_file__no_error(document_state_updated_dee, document_type_assigned_to_document_dee):
    document_state_updated_dee.event.metadata["batch_file_id"] = uuid4().hex
    document_state_updated_handler(document_state_updated_dee)
    document_type_assigned_to_document_handler(document_type_assigned_to_document_dee)


@pytest.mark.usefixtures("save_batch_without_document_type")
def test_handler__batch_without_document_type_exists__no_file__no_error(
    document_state_updated_dee, document_type_assigned_to_document_dee
):
    document_type_assigned_to_document_dee.event.metadata["batch_file_id"] = uuid4().hex
    document_type_assigned_to_document_handler(document_type_assigned_to_document_dee)


@pytest.mark.usefixtures("save_batch")
def test_handler__updated(document_state_updated_dee, fake_unit_of_work, batch, file_id):
    document_state_updated_handler(document_state_updated_dee)

    saved_batch = fake_unit_of_work.batches.batch_of_id(batch_id=batch.id(), tenant_id=batch.tenant_id())
    updated_file = saved_batch.file_of_id(file_id)
    assert updated_file.status == FileStatus.PROCESSING


@pytest.mark.usefixtures("save_batch_without_document_type")
def test_handler__assigned_to_document(
    document_type_assigned_to_document_dee,
    fake_unit_of_work,
    batch_without_document_type,
    file_id_without_document_type,
    document_type_id,
):
    document_type_assigned_to_document_handler(document_type_assigned_to_document_dee)

    saved_batch = fake_unit_of_work.batches.batch_of_id(
        batch_id=batch_without_document_type.id(), tenant_id=batch_without_document_type.tenant_id()
    )
    updated_file = saved_batch.file_of_id(file_id_without_document_type)
    assert updated_file.document_type_id == document_type_id
