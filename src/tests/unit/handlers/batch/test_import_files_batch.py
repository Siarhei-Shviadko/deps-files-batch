import json

import pytest
from deps_message_flow.commands.common import CommandReplyOutcome, ReplyMessageHeaders

from deps_files_batch.domain.model import ProcessingParameters
from deps_files_batch.messaging.handlers import import_files_batch


@pytest.mark.usefixtures("save_group")
def test_handler__success__created(
    import_files_batch_command_message,
    file_creation_data_dict,
    fake_unit_of_work,
    batch_metadata,
    batch_name,
    tenant_id,
    group_id,
):
    [reply_message] = import_files_batch(import_files_batch_command_message)

    assert reply_message.get_required_header(ReplyMessageHeaders.REPLY_OUTCOME) == CommandReplyOutcome.SUCCESS.value
    payload = json.loads(reply_message.payload)
    payload_batch_id = payload["batch_id"]
    saved_batch = fake_unit_of_work.batches.batch_of_id(batch_id=payload_batch_id, tenant_id=tenant_id())
    assert saved_batch.name == batch_name
    assert saved_batch.tenant_id == tenant_id
    assert saved_batch.metadata == batch_metadata
    assert saved_batch.group_id == group_id
    [saved_file] = saved_batch.files
    assert saved_file.name == file_creation_data_dict["name"]
    assert saved_file.file_path == file_creation_data_dict["file_path"]
    assert saved_file.processing_params == ProcessingParameters(**file_creation_data_dict["processing_params"])
    assert saved_file.document_type_id() == file_creation_data_dict["document_type_id"]


def test_handler__error__failure_reply(import_files_batch_command_message):
    [reply_message] = import_files_batch(import_files_batch_command_message)

    assert reply_message.get_required_header(ReplyMessageHeaders.REPLY_OUTCOME) == CommandReplyOutcome.FAILURE.value
