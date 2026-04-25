import logging

from dependency_injector.wiring import Provide, inject
from deps_message_flow.commands.common import (
    CommandMessageHeaders,
    CommandReplyOutcome,
    ReplyMessageHeaders,
    make_message_for_command,
)
from deps_message_flow.commands.consumer import CommandHandlerReplyBuilder
from deps_message_flow.commands.consumer.command_message import CommandMessage
from deps_message_flow.events.mappers import JsonMapper
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)
from deps_message_flow.messaging.common import IMessage

from deps_files_batch.application import (
    BatchService,
    ClassifyBatchFileReply,
    DeleteBatchesWithDocuments,
    DocumentCreationResult,
    GroupService,
    ImportFilesBatch,
    ImportFilesBatchReply,
    SaveBatchDocumentsReply,
)
from deps_files_batch.constants import METADATA_BATCH_FILE_ID_KEY, METADATA_BATCH_ID_KEY
from deps_files_batch.containers import Containers
from deps_files_batch.domain.exceptions.base import BusinessException
from deps_files_batch.domain.model import ErrorInfo
from deps_files_batch.messaging import (
    DocumentStateUpdated,
    DocumentTypeAssignedToDocument,
    GetDocumentTypesReply,
)

logger = logging.getLogger(__name__)


def is_command_successful(command_message: CommandMessage) -> bool:
    return (
        command_message.message.get_required_header(ReplyMessageHeaders.REPLY_OUTCOME)
        == CommandReplyOutcome.SUCCESS.name
    )


@inject
def get_groups_reply_handler(  # noqa: WPS463
    command_message: CommandMessage,
    group_service: GroupService = Provide[Containers.group_service],
):
    if is_command_successful(command_message):
        group_service.save_all(command_message.command.groups)
    else:
        logger.error(f"Failed to get groups. Command headers: {command_message.message.headers}")


@inject
def get_document_types_reply_handler(  # noqa: WPS463
    command_message: CommandMessage["GetDocumentTypesReply"],
    group_service: GroupService = Provide[Containers.group_service],
):
    if is_command_successful(command_message):
        document_type_ids = [dt["document_type"] for dt in command_message.command.document_types]
        group_service.save_document_types(document_type_ids)
    else:
        logger.error(f"Failed to get groups. Command headers: {command_message.message.headers}")


@inject
def group_created_handler(
    dee: DomainEventEnvelope,
    group_service: GroupService = Provide[Containers.group_service],
):
    group_service.create(
        group_id=dee.event.id,
        tenant_id=dee.event.tenant_id,
        document_type_ids=dee.event.document_type_ids,
        name=dee.event.name,
    )


@inject
def group_deleted_handler(
    dee: DomainEventEnvelope,
    group_service: GroupService = Provide[Containers.group_service],
):
    group_service.delete(group_id=dee.event.id, tenant_id=dee.event.tenant_id)


@inject
def document_types_added_handler(
    dee: DomainEventEnvelope,
    group_service: GroupService = Provide[Containers.group_service],
):
    group_service.add_document_types(
        group_id=dee.event.id,
        tenant_id=dee.event.tenant_id,
        document_type_ids=dee.event.document_type_ids,
    )


@inject
def document_types_removed_handler(
    dee: DomainEventEnvelope,
    group_service: GroupService = Provide[Containers.group_service],
):
    group_service.remove_document_types(
        group_id=dee.event.id,
        tenant_id=dee.event.tenant_id,
        document_type_ids=dee.event.document_type_ids,
    )


@inject
def save_batch_documents_reply_handler(
    command_message: CommandMessage[SaveBatchDocumentsReply],
    tenant_id: str = Provide[Containers.current_user_tenant],
    batch_service: BatchService = Provide[Containers.batch_service],
):
    try:
        command = command_message.command
        batch_service.add_documents_creation_result(
            batch_id=command.batch_id,
            tenant_id=tenant_id,
            documents_creation_result=command.files,
        )
    except BusinessException as err:
        logger.error(f"Failed to add documents creation result. Error: {err}")


