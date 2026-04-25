from factory import Faker

from deps_files_batch.domain.model import ProcessingParametersDict
from tests.factories import BatchFactory, FileFactory

from .filtering_fixtures import *


@pytest.fixture
def batch_command_repository(unit_of_work):
    return unit_of_work.batches


@pytest.fixture
def query_batch_repository(repositories):
    return repositories.query_batch()


@pytest.fixture
def batch_with_n_files(batch: Batch, document_type_id, faker: Faker) -> Batch:
    for _ in range(10):
        batch.add_file(
            file_name=faker.file_name(extension="pdf"),
            file_path=faker.file_path(extension="pdf"),
            processing_params=ProcessingParametersDict(),
            document_type_id=None,
        )
    return batch


@pytest.fixture
def save_group(group, unit_of_work):
    unit_of_work.groups.save(group)


@pytest.fixture
def save_batch(batch: Batch, batch_command_repository):
    batch_command_repository.save(batch)


@pytest.fixture
def batches(group_id, tenant_id, document_type_id):
    return [
        BatchFactory(
            group_id=group_id(),
            tenant_id=tenant_id(),
            files=FileFactory.create_batch(5, document_type_id=document_type_id()),
        )
        for _ in range(10)
    ]


@pytest.fixture
def batches_ids(batches) -> set[str]:
    return {b.id() for b in batches}


@pytest.fixture
def save_batches(batches, batch_command_repository):
    for batch in batches:
        batch_command_repository.save(batch)
