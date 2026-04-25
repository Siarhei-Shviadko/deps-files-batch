import pytest
from more_itertools import first

from deps_files_batch.application import DeleteBatchDocument
from deps_files_batch.constants import (
    COMMANDS_REPLIES_CHANNEL,
    DOCUMENT_COMMANDS_CHANNEL,
)
from deps_files_batch.messaging.handlers import delete_batches_with_documents_handler


@pytest.mark.usefixtures("save_batch_with_file_with_document_id")
def test_delete_batch_with_documents_handler__calls_service(
    delete_batches_with_documents_command_message,
    fake_command_producer,
    fake_unit_of_work,
    document_id,
    tenant_id,
    batch_id,
):
    delete_batches_with_documents_handler(delete_batches_with_documents_command_message)

    assert not fake_unit_of_work.batches.batch_of_id(batch_id(), tenant_id())
    sent_command = first(fake_command_producer.sent)
    assert sent_command.channel == DOCUMENT_COMMANDS_CHANNEL
    assert sent_command.command == DeleteBatchDocument(document_id())
    assert sent_command.reply_to == COMMANDS_REPLIES_CHANNEL