@inject
def classify_batch_file_reply_handler(
    command_message: CommandMessage[ClassifyBatchFileReply],
    tenant_id: str = Provide[Containers.current_user_tenant],
    batch_service: BatchService = Provide[Containers.batch_service],
):
    try:
        command = command_message.command
        batch_service.add_file_classification_result(
            batch_id=command.batch_id,
            tenant_id=tenant_id,
            file_id=command.file_id,
            document_id=command.document_id,
            document_type_id=command.document_type_id,
        )
    except BusinessException as err:
        logger.error(f"Failed to add documents creation result. Error: {err}")


@inject
def document_state_updated_handler(
    dee: DomainEventEnvelope[DocumentStateUpdated],
    tenant_id: str = Provide[Containers.current_user_tenant],
    batch_service: BatchService = Provide[Containers.batch_service],
):
    event = dee.event
    batch_id = event.metadata.get(METADATA_BATCH_ID_KEY)
    file_id = event.metadata.get(METADATA_BATCH_FILE_ID_KEY)

    if batch_id is not None and file_id is not None:
        try:
            batch_service.update_file_status(
                batch_id=batch_id,
                tenant_id=tenant_id,
                file_id=file_id,
                document_state=event.state,
                error_in_state=event.error_in_state,
            )
        except BusinessException as err:
            logger.error(f"Failed to update file status. Error: {err}")


@inject
def document_type_assigned_to_document_handler(
    dee: DomainEventEnvelope[DocumentTypeAssignedToDocument],
    tenant_id: str = Provide[Containers.current_user_tenant],
    batch_service: BatchService = Provide[Containers.batch_service],
):
    event = dee.event
    batch_id = event.metadata.get("batch_id")
    file_id = event.metadata.get("batch_file_id")

    if batch_id is not None and file_id is not None:
        try:
            batch_service.assign_document_type_to_file(
                batch_id=batch_id,
                tenant_id=tenant_id,
                file_id=file_id,
                document_type_id=event.document_type_id,
            )
        except BusinessException as err:
            logger.error(f"Failed to assign document type to file. Error: {err}")


@inject
def import_files_batch(
    command_message: CommandMessage[ImportFilesBatch],
    tenant_id: str = Provide[Containers.current_user_tenant],
    batch_service: BatchService = Provide[Containers.batch_service],
) -> list[IMessage]:
    is_importing_success = False

    try:
        command = command_message.command
        command.validate()

        batch = batch_service.create_batch(
            batch_name=command.name,
            group_id=command.group_id,
            file_params=command.file_params,
            tenant_id=tenant_id,
            batch_metadata=command.metadata,
        )
        reply = ImportFilesBatchReply(batch.id())
        is_importing_success = True

    except Exception as err:
        logger.error(f"Failed to create batch. Error: {err}")
        reply = ImportFilesBatchReply()

    reply_message = make_message_for_command(
        command_message.message.headers.get(CommandMessageHeaders.REPLY_TO),
        JsonMapper().serialize(reply),
        reply.__class__.__name__,
        "NONE",
    )

    if is_importing_success:
        return [CommandHandlerReplyBuilder.with_success(reply_message)]

    return [CommandHandlerReplyBuilder.with_failure(reply_message)]


@inject
def delete_batches_with_documents_handler(
    command_message: CommandMessage[DeleteBatchesWithDocuments],
    tenant_id: str = Provide[Containers.current_user_tenant],
    batch_service: BatchService = Provide[Containers.batch_service],
):
    batch_service.delete_batches_with_documents(tenant_id=tenant_id, ids=set(command_message.command.batch_ids))


@inject
def document_type_created_handler(
    dee: DomainEventEnvelope,
    group_service: GroupService = Provide[Containers.group_service],
):
    group_service.save_document_types([dee.event.document_type])


@inject
def document_type_deleted_handler(
    dee: DomainEventEnvelope,
    group_service: GroupService = Provide[Containers.group_service],
):
    group_service.delete_document_type(dee.event.document_type)
