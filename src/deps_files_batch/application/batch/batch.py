from logging import getLogger
from typing import Any

from deps_message_flow.commands.common import Command
from deps_message_flow.commands.producer import CommandProducer
from deps_message_flow.events.publisher import DomainEventPublisher

from deps_files_batch.constants import (
    CLASSIFICATION_COMMANDS_CHANNEL,
    COMMANDS_REPLIES_CHANNEL,
    DOCUMENT_COMMANDS_CHANNEL,
)
from deps_files_batch.domain.exceptions import (
    BatchNotFound,
    GroupDoesntContainDocumentTypes,
    GroupNotFound,
)
from deps_files_batch.domain.model import Batch, File, FileCreationData, FileId
from deps_files_batch.infrastructure.unit_of_work import AbstractUnitOfWork

from ..retry_transaction import retry_on_transaction_error
from .commands import (
    ClassifyBatchFile,
    DeleteBatchDocument,
    DocumentCreationResult,
    SaveBatchDocuments,
    StartBatchProcessing,
)
from .director import build_batch_with_file_params
from .document_state_caster import DocumentStateCaster

__all__ = ["BatchService"]


class BatchService:  # noqa: WPS214
    AGGREGATE_TYPE = "Batch"

    def __init__(
        self,
        unit_of_work: AbstractUnitOfWork,
        command_producer: CommandProducer,
        domain_event_publisher: DomainEventPublisher,
    ) -> None:
        self._uow = unit_of_work
        self._command_producer = command_producer
        self._domain_event_publisher = domain_event_publisher

        self._document_state_caster = DocumentStateCaster()

        self._logger = getLogger(self.__class__.__name__)

    @retry_on_transaction_error()
    def create_batch(
        self,
        batch_name: str,
        group_id: str | None,
        file_params: list[FileCreationData],
        tenant_id: str,
        batch_metadata: dict[str, Any] | None = None,
    ) -> Batch:
        with self._uow:
            if group_id:
                self._validate_group(file_params, group_id, tenant_id)

            batch = build_batch_with_file_params(
                batch_metadata=batch_metadata,
                batch_name=batch_name,
                file_params=file_params,
                group_id=group_id,
                tenant_id=tenant_id,
            )
            self._save_batch(batch)

        if files := batch.files_with_document_type:
            self._send_command(
                channel=DOCUMENT_COMMANDS_CHANNEL,
                command=SaveBatchDocuments.for_files(batch=batch, files=files),
                reply_to=COMMANDS_REPLIES_CHANNEL,
            )

        for file in batch.files_without_document_type:
            self._send_command(
                channel=CLASSIFICATION_COMMANDS_CHANNEL,
                command=ClassifyBatchFile.for_file(batch=batch, file=file),
                reply_to=COMMANDS_REPLIES_CHANNEL,
            )

        return batch

    @retry_on_transaction_error()
    def add_documents_creation_result(
        self,
        batch_id: str,
        tenant_id: str,
        documents_creation_result: list[DocumentCreationResult],
    ) -> None:
        document_ids_to_process = []

        with self._uow:
            batch = self._find_batch(batch_id=batch_id, tenant_id=tenant_id)

            for result in documents_creation_result:
                file_id = result["id"]
                document_id = result["document_id"]
                if document_id is not None:
                    batch.add_document_id(file_id=file_id, document_id=document_id)
                    document_ids_to_process.append(document_id)
                elif result["error"] is not None:
                    batch.add_document_creation_error(file_id=file_id)

            self._save_batch(batch)

        if document_ids_to_process:
            self._send_command(
                channel=DOCUMENT_COMMANDS_CHANNEL,
                command=StartBatchProcessing(document_ids_to_process),
                reply_to=COMMANDS_REPLIES_CHANNEL,
            )

    @retry_on_transaction_error()
    def add_file_classification_result(
        self,
        batch_id: str,
        tenant_id: str,
        file_id: str,
        document_id: str | None,
        document_type_id: str | None,
    ) -> None:
        with self._uow:
            batch = self._find_batch(batch_id=batch_id, tenant_id=tenant_id)

            if document_id is not None and document_type_id is not None:
                batch.add_classification_result(
                    file_id=file_id,
                    document_id=document_id,
                    document_type_id=document_type_id,
                )
            else:
                batch.add_document_creation_error(file_id=file_id)

            self._save_batch(batch)

        if document_id is not None:
            self._send_command(
                channel=DOCUMENT_COMMANDS_CHANNEL,
                command=StartBatchProcessing([document_id]),
                reply_to=COMMANDS_REPLIES_CHANNEL,
            )

    @retry_on_transaction_error()
    def update_file_status(
        self,
        batch_id: str,
        tenant_id: str,
        file_id: str,
        document_state: str,
        error_in_state: str | None = None,
    ) -> None:
        with self._uow:
            batch = self._find_batch(batch_id=batch_id, tenant_id=tenant_id)
            file_status = self._document_state_caster.cast_into_file_status(document_state)

            if batch.file_has_different_status(file_id=file_id, file_status=file_status):
                batch.update_file_status(file_id=file_id, file_status=file_status, error_in_state=error_in_state)
                self._save_batch(batch)

    @retry_on_transaction_error()
    def assign_document_type_to_file(self, batch_id: str, tenant_id: str, file_id: str, document_type_id: str) -> None:
        with self._uow:
            batch = self._find_batch(batch_id=batch_id, tenant_id=tenant_id)

            batch.assign_document_type_to_file(file_id=file_id, document_type_id=document_type_id)
            self._save_batch(batch)

    @retry_on_transaction_error()
    def delete_batches(self, ids: set[str], tenant_id: str) -> None:
        with self._uow:
            self._delete_batches(ids=ids, tenant_id=tenant_id)

    @retry_on_transaction_error()
    def delete_batches_with_documents(self, ids: set[str], tenant_id: str) -> None:
        with self._uow:
            deleted_batches = self._delete_batches(ids=ids, tenant_id=tenant_id)

        for batch in deleted_batches:
            if document_ids := batch.document_ids:
                for document_id in document_ids:
                    self._send_command(
                        channel=DOCUMENT_COMMANDS_CHANNEL,
                        command=DeleteBatchDocument(document_id),
                        reply_to=COMMANDS_REPLIES_CHANNEL,
                    )

    @retry_on_transaction_error()
    def delete_files(self, batch_id: str, file_ids: list[str], tenant_id: str) -> None:
        with self._uow:
            self._delete_files(batch_id=batch_id, file_ids=file_ids, tenant_id=tenant_id)

    @retry_on_transaction_error()
    def delete_files_with_documents(self, batch_id: str, file_ids: list[str], tenant_id: str) -> None:
        with self._uow:
            deleted_files = self._delete_files(batch_id=batch_id, file_ids=file_ids, tenant_id=tenant_id)

        for file in deleted_files:
            if document_id := file.document_id:
                self._send_command(
                    channel=DOCUMENT_COMMANDS_CHANNEL,
                    command=DeleteBatchDocument(document_id()),
                    reply_to=COMMANDS_REPLIES_CHANNEL,
                )

    @retry_on_transaction_error()
    def add_files(self, batch_id: str, tenant_id: str, file_params: list[FileCreationData]) -> None:
        with self._uow:
            batch = self._find_batch(batch_id=batch_id, tenant_id=tenant_id)

            if group_id := batch.group_id:
                self._validate_group(file_params=file_params, group_id=group_id(), tenant_id=tenant_id)

            new_file_ids: list[FileId] = []
            for file_param in file_params:
                file = batch.add_file(
                    file_name=file_param.name,
                    file_path=file_param.file_path,
                    processing_params=file_param.processing_params,
                    document_type_id=file_param.document_type_id,
                )
                new_file_ids.append(file.id)

            self._save_batch(batch)

        if files_to_create_documents := [f for f in batch.files_with_document_type if f.id in new_file_ids]:
            self._send_command(
                channel=DOCUMENT_COMMANDS_CHANNEL,
                command=SaveBatchDocuments.for_files(batch=batch, files=files_to_create_documents),
                reply_to=COMMANDS_REPLIES_CHANNEL,
            )
        for file_to_classify in (f for f in batch.files_without_document_type if f.id in new_file_ids):
            self._send_command(
                channel=CLASSIFICATION_COMMANDS_CHANNEL,
                command=ClassifyBatchFile.for_file(batch=batch, file=file_to_classify),
                reply_to=COMMANDS_REPLIES_CHANNEL,
            )

    def rename_batch(self, batch_id: str, tenant_id: str, new_name: str) -> None:
        with self._uow:
            batch = self._find_batch(batch_id=batch_id, tenant_id=tenant_id)
            batch.rename(new_name)
            self._save_batch(batch)

    def _save_batch(self, batch: Batch) -> None:
        self._uow.batches.save(batch)
        self._uow.commit()

        self._domain_event_publisher.publish(
            aggregate_type=self.AGGREGATE_TYPE,
            aggregate_id=batch.id(),
            domain_events=batch.events,
        )

    def _validate_group(self, file_params: list[FileCreationData], group_id: str, tenant_id: str) -> None:
        group = self._uow.groups.group_of_id(group_id=group_id, tenant_id=tenant_id)
        if not group:
            raise GroupNotFound(group_id=group_id)
        if not group.contains_document_types((fp.document_type_id for fp in file_params)):
            raise GroupDoesntContainDocumentTypes(group_id=group_id)

    def _find_batch(self, batch_id: str, tenant_id: str) -> Batch:
        if batch := self._uow.batches.batch_of_id(batch_id=batch_id, tenant_id=tenant_id):
            return batch

        raise BatchNotFound(batch_id)

    def _send_command(self, channel: str, command: Command, reply_to: str) -> None:
        self._command_producer.send(channel=channel, command=command, reply_to=reply_to)

    def _delete_batches(self, ids: set[str], tenant_id: str) -> list[Batch]:
        batches = self._uow.batches.batches_of_ids(ids=ids, tenant_id=tenant_id)

        if batches:
            self._uow.batches.delete_all(batches)
            self._uow.commit()

        return batches

    def _delete_files(self, batch_id: str, file_ids: list[str], tenant_id: str) -> list[File]:
        batch = self._find_batch(batch_id=batch_id, tenant_id=tenant_id)
        deleted_files = [batch.delete_file(file_id) for file_id in file_ids]
        self._save_batch(batch)

        return deleted_files
