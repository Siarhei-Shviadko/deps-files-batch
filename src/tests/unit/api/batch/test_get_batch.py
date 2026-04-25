import pytest

from deps_files_batch.constants import V1_API_PREFIX


@pytest.mark.usefixtures("save_aborted_batch")
def test_get_batch__ok(client, batch, file):
    response = client.get(f"{V1_API_PREFIX}/batches/{batch.id()}")

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["id"] == batch.id()
    assert json_response["name"] == batch.name
    assert json_response["status"] == batch.status
    assert json_response["group"]["id"] == batch.group_id()
    assert json_response["createdAt"] == batch.created_at.isoformat()
    [saved_file] = json_response["files"]
    assert saved_file["id"] == file.id()
    assert saved_file["documentId"] == file.document_id
    assert saved_file["documentTypeId"] == file.document_type_id()
    assert saved_file["engine"] == file.processing_params.engine
    assert saved_file["llmType"] == file.processing_params.llm_type
    assert saved_file["parsingFeatures"] == [pf.value for pf in file.processing_params.parsing_features]
    assert saved_file["error"] == {"code": file.error.code, "message": file.error.message}
    assert saved_file["status"] == file.status


def test_get_batch__not_found(client, batch_id):
    response = client.get(f"{V1_API_PREFIX}/batches/{batch_id()}")

    assert response.status_code == 404
