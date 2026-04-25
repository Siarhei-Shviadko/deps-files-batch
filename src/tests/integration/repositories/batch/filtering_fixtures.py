import pytest
from more_itertools import first

from deps_files_batch.domain.model import (
    Batch,
    BatchFiltering,
    BatchSortBy,
    BatchSorting,
    BatchSortOrder,
    Pagination,
    TenantId,
)


@pytest.fixture
def first_batch(batches) -> Batch:
    return first(batches)


@pytest.fixture
def empty_filter(tenant_id: TenantId) -> BatchFiltering:
    return BatchFiltering(tenant_id=tenant_id())


@pytest.fixture
def name_filter(tenant_id: TenantId, first_batch: Batch) -> BatchFiltering:
    return BatchFiltering(tenant_id=tenant_id(), name=first_batch.name)


@pytest.fixture
def status_filter(tenant_id: TenantId, first_batch: Batch) -> BatchFiltering:
    return BatchFiltering(tenant_id=tenant_id(), status=[first_batch.status()])


@pytest.fixture
def group_filter(tenant_id: TenantId, group_name) -> BatchFiltering:
    return BatchFiltering(tenant_id=tenant_id(), group=group_name)


@pytest.fixture
def date_start_filter(tenant_id: TenantId, first_batch: Batch) -> BatchFiltering:
    return BatchFiltering(tenant_id=tenant_id(), date_start=first_batch.created_at)


@pytest.fixture
def date_end_filter(tenant_id: TenantId, first_batch: Batch) -> BatchFiltering:
    return BatchFiltering(tenant_id=tenant_id(), date_end=first_batch.created_at)


@pytest.fixture
def default_sorting() -> BatchSorting:
    return BatchSorting()


@pytest.fixture
def reversed_sorting() -> BatchSorting:
    return BatchSorting(sort_order=BatchSortOrder.DESC)


@pytest.fixture
def name_sorting() -> BatchSorting:
    return BatchSorting(sort_by=BatchSortBy.NAME)


@pytest.fixture
def status_sorting() -> BatchSorting:
    return BatchSorting(sort_by=BatchSortBy.STATUS)


@pytest.fixture
def group_sorting() -> BatchSorting:
    return BatchSorting(sort_by=BatchSortBy.GROUP)


@pytest.fixture
def next_page_pagination() -> Pagination:
    return Pagination(page=1, per_page=5)


@pytest.fixture
def one_record_pagination() -> Pagination:
    return Pagination(page=0, per_page=1)


@pytest.fixture
def default_pagination() -> Pagination:
    return Pagination(page=0, per_page=9999)
