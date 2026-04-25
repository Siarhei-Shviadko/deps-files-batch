import pytest

from deps_files_batch.domain.model import Batch, BatchStatus


@pytest.mark.parametrize(
    "setup,expected_status",
    [
        (pytest.lazy_fixture("set_all_file_as_new"), BatchStatus.NEW),
        (pytest.lazy_fixture("set_all_file_as_completed"), BatchStatus.COMPLETED),
        (pytest.lazy_fixture("set_all_file_as_exported"), BatchStatus.EXPORTED),
        (pytest.lazy_fixture("set_file_as_processing"), BatchStatus.PROCESSING),
        (pytest.lazy_fixture("set_file_as_aborted"), BatchStatus.ABORTED),
        (pytest.lazy_fixture("set_file_as_failed"), BatchStatus.FAILED),
        (pytest.lazy_fixture("set_file_as_review"), BatchStatus.REVIEW),
        (pytest.lazy_fixture("set_files_as_aborted_failed_review"), BatchStatus.ABORTED),
        (pytest.lazy_fixture("set_files_as_failed_review"), BatchStatus.FAILED),
        (pytest.lazy_fixture("set_files_as_new_processing_completed_review"), BatchStatus.REVIEW),
    ],
)
@pytest.mark.state_manager
def test_synchronize_status(batch: Batch, setup, expected_status):
    batch._synchronize_status()

    assert batch.status == expected_status
