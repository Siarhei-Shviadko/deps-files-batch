import pytest

from deps_files_batch.application import BatchService, StartBatchProcessing
from deps_files_batch.constants import (
    COMMANDS_REPLIES_CHANNEL,
    DOCUMENT_COMMANDS_CHANNEL,
)
from tests.fakes import FakeCommandProducer


@pytest.mark.usefixtures("save_batch")
def test_add_documents_creation_result__no_error__command_sent(
    documents_creation_result_with_document_id,
    fake_command_producer: FakeCommandProducer,
    batch_service: BatchService,
    document_id,
    tenant_id,
    batch,
):
    batch_service.add_documents_creation_result(
        batch_id=batch.id(),
        tenant_id=tenant_id(),
        documents_creation_result=[documents_creation_result_with_document_id],
    )

    [sent_command] = fake_command_producer.sent
    assert sent_command.channel == DOCUMENT_COMMANDS_CHANNEL
    assert sent_command.reply_to == COMMANDS_REPLIES_CHANNEL
    assert sent_command.command == StartBatchProcessing(documents=[document_id()])
