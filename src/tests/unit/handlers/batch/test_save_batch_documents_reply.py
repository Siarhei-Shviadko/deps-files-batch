import pytest
from pytest_mock import MockerFixture

from deps_files_batch.application import BatchService
from deps_files_batch.messaging.handlers import save_batch_documents_reply_handler
from tests.fakes import FakeCommandProducer


def test_handler__no_batch__business_error__no_error(save_batch_documents_success_reply):
    save_batch_documents_reply_handler(save_batch_documents_success_reply)


def test_handler__system_error__error(save_batch_documents_success_reply, mocker: MockerFixture):
    with mocker.patch.object(BatchService, "add_documents_creation_result", side_effect=SystemError):
        with pytest.raises(SystemError):
            save_batch_documents_reply_handler(save_batch_documents_success_reply)


@pytest.mark.usefixtures("save_batch")
def test_handler__ok_file__file_updated(
    fake_command_producer: FakeCommandProducer,
    save_batch_documents_success_reply,
    fake_unit_of_work,
    batch,
):
    save_batch_documents_reply_handler(save_batch_documents_success_reply)

    [updated_file] = fake_unit_of_work.batches.batch_of_id(batch_id=batch.id(), tenant_id=batch.tenant_id()).files
    assert updated_file.document_id
    assert updated_file.error is None
    assert fake_command_producer.sent


@pytest.mark.usefixtures("save_batch")
def test_handler__error_file__file_updated(
    fake_command_producer: FakeCommandProducer,
    save_batch_documents_error_reply,
    fake_unit_of_work,
    batch,
):
    save_batch_documents_reply_handler(save_batch_documents_error_reply)

    [updated_file] = fake_unit_of_work.batches.batch_of_id(batch_id=batch.id(), tenant_id=batch.tenant_id()).files
    assert updated_file.error
    assert updated_file.document_id is None
    assert not fake_command_producer.sent
