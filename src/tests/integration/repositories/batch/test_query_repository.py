import pytest
from pytest import lazy_fixture as lazy

from deps_files_batch.domain.model import (
    Batch,
    BatchFiltering,
    BatchId,
    BatchSorting,
    IQueryBatchRepository,
    Pagination,
    TenantId,
)

from .helpers import (
    apply_sorting_filtering_and_pagination_to_batches,
    calculate_total_records_from_batches,
    compare_batch_and_batch_info,
    compare_batch_and_list_batch_unit,
)


@pytest.mark.batch_query_repository
def test_find_batch__no_batch__none(
    query_batch_repository: IQueryBatchRepository, batch_id: BatchId, tenant_id: TenantId
):
    batch_info = query_batch_repository.find_batch(batch_id=batch_id(), tenant_id=tenant_id())
    assert batch_info is None


@pytest.mark.batch_query_repository
@pytest.mark.usefixtures("save_group", "save_batch")
def test_find_batch__has_batch__valid_response(
    query_batch_repository: IQueryBatchRepository, batch_id: BatchId, tenant_id: TenantId, batch: Batch, group_name: str
):
    batch_info = query_batch_repository.find_batch(batch_id=batch_id(), tenant_id=tenant_id())
    compare_batch_and_batch_info(batch=batch, batch_info=batch_info, group_name=group_name)


@pytest.mark.batch_query_repository
@pytest.mark.usefixtures("save_group", "save_batches")
@pytest.mark.parametrize(
    "filtering,sorting,pagination",
    [
        (lazy("empty_filter"), lazy("default_sorting"), lazy("default_pagination")),
        (lazy("name_filter"), lazy("default_sorting"), lazy("default_pagination")),
        (lazy("status_filter"), lazy("default_sorting"), lazy("default_pagination")),
        (lazy("group_filter"), lazy("default_sorting"), lazy("default_pagination")),
        (lazy("date_start_filter"), lazy("default_sorting"), lazy("default_pagination")),
        (lazy("date_end_filter"), lazy("default_sorting"), lazy("default_pagination")),
        (lazy("empty_filter"), lazy("reversed_sorting"), lazy("default_pagination")),
        (lazy("empty_filter"), lazy("name_sorting"), lazy("default_pagination")),
        (lazy("empty_filter"), lazy("status_sorting"), lazy("default_pagination")),
        (lazy("empty_filter"), lazy("group_sorting"), lazy("default_pagination")),
        (lazy("empty_filter"), lazy("default_sorting"), lazy("next_page_pagination")),
        (lazy("empty_filter"), lazy("default_sorting"), lazy("one_record_pagination")),
    ],
)
def test_find_all_with__filters_and_stuff__valid_response(
    query_batch_repository: IQueryBatchRepository,
    batch_id: BatchId,
    tenant_id: TenantId,
    batches: list[Batch],
    filtering: BatchFiltering,
    sorting: BatchSorting,
    pagination: Pagination,
    group_name: str,
):
    expected_batches = apply_sorting_filtering_and_pagination_to_batches(
        batches=batches, filtering=filtering, sorting=sorting, pagination=pagination
    )
    result = query_batch_repository.find_all_with(filtering=filtering, sorting=sorting, pagination=pagination)
    assert len(expected_batches) == result["metadata"]["size"] == len(result["batches"])
    assert result["metadata"]["total"] == calculate_total_records_from_batches(batches, filtering)
    for batch, batch_info in zip(expected_batches, result["batches"]):
        compare_batch_and_list_batch_unit(batch=batch, batch_info=batch_info, group_name=group_name)
