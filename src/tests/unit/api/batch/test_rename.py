from http import HTTPStatus

import pytest

from deps_files_batch.constants import V1_API_PREFIX
from deps_files_batch.domain.model import BatchSortBy, BatchSorting


@pytest.mark.usefixtures("save_batch")
def test_rename_batch(tenant_id, batch_name, batch, set_user, client, faker, fake_unit_of_work):
    response = client.patch(
        f"{V1_API_PREFIX}/batches/{batch.id()}",
        json={
            "name": (new_name := faker.word()),
        },
    )

    assert response.status_code == HTTPStatus.OK
    batch = fake_unit_of_work.batches.batch_of_id(batch_id=batch.id(), tenant_id=tenant_id())
    assert batch.name == new_name
