import pytest
from pytest_mock import MockerFixture

from deps_files_batch.application import BatchService
from deps_files_batch.domain.model import DocumentState


@pytest.mark.usefixtures("save_batch_with_file_in_processing_status")
def test_update_file_status__status_not_changed__batch_not_changed(
    batch_service: BatchService,
    mocker: MockerFixture,
    tenant_id,
    batch_id,
    file_id,
):
    save_batch_method_mock = mocker.patch.object(BatchService, "_save_batch", return_value=None)
    batch_service.update_file_status(
        batch_id=batch_id(),
        tenant_id=tenant_id(),
        file_id=file_id(),
        document_state=DocumentState.VALIDATION,
    )

    save_batch_method_mock.assert_not_called()
