from http import HTTPStatus

import pytest

from deps_files_batch.constants import V1_API_PREFIX
from deps_files_batch.domain.model import BatchSortBy, BatchSorting


@pytest.mark.usefixtures("save_batches")
def test_find_batches(tenant_id, batch_name, batches, set_user, client):
    page = 0
    per_page = 3

    response = client.get(
        f"{V1_API_PREFIX}/batches",
        params={
            "name": batch_name,
            "page": page,
            "perPage": per_page,
            "sortBy": BatchSortBy.CREATED_AT.value,
            "sortOrder": BatchSorting.sort_order.value,
        },
    )

    assert response.status_code == HTTPStatus.OK

    json_response = response.json()

    expected_batches_without_pagination = [batch for batch in batches if batch.name == batch_name]
    expected_batches = expected_batches_without_pagination[page * per_page : page * per_page + per_page]

    assert len(json_response["result"]) == len(expected_batches) == json_response["meta"]["size"]

    for batch, expected_batch in zip(json_response["result"], expected_batches):
        assert batch["id"] == expected_batch.id()

    assert json_response["meta"]["total"] == len(expected_batches_without_pagination)


@pytest.mark.usefixtures("save_batch_with_source_file_id")
def test_find_batches__with_source_file_id__source_file_id_in_response(client, batch_with_source_file_id):
    response = client.get(f"{V1_API_PREFIX}/batches")

    assert response.status_code == HTTPStatus.OK
    [batch] = response.json()["result"]
    assert batch["sourceFileId"] == batch_with_source_file_id.source_file_id
