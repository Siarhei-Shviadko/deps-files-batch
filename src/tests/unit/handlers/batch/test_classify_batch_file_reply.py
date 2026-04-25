import pytest
from pytest_mock import MockerFixture

from deps_files_batch.application import BatchService
from deps_files_batch.messaging.handlers import classify_batch_file_reply_handler
from tests.fakes import FakeCommandProducer


def test_handler__no_batch__business_error__no_error(classify_batch_file_reply_success):
    classify_batch_file_reply_handler(classify_batch_file_reply_success)


def test_handler__system_error__error(classify_batch_file_reply_success, mocker: MockerFixture):
    with mocker.patch.object(BatchService, "add_file_classification_result", side_effect=SystemError):
        with pytest.raises(SystemError):
            classify_batch_file_reply_handler(classify_batch_file_reply_success)


@pytest.mark.usefixtures("save_batch")
def test_handler__ok_file__file_updated(
    fake_command_producer: FakeCommandProducer,
    classify_batch_file_reply_success,
    fake_unit_of_work,
    batch,
):
    classify_batch_file_reply_handler(classify_batch_file_reply_success)

    [updated_file] = fake_unit_of_work.batches.batch_of_id(batch_id=batch.id(), tenant_id=batch.tenant_id()).files
    assert updated_file.document_id
    assert updated_file.error is None
    assert fake_command_producer.sent


@pytest.mark.usefixtures("save_batch")
def test_handler__error_file__file_updated(
    fake_command_producer: FakeCommandProducer,
    classify_batch_file_reply_error,
    fake_unit_of_work,
    batch,
):
    classify_batch_file_reply_handler(classify_batch_file_reply_error)

    [updated_file] = fake_unit_of_work.batches.batch_of_id(batch_id=batch.id(), tenant_id=batch.tenant_id()).files
    assert updated_file.error
    assert updated_file.document_id is None
    assert not fake_command_producer.sent
