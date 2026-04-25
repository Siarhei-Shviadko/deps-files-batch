import pytest

from deps_files_batch.messaging.handlers import (
    document_types_added_handler,
    document_types_removed_handler,
    get_groups_reply_handler,
    group_created_handler,
    group_deleted_handler,
)


def test_get_groups_reply__success__saved(
    get_groups_success_reply,
    fake_unit_of_work,
    document_type_ids,
    group_id,
    tenant_id,
):
    get_groups_reply_handler(get_groups_success_reply)

    result_group = fake_unit_of_work.groups.group_of_id(group_id=group_id(), tenant_id=tenant_id())
    assert result_group.id == group_id
    assert result_group.tenant_id == tenant_id
    assert [dt() for dt in result_group.document_types] == document_type_ids


def test_get_groups_reply__failure__no_error(get_groups_failure_reply):
    get_groups_reply_handler(get_groups_failure_reply)


def test_group_created__created(group_created_dee, fake_unit_of_work, group_id, tenant_id, document_type_ids):
    group_created_handler(group_created_dee)

    result_group = fake_unit_of_work.groups.group_of_id(group_id=group_id(), tenant_id=tenant_id())
    assert result_group.id == group_id
    assert result_group.tenant_id == tenant_id
    assert [dt() for dt in result_group.document_types] == document_type_ids


@pytest.mark.usefixtures("save_group")
def test_group_deleted__deleted(group_deleted_dee, fake_unit_of_work, group):
    group_deleted_handler(group_deleted_dee)

    assert not fake_unit_of_work.groups.group_of_id(group_id=group.id(), tenant_id=group.tenant_id())


@pytest.mark.usefixtures("save_group")
def test_document_types_added_handler__added(
    document_type_ids_to_add,
    document_types_added_dee,
    fake_unit_of_work,
    document_type_ids,
    group,
):
    document_types_added_handler(document_types_added_dee)

    result_group = fake_unit_of_work.groups.group_of_id(group_id=group.id(), tenant_id=group.tenant_id())
    assert [dt() for dt in result_group.document_types] == document_type_ids + document_type_ids_to_add


@pytest.mark.usefixtures("save_group")
def test_document_types_removed_handler__deleted(
    document_types_removed_dee,
    fake_unit_of_work,
    document_type_ids,
    group,
):
    document_types_removed_handler(document_types_removed_dee)

    result_group = fake_unit_of_work.groups.group_of_id(group_id=group.id(), tenant_id=group.tenant_id())
    assert result_group.document_types == []
