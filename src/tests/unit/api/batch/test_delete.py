from random import randint

import pytest

from deps_files_batch.constants import V1_API_PREFIX
from deps_files_batch.domain.model import BatchId, FileId, TenantId


def test_delete__no_batches__204(client, faker):
    params = {"ids": [faker.uuid4() for _ in range(randint(1, 10))]}

    response = client.delete(f"{V1_API_PREFIX}/batches", params=params)

    assert response.status_code == 204


@pytest.mark.usefixtures("save_batches")
def test_delete__batches_exist__deleted(client, batches, fake_unit_of_work):
    params = {"ids": [b.id() for b in batches]}

    response = client.delete(f"{V1_API_PREFIX}/batches", params=params)

    assert response.status_code == 204


def test_delete_with_documents__no_batches__204(client, faker, fake_command_producer):
    params = {"ids": [faker.uuid4() for _ in range(randint(1, 10))]}

    response = client.delete(f"{V1_API_PREFIX}/batches/with-documents", params=params)

    assert response.status_code == 204


@pytest.mark.usefixtures("save_batches")
def test_delete_with_documents__batches_exist__deleted(client, batches, fake_unit_of_work, fake_command_producer):
    params = {"ids": [b.id() for b in batches]}

    response = client.delete(f"{V1_API_PREFIX}/batches/with-documents", params=params)

    assert response.status_code == 204


def test_delete_files__no_batch__not_found(client, batch_id: BatchId, file_id: FileId):
    params = {"ids": [file_id()]}

    response = client.delete(f"{V1_API_PREFIX}/batches/{batch_id()}/files", params=params)

    assert response.status_code == 404


@pytest.mark.usefixtures("save_batch")
def test_delete_files__batch_exists__no_file__not_found(client, batch_id: BatchId):
    params = {"ids": ["nonexistent file id"]}

    response = client.delete(f"{V1_API_PREFIX}/batches/{batch_id()}/files", params=params)

    assert response.status_code == 404


@pytest.mark.usefixtures("save_batch_with_files")
def test_delete_files__batch_file_exist__deleted(
    client,
    batch_id: BatchId,
    file_id: FileId,
    tenant_id: TenantId,
    fake_unit_of_work,
):
    params = {"ids": [file_id()]}

    response = client.delete(f"{V1_API_PREFIX}/batches/{batch_id()}/files", params=params)

    assert response.status_code == 204


def test_delete_files_with_documents__no_batch__not_found(client, batch_id: BatchId, file_id: FileId):
    params = {"ids": [file_id()]}

    response = client.delete(f"{V1_API_PREFIX}/batches/{batch_id()}/files/with-documents", params=params)

    assert response.status_code == 404


@pytest.mark.usefixtures("save_batch")
def test_delete_files_with_documents__batch_exists__no_file__not_found(client, batch_id: BatchId):
    params = {"ids": ["nonexistent file id"]}

    response = client.delete(f"{V1_API_PREFIX}/batches/{batch_id()}/files/with-documents", params=params)

    assert response.status_code == 404


@pytest.mark.usefixtures("save_batch_with_files")
def test_delete_files_with_documents__batch_file_exist__deleted(
    client,
    batch_id: BatchId,
    file_id: FileId,
    tenant_id: TenantId,
    fake_unit_of_work,
):
    params = {"ids": [file_id()]}

    response = client.delete(f"{V1_API_PREFIX}/batches/{batch_id()}/files/with-documents", params=params)

    assert response.status_code == 204
