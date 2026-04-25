import pytest
from more_itertools.more import first

from deps_files_batch.domain.exceptions import IllegalArgument, LimitExceeded
from deps_files_batch.domain.model import (
    MAX_BATCH_FILES_AMOUNT,
    MAX_BATCH_NAME_LENGTH,
    BatchBuilder,
    BatchCreated,
    BatchStatus,
)


def test_create__with_optional__created(batch_name, tenant_id, file_creation_data, group_id, document_type_id):
    batch = (
        BatchBuilder.for_tenant(tenant_id())
        .with_name(batch_name)
        .with_group_id(group_id())
        .with_file()
        .with_name(file_creation_data.name)
        .with_path(file_creation_data.file_path)
        .with_processing_params(file_creation_data.processing_params)
        .with_document_type_id(document_type_id())
        .build()
    )

    assert batch.id
    assert batch.tenant_id == tenant_id
    assert batch.name == batch_name
    assert batch.status == BatchStatus.NEW
    assert batch.files
    assert batch.metadata == {}
    assert batch.created_at
    assert batch.updated_at is None
    assert batch.group_id == group_id
    assert batch.commands == []
    assert (
        BatchCreated(
            id=batch.id(),
            name=batch_name,
            group_id=group_id(),
            files=[f.id() for f in batch.files],
        )
        in batch.events
    )


def test_create__without_optional__created(batch_name, tenant_id, file_path, file_name):
    batch = (
        BatchBuilder.for_tenant(tenant_id())
        .with_name(batch_name)
        .with_file()
        .with_name(file_name)
        .with_path(file_path)
        .build()
    )
    assert batch.group_id is None
    assert (
        BatchCreated(
            id=batch.id(),
            name=batch_name,
            group_id=None,
            files=[first(batch.files).id()],
        )
        in batch.events
    )


def test_create__too_many_files__error(faker, batch_name, tenant_id):
    builder = BatchBuilder.for_tenant(tenant_id()).with_name(batch_name)
    for i in range(MAX_BATCH_FILES_AMOUNT + 1):
        name = faker.file_name(extension="pdf")
        path = faker.file_path(extension="pdf")
        builder = builder.with_file().with_name(name).with_path(path)
    with pytest.raises(LimitExceeded):
        builder.build()


def test_create__too_long_batch_name__error(tenant_id, file_path):
    batch_name = "a" * (MAX_BATCH_NAME_LENGTH + 1)
    builder = BatchBuilder.for_tenant(tenant_id()).with_name(batch_name).with_file().with_path(file_path)
    with pytest.raises(IllegalArgument):
        builder.build()
