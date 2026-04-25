import logging

from deps_message_flow.commands.consumer import (
    CommandDispatcher,
    CommandHandlersBuilder,
)
from deps_message_flow.events.subscriber import (
    DomainEventDispatcher,
    DomainEventHandlersBuilder,
)
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer

from deps_files_batch.application import (
    ClassifyBatchFileReply,
    DeleteBatchesWithDocuments,
    ImportFilesBatch,
    SaveBatchDocumentsReply,
)
from deps_files_batch.constants import (
    COMMANDS_CHANNEL,
    COMMANDS_QUEUE,
    COMMANDS_REPLIES_CHANNEL,
    DOCUMENT_TYPE_EXCHANGER,
    DOCUMENTS_EXCHANGER,
    EVENTS_QUEUE,
    GROUP_DESTINATION,
)
from deps_files_batch.domain.model import (
    DocumentTypesAdded,
    DocumentTypesRemoved,
    GroupCreated,
    GroupDeleted,
)
from deps_files_batch.messaging import (
    DocumentStateUpdated,
    DocumentTypeAssignedToDocument,
    DocumentTypeCreated,
    DocumentTypeDeleted,
    GetDocumentTypesReply,
    GetGroupsReply,
)

_logger = logging.getLogger(__name__)


def make_message_dispatcher(subscriber: IMessageConsumer, producer: IMessageProducer) -> IMessageConsumer:
    from deps_files_batch.messaging.handlers import (  # noqa: WPS433, WPS235
        classify_batch_file_reply_handler,
        delete_batches_with_documents_handler,
        document_state_updated_handler,
        document_type_assigned_to_document_handler,
        document_type_created_handler,
        document_type_deleted_handler,
        document_types_added_handler,
        document_types_removed_handler,
        get_document_types_reply_handler,
        get_groups_reply_handler,
        group_created_handler,
        group_deleted_handler,
        import_files_batch,
        save_batch_documents_reply_handler,
    )

    events_handlers = (
        DomainEventHandlersBuilder.for_aggregate_type(GROUP_DESTINATION)
        .on_event(GroupCreated, group_created_handler)
        .on_event(GroupDeleted, group_deleted_handler)
        .on_event(DocumentTypesAdded, document_types_added_handler)
        .on_event(DocumentTypesRemoved, document_types_removed_handler)
        .and_for_aggregate_type(DOCUMENT_TYPE_EXCHANGER)
        .on_event(DocumentTypeCreated, document_type_created_handler)
        .on_event(DocumentTypeDeleted, document_type_deleted_handler)
        .and_for_aggregate_type(DOCUMENTS_EXCHANGER)
        .on_event(DocumentStateUpdated, document_state_updated_handler)
        .on_event(DocumentTypeAssignedToDocument, document_type_assigned_to_document_handler)
        .for_queue(EVENTS_QUEUE)
        .build()
    )

    commands_handlers = (
        CommandHandlersBuilder.from_channel(COMMANDS_REPLIES_CHANNEL)
        .on_message(GetGroupsReply, get_groups_reply_handler)
        .on_message(GetDocumentTypesReply, get_document_types_reply_handler)
        .on_message(SaveBatchDocumentsReply, save_batch_documents_reply_handler)
        .on_message(ClassifyBatchFileReply, classify_batch_file_reply_handler)
        .and_from_channel(COMMANDS_CHANNEL)
        .on_message(ImportFilesBatch, import_files_batch)
        .on_message(DeleteBatchesWithDocuments, delete_batches_with_documents_handler)
        .for_queue(COMMANDS_QUEUE)
        .build()
    )

    ded = DomainEventDispatcher(events_handlers, subscriber)
    ded.initialize()

    cd = CommandDispatcher(commands_handlers, subscriber, producer)
    cd.initialize()

    _logger.info("Start consuming....")

    return subscriber
