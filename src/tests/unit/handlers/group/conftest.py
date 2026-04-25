from uuid import uuid4

import pytest
from deps_message_flow.commands.common import CommandReplyOutcome
from deps_message_flow.commands.consumer import CommandMessage
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)

from deps_files_batch.domain.model import (
    DocumentTypesAdded,
    DocumentTypesRemoved,
    GroupCreated,
    GroupDeleted,
    GroupInfo,
)
from deps_files_batch.messaging import GetGroupsReply


@pytest.fixture
def document_type_ids(group):
    return [dt() for dt in group.document_types]


@pytest.fixture
def document_type_ids_to_add():
    return [uuid4().hex for _ in range(3)]


@pytest.fixture
def get_groups_success_reply(mocker, document_type_ids, group_id, tenant_id, group_name):
    command_message = mocker.Mock(CommandMessage)
    command_message.message.get_required_header.return_value = CommandReplyOutcome.SUCCESS.value
    command_message.command = GetGroupsReply(
        groups=[GroupInfo(id=group_id(), tenant_id=tenant_id(), document_type_ids=document_type_ids, name=group_name)],
    )

    return command_message


@pytest.fixture
def get_groups_failure_reply(mocker, group, document_type_ids):
    command_message = mocker.Mock(CommandMessage)
    command_message.message.get_required_header.return_value = CommandReplyOutcome.FAILURE.value

    return command_message


@pytest.fixture
def group_created_dee(mocker, group, document_type_ids):
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event = GroupCreated(
        id=group.id(), tenant_id=group.tenant_id(), name=group.name, document_type_ids=document_type_ids
    )

    return dee


@pytest.fixture
def group_deleted_dee(mocker, group_id, tenant_id):
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event = GroupDeleted(id=group_id(), tenant_id=tenant_id())

    return dee


@pytest.fixture
def document_types_added_dee(mocker, group_id, tenant_id, document_type_ids_to_add):
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event = DocumentTypesAdded(id=group_id(), tenant_id=tenant_id(), document_type_ids=document_type_ids_to_add)

    return dee


@pytest.fixture
def document_types_removed_dee(mocker, group_id, tenant_id, document_type_ids):
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event = DocumentTypesRemoved(id=group_id(), tenant_id=tenant_id(), document_type_ids=document_type_ids)

    return dee
