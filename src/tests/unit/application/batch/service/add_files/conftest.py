import pytest

from deps_files_batch.domain.model import Batch, BatchStatus, FileStatus
from tests.factories import BatchFactory, FileFactory


@pytest.fixture
def completed_batch(batch_id, tenant_id, group_id) -> Batch:
    return BatchFactory(
        id_=batch_id(),
        tenant_id=tenant_id(),
        group_id=group_id(),
        status=BatchStatus.COMPLETED,
        updated_at=None,
        files=[FileFactory(status=FileStatus.COMPLETED)],
    )


@pytest.fixture
def save_completed_batch(completed_batch, fake_unit_of_work):
    fake_unit_of_work.batches.save(completed_batch)
