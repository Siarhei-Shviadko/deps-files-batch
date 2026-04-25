import pytest
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)

from deps_files_batch.messaging.events import DocumentTypeCreated, DocumentTypeDeleted


@pytest.fixture
def document_type_name(faker):
    return faker.word()


@pytest.fixture
def save_document_type(document_type_id, fake_unit_of_work):
    fake_unit_of_work.groups.save_document_types([document_type_id()])
    return document_type_id


@pytest.fixture
def document_type_created_dee(mocker, document_type_id, tenant_id, document_type_name):
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event = DocumentTypeCreated(
        document_type=document_type_id(),
        tenant=tenant_id(),
        name=document_type_name,
    )
    return dee


@pytest.fixture
def document_type_deleted_dee(mocker, document_type_id, tenant_id):
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event = DocumentTypeDeleted(
        document_type=document_type_id(),
        tenant=tenant_id(),
    )
    return dee
