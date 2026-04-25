import pytest
from more_itertools import first, nth

from deps_files_batch.application import (
    BatchService,
    ClassifyBatchFile,
    SaveBatchDocuments,
)
from deps_files_batch.constants import (
    CLASSIFICATION_COMMANDS_CHANNEL,
    DOCUMENT_COMMANDS_CHANNEL,
)
from deps_files_batch.domain.exceptions import (
    GroupDoesntContainDocumentTypes,
    GroupNotFound,
)
from deps_files_batch.domain.model import (
    BatchCreated,
    FileCreationData,
    Group,
    GroupId,
    TenantId,
)
from tests.fakes import FakeCommandProducer, FakeDomainEventPublisher, FakeUnitOfWork


def test_batch_service__create_batch__batch_created(
    fake_unit_of_work: "FakeUnitOfWork",
    batch_service: "BatchService",
    tenant_id: "TenantId",
    file_creation_data: "FileCreationData",
    group: "Group",
    batch_name: str,
    fake_command_producer: "FakeCommandProducer",
    fake_domain_event_publisher: "FakeDomainEventPublisher",
):
    fake_unit_of_work.groups.save(group)
    file_params = [file_creation_data]
    batch = batch_service.create_batch(
        batch_name=batch_name, batch_metadata={}, tenant_id=tenant_id(), group_id=group.id(), file_params=file_params
    )
    assert fake_unit_of_work.batches.batch_of_id(batch_id=batch.id(), tenant_id=batch.tenant_id()) is batch


def test_batch_service__create_batch__command_sent(
    fake_unit_of_work: "FakeUnitOfWork",
    batch_service: "BatchService",
    tenant_id: "TenantId",
    file_creation_data: "FileCreationData",
    group: "Group",
    batch_name: str,
    fake_command_producer: "FakeCommandProducer",
    fake_domain_event_publisher: "FakeDomainEventPublisher",
):
    fake_unit_of_work.groups.save(group)
    file_params = [file_creation_data]
    batch = batch_service.create_batch(
        batch_name=batch_name, batch_metadata={}, tenant_id=tenant_id(), group_id=group.id(), file_params=file_params
    )
    assert (sent_command := first(fake_command_producer.sent))
    assert sent_command.command.batch_id == batch.id(), "Batch ID mismatch"
    assert sent_command.command.group_id == batch.group_id(), "Group ID mismatch"
    assert len(sent_command.command.files) == len(batch.files), "Number of files mismatch"

    for sent_file, original_file in zip(sent_command.command.files, batch.files):
        assert sent_file["id"] == original_file.id(), "File ID mismatch"
        assert sent_file["path"] == original_file.file_path, "File path mismatch"
        assert sent_file["metadata"] == {
            "batch_id": batch.id(),
            "batch_file_id": sent_file["id"],
            **batch.metadata,
        }, "File metadata mismatch"
        if original_file.document_type_id:
            assert sent_file["document_type_id"] == original_file.document_type_id(), "Document type ID mismatch"

        sent_params = sent_file["processing_params"]
        original_params = original_file.processing_params

        assert sent_params["engine"] == original_params.engine, "Processing engine mismatch"
        assert sent_params["language"] == original_params.language, "Processing language mismatch"
        assert sent_params["llm_type"] == original_params.llm_type, "LLM type mismatch"

        if original_params.parsing_features:
            expected_features = sorted(pf.value for pf in original_params.parsing_features)
            assert sent_params["parsing_features"] == expected_features, "Parsing features mismatch"
        else:
            assert sent_params["parsing_features"] == (
                sorted(original_params.parsing_features),
                "Parsing features mismatch",
            )


def test_batch_service__create_batch__event_published(
    fake_unit_of_work: "FakeUnitOfWork",
    batch_service: "BatchService",
    tenant_id: "TenantId",
    file_creation_data: "FileCreationData",
    group: "Group",
    batch_name: str,
    fake_domain_event_publisher: "FakeDomainEventPublisher",
):
    fake_unit_of_work.groups.save(group)
    file_params = [file_creation_data]
    batch = batch_service.create_batch(
        batch_name=batch_name, batch_metadata={}, tenant_id=tenant_id(), group_id=group.id(), file_params=file_params
    )
    assert fake_unit_of_work.batches.batch_of_id(batch.id(), batch.tenant_id()) is batch

    expected_event = BatchCreated(
        id=batch.id(),
        name=batch_name,
        group_id=group.id(),
        files=[file.id() for file in batch.files],
    )
    assert (published_event := first(fake_domain_event_publisher.published))
    assert published_event.events == [expected_event]


@pytest.mark.usefixtures("save_group")
def test_create_batch__group_and_document_type__commands_sent(
    fake_unit_of_work: FakeUnitOfWork,
    batch_service: BatchService,
    tenant_id: TenantId,
    file_creation_data: FileCreationData,
    file_creation_data_without_document_type: FileCreationData,
    group_id: GroupId,
    batch_name: str,
    fake_command_producer: FakeCommandProducer,
    batch_metadata,
):
    batch = batch_service.create_batch(
        batch_name=batch_name,
        batch_metadata=batch_metadata,
        tenant_id=tenant_id(),
        group_id=group_id(),
        file_params=[file_creation_data, file_creation_data_without_document_type],
    )

    assert fake_unit_of_work.batches.batch_of_id(batch.id(), batch.tenant_id()) is batch
    assert (message := first(fake_command_producer.sent))
    assert message.channel == DOCUMENT_COMMANDS_CHANNEL
    assert isinstance(message.command, SaveBatchDocuments)
    assert (message := nth(fake_command_producer.sent, 1))
    assert message.channel == CLASSIFICATION_COMMANDS_CHANNEL
    assert isinstance(message.command, ClassifyBatchFile)


def test_batch_service__create_batch__no_group_found__raised(
    batch_service: "BatchService",
    tenant_id: "TenantId",
    file_creation_data: "FileCreationData",
    faker,
    batch_name: str,
):
    missing_group_id = faker.uuid4()
    with pytest.raises(GroupNotFound):
        batch_service.create_batch(
            batch_name=batch_name,
            batch_metadata={},
            tenant_id=tenant_id(),
            group_id=missing_group_id,
            file_params=[file_creation_data],
        )


def test_batch_service__create_batch__not_all_doc_types_in_the_group__raised(
    fake_unit_of_work: "FakeUnitOfWork",
    batch_service: "BatchService",
    tenant_id: "TenantId",
    file_creation_data: "FileCreationData",
    group: "Group",
    batch_name: str,
    fake_command_producer: "FakeCommandProducer",
    fake_domain_event_publisher: "FakeDomainEventPublisher",
):
    file_creation_data.document_type_id = "wrong document type id"
    fake_unit_of_work.groups.save(group)

    with pytest.raises(GroupDoesntContainDocumentTypes):
        batch_service.create_batch(
            batch_name=batch_name,
            batch_metadata={},
            tenant_id=tenant_id(),
            group_id=group.id(),
            file_params=[file_creation_data],
        )
