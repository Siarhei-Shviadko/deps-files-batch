from datetime import datetime, timedelta, timezone
from random import randint
from typing import Any

import pytest
from faker.proxy import Faker

from deps_files_batch.constants import DEFAULT_PAGE, DEFAULT_PER_PAGE
from deps_files_batch.domain.model import (
    Batch,
    BatchBuilder,
    BatchFiltering,
    BatchId,
    BatchInfo,
    BatchSorting,
    BatchSortOrder,
    DocumentState,
    FileStatus,
)
from tests.factories import BatchFactory, FileFactory

__all__ = [
    "batch",
    "batch_without_document_type",
    "batch_id",
    "batch_id_without_document",
    "batch_name",
    "save_batch",
    "save_batch_without_document_type",
    "save_batches",
    "aborted_batch",
    "batches",
    "batch_info",
    "batch_with_file_in_processing_status",
    "save_batch_with_file_in_processing_status",
    "list_batch_info",
    "batches_filtering",
    "batches_size",
    "batch_with_file_with_document_id",
    "batch_with_file_with_document_id_without_document_type",
    "save_batch_with_file_with_document_id",
    "batch_with_files",
    "save_batch_with_files",
    "batch_metadata",
    "save_aborted_batch",
    "failed_batch",
    "batch_without_group",
    "save_batch_without_group",
]


@pytest.fixture
def batch_name(faker) -> str:
    return faker.word()


@pytest.fixture
def batch_metadata(faker: Faker) -> dict[str, Any]:
    return faker.pydict(nb_elements=2, allowed_types=(str,))


@pytest.fixture
def batch(batch_name, tenant_id, group_id, file_creation_data, batch_metadata) -> Batch:
    batch = (
        BatchBuilder.for_tenant(tenant_id())
        .with_name(batch_name)
        .with_group_id(group_id())
        .with_metadata(batch_metadata)
        .with_file()
        .with_name(file_creation_data.name)
        .with_path(file_creation_data.file_path)
        .with_document_type_id(file_creation_data.document_type_id)
        .with_processing_params(file_creation_data.processing_params)
        .build()
    )
    batch.events.clear()

    return batch


@pytest.fixture
def batch_without_document_type(
    batch_name, tenant_id, group_id, file_creation_data_without_document_type, batch_metadata
) -> Batch:
    batch = (
        BatchBuilder.for_tenant(tenant_id())
        .with_name(batch_name)
        .with_group_id(group_id())
        .with_metadata(batch_metadata)
        .with_file()
        .with_name(file_creation_data_without_document_type.name)
        .with_path(file_creation_data_without_document_type.file_path)
        .with_document_type_id(file_creation_data_without_document_type.document_type_id)
        .with_processing_params(file_creation_data_without_document_type.processing_params)
        .build()
    )
    batch.events.clear()

    return batch


@pytest.fixture
def batches_size() -> int:
    return randint(2, 10)


@pytest.fixture
def batches(batches_size, tenant_id, batch):
    batches = BatchFactory.create_batch(size=batches_size - 1, tenant_id=tenant_id())
    batches.append(batch)

    return batches


@pytest.fixture
def aborted_batch(batch, file_id):
    batch.add_document_creation_error(file_id=file_id())

    return batch


@pytest.fixture
def failed_batch(batch, file_id):
    batch.update_file_status(file_id=file_id(), file_status=FileStatus.FAILED, error_in_state=DocumentState.EXPORTING)

    return batch


@pytest.fixture
def save_batch(batch, fake_unit_of_work, fake_query_batch_repository) -> None:
    fake_unit_of_work.batches.save(batch)
    fake_query_batch_repository.save(batch)


@pytest.fixture
def save_batch_without_document_type(
    batch_without_document_type, fake_unit_of_work, fake_query_batch_repository
) -> None:
    fake_unit_of_work.batches.save(batch_without_document_type)
    fake_query_batch_repository.save(batch_without_document_type)


