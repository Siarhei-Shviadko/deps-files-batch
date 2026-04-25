import pytest
from more_itertools import last

from deps_files_batch.application import (
    BatchService,
    ClassifyBatchFile,
    FileData,
    SaveBatchDocuments,
)
from deps_files_batch.constants import (
    CLASSIFICATION_COMMANDS_CHANNEL,
    COMMANDS_REPLIES_CHANNEL,
    DOCUMENT_COMMANDS_CHANNEL,
    METADATA_BATCH_FILE_ID_KEY,
    METADATA_BATCH_ID_KEY,
)
from deps_files_batch.domain.exceptions import GroupDoesntContainDocumentTypes
from deps_files_batch.domain.model import BatchStatus, FileStatus


@pytest.mark.usefixtures("save_batch_without_group")
def test_add_files__batch_without_group__document_type_not_validated__added(
    batch_service: BatchService,
    fake_unit_of_work,
    file_creation_data,
    tenant_id,
    batch_id,
):
    batch_service.add_files(batch_id=batch_id(), tenant_id=tenant_id(), file_params=[file_creation_data])

    new_file = last(fake_unit_of_work.batches.batch_of_id(batch_id=batch_id(), tenant_id=tenant_id()).files)
    assert new_file.file_path == file_creation_data.file_path
    assert new_file.document_type_id() == file_creation_data.document_type_id
    assert new_file.processing_params.engine == file_creation_data.processing_params["engine"]
    assert new_file.processing_params.language == file_creation_data.processing_params["language"]
    assert new_file.processing_params.llm_type == file_creation_data.processing_params["llm_type"]
    assert sorted(new_file.processing_params.parsing_features) == sorted(
        file_creation_data.processing_params["parsing_features"]
    )


@pytest.mark.usefixtures("save_batch", "save_group")
def test_add_files__batch_with_group__wrong_document_type__error(
    batch_service: BatchService,
    file_creation_data,
    tenant_id,
    batch_id,
):
    file_creation_data.document_type_id = "wrong document type id"

    with pytest.raises(GroupDoesntContainDocumentTypes):
        batch_service.add_files(batch_id=batch_id(), tenant_id=tenant_id(), file_params=[file_creation_data])


@pytest.mark.usefixtures("save_batch", "save_group")
def test_add_files__document_type__save_batch_documents_sent(
    batch_service: BatchService,
    fake_command_producer,
    processing_params,
    fake_unit_of_work,
    file_creation_data,
    batch_metadata,
    tenant_id,
    batch_id,
    group_id,
):
    batch_service.add_files(batch_id=batch_id(), tenant_id=tenant_id(), file_params=[file_creation_data])

    [sent_command] = fake_command_producer.sent
    new_file = last(fake_unit_of_work.batches.batch_of_id(batch_id=batch_id(), tenant_id=tenant_id()).files)
    assert sent_command.channel == DOCUMENT_COMMANDS_CHANNEL
    assert sent_command.reply_to == COMMANDS_REPLIES_CHANNEL
    assert sent_command.command == SaveBatchDocuments(
        batch_id=batch_id(),
        group_id=group_id(),
        files=[
            FileData(
                id=new_file.id(),
                name=new_file.name,
                path=file_creation_data.file_path,
                document_type_id=file_creation_data.document_type_id,
                metadata={"batch_file_id": new_file.id(), "batch_id": batch_id()} | batch_metadata,
                processing_params={
                    "engine": processing_params["engine"],
                    "language": processing_params["language"],
                    "llm_type": processing_params["llm_type"],
                    "parsing_features": sorted(pf.value for pf in processing_params["parsing_features"]),
                },
            ),
        ],
    )


@pytest.mark.usefixtures("save_batch", "save_group")
def test_add_files__no_document_type__classify_batch_file_sent(
    batch_service: BatchService,
    fake_command_producer,
    processing_params,
    fake_unit_of_work,
    file_creation_data_without_document_type,
    batch_metadata,
    tenant_id,
    batch_id,
    group_id,
):
    batch_service.add_files(
        batch_id=batch_id(),
        tenant_id=tenant_id(),
        file_params=[file_creation_data_without_document_type],
    )

    [sent_command] = fake_command_producer.sent
    new_file = last(fake_unit_of_work.batches.batch_of_id(batch_id=batch_id(), tenant_id=tenant_id()).files)
    assert sent_command.channel == CLASSIFICATION_COMMANDS_CHANNEL
    assert sent_command.reply_to == COMMANDS_REPLIES_CHANNEL
    assert sent_command.command == ClassifyBatchFile(
        batch_id=batch_id(),
        file_id=new_file.id(),
        file_name=new_file.name,
        file_path=new_file.file_path,
        group_id=group_id(),
        engine=processing_params["engine"],
        language=processing_params["language"],
        parsing_features=sorted(pf.value for pf in processing_params["parsing_features"]),
        llm_type=processing_params["llm_type"],
        needs_unifier=True,
        needs_extraction=True,
        assigned_to_me=False,
        metadata={METADATA_BATCH_ID_KEY: batch_id(), METADATA_BATCH_FILE_ID_KEY: new_file.id(), **batch_metadata},
        start_processing=False,
    )


@pytest.mark.usefixtures("save_completed_batch", "save_group")
def test_add_files__statuses_changed(
    batch_service: BatchService,
    completed_batch,
    fake_unit_of_work,
    file_creation_data,
    tenant_id,
    batch_id,
):
    batch_service.add_files(batch_id=batch_id(), tenant_id=tenant_id(), file_params=[file_creation_data])

    new_file = last(fake_unit_of_work.batches.batch_of_id(batch_id=batch_id(), tenant_id=tenant_id()).files)
    assert new_file.status == FileStatus.NEW
    assert completed_batch.status == BatchStatus.PROCESSING
