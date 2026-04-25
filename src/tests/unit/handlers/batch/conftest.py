import pytest
from deps_message_flow.commands.consumer import CommandMessage
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)
from faker.proxy import Faker

from deps_files_batch.application import (
    ClassifyBatchFileReply,
    DeleteBatchesWithDocuments,
    DocumentCreationResult,
    ImportFilesBatch,
    SaveBatchDocumentsReply,
)
from deps_files_batch.domain.model import DocumentId, DocumentState, ErrorInfo
from deps_files_batch.messaging import (
    DocumentStateUpdated,
    DocumentTypeAssignedToDocument,
)


@pytest.fixture
def document_id() -> DocumentId:
    return DocumentId()


@pytest.fixture
def new_document_state() -> DocumentState:
    return DocumentState.UNIFICATION


@pytest.fixture
def document_metadata(batch_id, file_id):
    return {"batch_id": batch_id(), "batch_file_id": file_id()}


@pytest.fixture
def document_metadata_without_document_type(batch_id_without_document, file_id_without_document_type):
    return {"batch_id": batch_id_without_document(), "batch_file_id": file_id_without_document_type()}


@pytest.fixture
def error_message(faker: Faker) -> str:
    return faker.text(max_nb_chars=50)


@pytest.fixture
def error_code(faker: Faker) -> str:
    return faker.text(max_nb_chars=15)


@pytest.fixture
def error_info(error_message, error_code) -> ErrorInfo:
    return ErrorInfo(message=error_message, code=error_code)


@pytest.fixture
def save_batch_documents_success_reply(mocker, batch, file, document_id):
    command_message = mocker.Mock(CommandMessage)
    command_message.command = SaveBatchDocumentsReply(
        batch_id=batch.id(),
        files=[DocumentCreationResult(id=file.id(), document_id=document_id(), error=None)],
    )

    return command_message


@pytest.fixture
def save_batch_documents_error_reply(mocker, batch, file, error_info):
    command_message = mocker.Mock(CommandMessage)
    command_message.command = SaveBatchDocumentsReply(
        batch_id=batch.id(),
        files=[DocumentCreationResult(id=file.id(), document_id=None, error=error_info)],
    )

    return command_message


@pytest.fixture
def document_state_updated_dee(mocker, document_id, new_document_state, document_metadata):
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event = DocumentStateUpdated(
        document_id=document_id(),
        state=new_document_state.value,
        metadata=document_metadata,
    )

    return dee


@pytest.fixture
def document_state_updated_dee_with_empty_metadata(mocker, document_id, new_document_state):
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event = DocumentStateUpdated(document_id=document_id(), state=new_document_state.value, metadata={})

    return dee


@pytest.fixture
def document_type_assigned_to_document_dee(
    mocker, document_id, document_type_id, document_metadata_without_document_type
):
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event = DocumentTypeAssignedToDocument(
        document_id=document_id(),
        document_type_id=document_type_id(),
        metadata=document_metadata_without_document_type,
    )

    return dee


@pytest.fixture
def document_type_assigned_to_document_dee_with_empty_metadata(mocker, document_id, document_type_id):
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event = DocumentTypeAssignedToDocument(
        document_id=document_id(), document_type_id=document_type_id, metadata={}
    )

    return dee


@pytest.fixture
def import_files_batch_command_message(mocker, batch_name, group_id, file_creation_data_dict, batch_metadata):
    command_message = mocker.Mock(CommandMessage)
    command_message.command = ImportFilesBatch(
        name=batch_name,
        group_id=group_id(),
        file_params=[file_creation_data_dict],
        metadata=batch_metadata,
    )

    return command_message


@pytest.fixture
def delete_batches_with_documents_command_message(mocker, batch_id):
    command_message = mocker.Mock(CommandMessage)
    command_message.command = DeleteBatchesWithDocuments(batch_ids=[batch_id()])

    return command_message


@pytest.fixture
def classify_batch_file_reply_success(mocker, batch, file, document_id, document_type_id):
    command_message = mocker.Mock(CommandMessage)
    command_message.command = ClassifyBatchFileReply(
        batch_id=batch.id(),
        file_id=file.id(),
        document_id=document_id(),
        document_type_id=document_type_id(),
        error_type=None,
        error_message=None,
    )

    return command_message


@pytest.fixture
def classify_batch_file_reply_error(mocker, batch, file, error_message, error_code):
    command_message = mocker.Mock(CommandMessage)
    command_message.command = ClassifyBatchFileReply(
        batch_id=batch.id(),
        file_id=file.id(),
        document_id=None,
        document_type_id=None,
        error_type=error_code,
        error_message=error_message,
    )

    return command_message
