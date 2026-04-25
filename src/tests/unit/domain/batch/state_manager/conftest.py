import pytest
from faker.proxy import Faker

from deps_files_batch.domain.model import Batch, FileStatus, ProcessingParametersDict

FILE_STATUSES_AMOUNT = len(FileStatus)
NEW, PROCESSING, COMPLETED, REVIEW, FAILED, ABORTED, EXPORTED = range(FILE_STATUSES_AMOUNT)


@pytest.fixture
def batch(batch: Batch, faker: Faker) -> Batch:
    for _ in range(FILE_STATUSES_AMOUNT):
        batch.add_file(
            file_name=faker.file_name(extension="pdf"),
            file_path=faker.file_path(extension="pdf"),
            processing_params=ProcessingParametersDict(),
            document_type_id=None,
        )

    return batch


@pytest.fixture
def set_all_file_as_new(batch):
    for file in batch:
        file.status = FileStatus.NEW


@pytest.fixture
def set_all_file_as_completed(batch):
    for file in batch:
        file._set_completed_state()


@pytest.fixture
def set_all_file_as_exported(batch):
    for file in batch:
        file._set_exported_state()


@pytest.fixture
def set_file_as_processing(batch):
    batch.files[PROCESSING]._set_processing_state()


@pytest.fixture
def set_file_as_completed(batch):
    batch.files[COMPLETED]._set_completed_state()


@pytest.fixture
def set_file_as_review(batch):
    batch.files[REVIEW]._set_review_state()


@pytest.fixture
def set_file_as_failed(batch):
    batch.files[FAILED]._set_failed_state()


@pytest.fixture
def set_file_as_aborted(batch):
    batch.files[ABORTED]._set_aborted_state()


@pytest.fixture
def set_files_as_aborted_failed_review(set_file_as_aborted, set_file_as_failed, set_file_as_review):
    pass


@pytest.fixture
def set_files_as_failed_review(set_file_as_failed, set_file_as_review):
    pass


@pytest.fixture
def set_files_as_new_processing_completed_review(set_file_as_review, set_file_as_completed, set_file_as_processing):
    pass
