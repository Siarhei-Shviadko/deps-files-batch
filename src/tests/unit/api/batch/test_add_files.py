import pytest

from deps_files_batch.constants import V1_API_PREFIX
from deps_files_batch.domain.model import BatchId, FileCreationData


def test_add_batch_files__no_batch__not_found(
    file_creation_data: FileCreationData,
    batch_id: BatchId,
    file_name,
    client,
):
    payload = {
        "files": [
            {"name": file_name, "path": file_creation_data.file_path, "documentTypeId": None, "processingParams": {}},
        ],
    }

    response = client.post(f"{V1_API_PREFIX}/batches/{batch_id()}/files", json=payload)

    assert response.status_code == 404


@pytest.mark.usefixtures("save_batch", "save_group")
def test_add_batch_files__added(
    file_creation_data: FileCreationData,
    batch_id: BatchId,
    file_name,
    client,
):
    payload = {
        "files": [
            {"name": file_name, "path": file_creation_data.file_path, "documentTypeId": None, "processingParams": {}},
        ],
    }

    response = client.post(f"{V1_API_PREFIX}/batches/{batch_id()}/files", json=payload)

    assert response.status_code == 201


@pytest.mark.usefixtures("save_batch_without_group")
def test_add_batch_files__no_group__no_document_type__error(
    file_creation_data: FileCreationData,
    batch_id,
    file_name,
    client,
):
    payload = {
        "files": [
            {"name": file_name, "path": file_creation_data.file_path, "documentTypeId": None, "processingParams": {}},
        ],
    }

    response = client.post(f"{V1_API_PREFIX}/batches/{batch_id()}/files", json=payload)

    assert response.status_code == 400
