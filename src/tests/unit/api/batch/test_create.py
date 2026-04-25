from typing import TYPE_CHECKING

from deps_files_batch.api import BatchRequestSerializer
from deps_files_batch.constants import V1_API_PREFIX
from deps_files_batch.domain.model import DocumentTypeId, FileCreationData

if TYPE_CHECKING:
    from deps_files_batch.domain.model import Group
    from tests.fakes import FakeUnitOfWork


def test__create_batch__group__no_document_types__batch_created(
    fake_unit_of_work: "FakeUnitOfWork",
    file_creation_data: "FileCreationData",
    group: "Group",
    batch_name: str,
    client,
):
    fake_unit_of_work.groups.save(group)
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
        group_id=group.id(),
        metadata={},
        files=file_params,
    ).json(by_alias=True)

    response = client.post(f"{V1_API_PREFIX}/batches", data=payload)
    assert response.status_code == 201
    assert response.json()


def test__create_batch__no_group__no_document_types__error(
    file_creation_data,
    batch_name: str,
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
    payload = {"name": batch_name, "groupId": None, "metadata": {}, "files": file_params}

    response = client.post(f"{V1_API_PREFIX}/batches", json=payload)
    assert response.status_code == 422


def test__create_batch__no_group__document_types__batch_created(
    document_type_id: DocumentTypeId,
    fake_unit_of_work: "FakeUnitOfWork",
    file_creation_data: "FileCreationData",
    group: "Group",
    batch_name: str,
    client,
):
    fake_unit_of_work.groups.save(group)
    file_params = [
        dict(
            name=file_creation_data.name,
            path=file_creation_data.file_path,
            documentTypeId=document_type_id(),
            processingParams=file_creation_data.processing_params,
        )
    ]
    payload = BatchRequestSerializer(
        name=batch_name,
        group_id=None,
        metadata={},
        files=file_params,
    ).json(by_alias=True)

    response = client.post(f"{V1_API_PREFIX}/batches", data=payload)
    assert response.status_code == 201
    assert response.json()


def test_batch_service__create_batch__no_group_found__raised(
    file_creation_data: "FileCreationData",
    faker,
    batch_name: str,
    client,
):
    missing_group_id = faker.uuid4()
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
        group_id=missing_group_id,
        metadata={},
        files=file_params,
    ).json(by_alias=True)
    response = client.post(f"{V1_API_PREFIX}/batches", data=payload)
    assert response.status_code == 404


def test_batch_service__create_batch__not_all_doc_types_in_the_group__raised(
    fake_unit_of_work: "FakeUnitOfWork",
    file_creation_data: "FileCreationData",
    group: "Group",
    batch_name: str,
    client,
):
    fake_unit_of_work.groups.save(group)
    file_params = [
        dict(
            name=file_creation_data.name,
            path=file_creation_data.file_path,
            documentTypeId="wrong_document_type",
            processingParams=file_creation_data.processing_params,
        )
    ]
    payload = BatchRequestSerializer(
        name=batch_name,
        group_id=group.id(),
        metadata={},
        files=file_params,
    ).json(by_alias=True)
    response = client.post(f"{V1_API_PREFIX}/batches", data=payload)
    assert response.status_code == 400
