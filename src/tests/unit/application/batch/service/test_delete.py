import pytest

from deps_files_batch.application import BatchService, DeleteBatchDocument
from deps_files_batch.constants import (
    COMMANDS_REPLIES_CHANNEL,
    DOCUMENT_COMMANDS_CHANNEL,
)


@pytest.mark.usefixtures("save_batch")
def test_delete_batches__deleted(batch_service: BatchService, fake_unit_of_work, tenant_id, batch_id):
    batch_service.delete_batches(ids={batch_id()}, tenant_id=tenant_id())

    assert not fake_unit_of_work.batches.batch_of_id(batch_id(), tenant_id())


@pytest.mark.usefixtures("save_batch")
def test_delete_batches_with_documents__deleted(batch_service: BatchService, fake_unit_of_work, tenant_id, batch_id):
    batch_service.delete_batches_with_documents(ids={batch_id()}, tenant_id=tenant_id())

    assert not fake_unit_of_work.batches.batch_of_id(batch_id(), tenant_id())


@pytest.mark.usefixtures("save_batch")
def test_delete_batches__no_document_ids__command_not_sent(
    batch_service: BatchService,
    fake_command_producer,
    document_id,
    tenant_id,
    batch_id,
):
    batch_service.delete_batches_with_documents(ids={batch_id()}, tenant_id=tenant_id())

    assert not fake_command_producer.sent


@pytest.mark.usefixtures("save_batch_with_file_with_document_id")
def test_delete_batches_with_documents__command_sent(
    batch_service: BatchService,
    fake_command_producer,
    document_id,
    tenant_id,
    batch_id,
):
    batch_service.delete_batches_with_documents(ids={batch_id()}, tenant_id=tenant_id())

    [sent_command] = fake_command_producer.sent
    assert sent_command.channel == DOCUMENT_COMMANDS_CHANNEL
    assert sent_command.command == DeleteBatchDocument(document_id())
    assert sent_command.reply_to == COMMANDS_REPLIES_CHANNEL


@pytest.mark.usefixtures("save_batch_with_files")
def test_delete_files__deleted(
    batch_service: BatchService,
    fake_unit_of_work,
    tenant_id,
    batch_id,
    file_id,
):
    batch_service.delete_files_with_documents(batch_id=batch_id(), file_ids=[file_id()], tenant_id=tenant_id())

    batch = fake_unit_of_work.batches.batch_of_id(batch_id(), tenant_id())
    assert not file_id in batch.file_storage


@pytest.mark.usefixtures("save_batch_with_files")
def test_delete_files__no_document_id__command_not_sent(
    batch_service: BatchService,
    fake_command_producer,
    tenant_id,
    batch_id,
    file_id,
):
    batch_service.delete_files_with_documents(batch_id=batch_id(), file_ids=[file_id()], tenant_id=tenant_id())

    assert not fake_command_producer.sent


@pytest.mark.usefixtures("save_batch_with_files")
def test_delete_files__document_id_added__command_sent(
    batch_service: BatchService,
    fake_command_producer,
    document_id,
    tenant_id,
    batch_id,
    file,
):
    file.add_document_id(document_id())

    batch_service.delete_files_with_documents(batch_id=batch_id(), file_ids=[file.id()], tenant_id=tenant_id())

    [sent_command] = fake_command_producer.sent
    assert sent_command.channel == DOCUMENT_COMMANDS_CHANNEL
    assert sent_command.command == DeleteBatchDocument(document_id())
    assert sent_command.reply_to == COMMANDS_REPLIES_CHANNEL
