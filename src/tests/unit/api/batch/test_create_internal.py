import pytest

from deps_files_batch.api import BatchRequestSerializer
from deps_files_batch.constants import INTERNAL_API_PREFIX


@pytest.mark.usefixtures("save_group")
def test_internal_create_batch_from_file__batch_created(
    file_creation_data,
    group_id,
    batch_name,
    client,
):
    file_params = [
        dict(
            name=file_creation_data.name,
            path=file_creation_data.file_path,
            documentTypeId=None,
            processingParams=file_creation_data.processing_params,
        )
    ]
    payload = BatchRequestSerializer(
        name=batch_name,
        group_id=group_id(),
        metadata={},
        files=file_params,
    ).json(by_alias=True)

    response = client.post(f"{INTERNAL_API_PREFIX}/batches/from-file", data=payload)

    assert response.status_code == 201
    response_data = response.json()
    assert "batchId" in response_data
    assert "batchName" in response_data
