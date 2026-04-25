import pytest
from sqlalchemy import text

from deps_files_batch.domain.model import (
    Batch,
    BatchId,
    File,
    Group,
    ICommandBatchRepository,
    ProcessingParametersDict,
    TenantId,
)
from deps_files_batch.infrastructure.unit_of_work import SqlAlchemyUnitOfWork

from .helpers import compare_batches, sort_entities_by_id


@pytest.mark.usefixtures("save_group")
@pytest.mark.batch_command_repository
def test_save_batch__valid_batch__saved(
    batch_with_n_files: Batch,
    group: Group,
    unit_of_work: SqlAlchemyUnitOfWork,
    batch_command_repository: ICommandBatchRepository,
    batch_id: BatchId,
    tenant_id: TenantId,
):
    batch_command_repository.save(batch_with_n_files)
    saved_batch = batch_command_repository.batch_of_id(batch_id=batch_id(), tenant_id=tenant_id())
    compare_batches(batch_with_n_files, saved_batch)


@pytest.mark.batch_command_repository
def test_get_batch__not_exists__none(
    unit_of_work: SqlAlchemyUnitOfWork,
    batch_command_repository: ICommandBatchRepository,
    tenant_id: TenantId,
    faker,
):
    assert batch_command_repository.batch_of_id(batch_id=faker.uuid4(), tenant_id=tenant_id()) is None


@pytest.mark.usefixtures("save_group")
@pytest.mark.batch_command_repository
def test_save_batch__batch_and_files_are_modified__updated(
    batch_with_n_files: Batch,
    unit_of_work: SqlAlchemyUnitOfWork,
    batch_command_repository: ICommandBatchRepository,
    file: File,
    batch_id: BatchId,
    tenant_id: TenantId,
    faker,
):
    batch_command_repository.save(batch_with_n_files)
    initial_batch = batch_command_repository.batch_of_id(batch_id=batch_id(), tenant_id=tenant_id())

    initial_batch.delete_file(file.id())
    initial_batch.add_file(
        file_name=faker.file_name(extension="pdf"),
        file_path=faker.file_path(extension="pdf"),
        processing_params=ProcessingParametersDict(),
        document_type_id=None,
    )
    initial_batch._synchronize_status()
    batch_command_repository.save(initial_batch)

    final_batch = batch_command_repository.batch_of_id(batch_id=batch_id(), tenant_id=tenant_id())
    compare_batches(initial_batch, final_batch)


@pytest.mark.usefixtures("save_group", "save_batches")
@pytest.mark.batch_command_repository
def test_get_several_batches__all_got_and_valid(
    group: Group,
    batches: list[Batch],
    batches_ids: set[str],
    batch_command_repository: ICommandBatchRepository,
    tenant_id: TenantId,
):
    saved_batches = batch_command_repository.batches_of_ids(ids=batches_ids, tenant_id=tenant_id())
    assert len(saved_batches) == len(batches)
    for batch, saved_batch in zip(sort_entities_by_id(batches), sort_entities_by_id(saved_batches)):
        compare_batches(batch, saved_batch)


@pytest.mark.usefixtures("save_group", "save_batches")
@pytest.mark.batch_command_repository
def test_get_several_batches__not_found_empty_list(
    batch_command_repository: ICommandBatchRepository, tenant_id: TenantId, faker
):
    found_batches = batch_command_repository.batches_of_ids(
        ids={faker.uuid4() for _ in range(5)}, tenant_id=tenant_id()
    )
    assert found_batches == []


@pytest.mark.usefixtures("save_group", "save_batches")
@pytest.mark.batch_command_repository
def test_delete_batches__deleted(
    batches: list[Batch],
    batches_ids: set[str],
    batch_command_repository: ICommandBatchRepository,
    tenant_id: TenantId,
):
    def check_all_files_deleted():
        count_files_of_batches = text(f"SELECT COUNT(id) FROM file WHERE batch_id IN {tuple(batches_ids)}")
        assert batch_command_repository._connection.execute(count_files_of_batches).scalar() == 0

    batch_command_repository.delete_all(batches)
    assert batch_command_repository.batches_of_ids(batches_ids, tenant_id()) == []
    check_all_files_deleted()
