import pytest

from deps_files_batch.application import GroupService
from deps_files_batch.constants import COMMANDS_CHANNEL, COMMANDS_REPLIES_CHANNEL
from deps_files_batch.domain.exceptions import GroupNotFound
from deps_files_batch.messaging import GetDocumentTypes, GetGroups


def test_delete__no_group__error(group_service, group_id, tenant_id):
    with pytest.raises(GroupNotFound):
        group_service.delete(group_id=group_id(), tenant_id=tenant_id())


def test_obtain_all__command_sent(fake_command_producer, group_service: GroupService):
    group_service.obtain_all()

    [get_group_command, get_doc_types_command] = fake_command_producer.sent
    assert get_group_command.channel == COMMANDS_CHANNEL
    assert get_group_command.command == GetGroups()
    assert get_group_command.reply_to == COMMANDS_REPLIES_CHANNEL

    assert get_doc_types_command.channel == COMMANDS_CHANNEL
    assert get_doc_types_command.command == GetDocumentTypes()
    assert get_doc_types_command.reply_to == COMMANDS_REPLIES_CHANNEL


def test_add_document_types__no_group__error(group_service, group_id, tenant_id):
    with pytest.raises(GroupNotFound):
        group_service.add_document_types(group_id=group_id(), tenant_id=tenant_id(), document_type_ids=[])


def test_remove_document_types__no_group__error(group_service, group_id, tenant_id):
    with pytest.raises(GroupNotFound):
        group_service.remove_document_types(group_id=group_id(), tenant_id=tenant_id(), document_type_ids=[])
