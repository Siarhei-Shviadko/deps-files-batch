import pytest

from deps_files_batch.application import BatchService
from deps_files_batch.domain.model import Batch


@pytest.fixture
def expected_name(faker):
    return faker.word()


@pytest.mark.usefixtures("save_batch_with_files")
def test_rename_batch__successfully_renamed(
    batch_service: BatchService,
    fake_unit_of_work,
    batch_with_files: Batch,
    batch_id,
    tenant_id,
    expected_name,
):
    batch_service.rename_batch(batch_id=batch_id(), tenant_id=tenant_id(), new_name=expected_name)

    assert (saved_batch := fake_unit_of_work.batches.batch_of_id(batch_id=batch_id(), tenant_id=tenant_id()))
    assert saved_batch.name == expected_name