@pytest.fixture
def save_aborted_batch(aborted_batch, fake_unit_of_work, fake_query_batch_repository) -> None:
    fake_unit_of_work.batches.save(aborted_batch)
    fake_query_batch_repository.save(aborted_batch)


@pytest.fixture
def batch_with_file_in_processing_status(batch, file_id) -> Batch:
    batch.update_file_status(file_id=file_id(), file_status=FileStatus.PROCESSING)

    return batch


@pytest.fixture
def save_batch_with_file_in_processing_status(batch_with_file_in_processing_status, fake_unit_of_work) -> None:
    fake_unit_of_work.batches.save(batch_with_file_in_processing_status)


@pytest.fixture
def batch_id(batch) -> BatchId:
    return batch.id


@pytest.fixture
def batch_id_without_document(batch_without_document_type) -> BatchId:
    return batch_without_document_type.id


@pytest.fixture
def list_batch_info(batch, list_batch_file_info) -> BatchInfo:
    return BatchInfo(
        id=batch.id(),
        name=batch.name,
        group={"id": batch.group_id(), "name": "group_name"},
        status=batch.status,
        created_at=batch.created_at,
        files=[list_batch_file_info],
    )


@pytest.fixture
def batch_info(batch, file_info) -> BatchInfo:
    return BatchInfo(
        id=batch.id(),
        name=batch.name,
        group={"id": batch.group_id(), "name": "group_name"},
        status=batch.status,
        created_at=batch.created_at,
        files=[file_info],
        metadata=batch.metadata,
    )


@pytest.fixture
def batches_filtering(batch_name, tenant_id, group_id) -> BatchFiltering:
    return BatchFiltering(
        tenant_id=tenant_id(),
        name=batch_name,
        group=group_id(),
        status=["new"],
        date_start=datetime.now(timezone.utc) - timedelta(days=1),
        date_end=datetime.now(timezone.utc),
        sort_by=BatchSorting.sort_by,
        sort_order=BatchSortOrder.DESC,
        per_page=DEFAULT_PER_PAGE,
        page=DEFAULT_PAGE,
    )


@pytest.fixture
def save_batches(batches, fake_unit_of_work, fake_query_batch_repository) -> None:
    for batch in batches:
        fake_unit_of_work.batches.save(batch)
        fake_query_batch_repository.save(batch)


@pytest.fixture
def batch_with_file_with_document_id(batch, document_id) -> Batch:
    [file] = batch.files
    file.add_document_id(document_id())

    return batch


@pytest.fixture
def batch_with_file_with_document_id_without_document_type(batch_without_document_type, document_id) -> Batch:
    [file] = batch_without_document_type.files
    file.add_document_id(document_id())

    return batch_without_document_type


@pytest.fixture
def save_batch_with_file_with_document_id(
    batch_with_file_with_document_id,
    fake_unit_of_work,
    fake_query_batch_repository,
) -> None:
    fake_unit_of_work.batches.save(batch_with_file_with_document_id)
    fake_query_batch_repository.save(batch_with_file_with_document_id)


@pytest.fixture
def batch_with_files(batch, faker):
    batch.add_file(
        file_name=faker.file_name(),
        file_path=faker.file_path(),
        processing_params={},
        document_type_id=None,
    )

    return batch


@pytest.fixture
def save_batch_with_files(batch_with_files, fake_unit_of_work, fake_query_batch_repository):
    fake_unit_of_work.batches.save(batch_with_files)
    fake_query_batch_repository.save(batch_with_files)


@pytest.fixture
def batch_without_group(batch_id, tenant_id, document_type_id) -> Batch:
    return BatchFactory(
        id_=batch_id(),
        tenant_id=tenant_id(),
        updated_at=None,
        group_id=None,
        files=[FileFactory(document_type_id=document_type_id()) for _ in range(randint(1, 10))],
    )


@pytest.fixture
def save_batch_without_group(batch_without_group, fake_unit_of_work, fake_query_batch_repository):
    fake_unit_of_work.batches.save(batch_without_group)
    fake_query_batch_repository.save(batch_without_group)
