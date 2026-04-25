from uuid import uuid4

import pytest

from deps_files_batch.domain.model import GroupFactory


@pytest.mark.usefixtures("add_groups")
def test_group_of_id__success(unit_of_work, group):
    assert unit_of_work.groups.group_of_id(group.id(), group.tenant_id()) == group


def test_group_of_id__not_found(unit_of_work, tenant_id):
    assert unit_of_work.groups.group_of_id(uuid4().hex, tenant_id()) is None


def test_save_all__success(unit_of_work, group):
    new_group = GroupFactory.create(
        id_=uuid4().hex,
        tenant_id=group.tenant_id(),
        name=group.name,
        document_types=[uuid4().hex for _ in range(3)],
    )

    unit_of_work.groups.save_all([group, new_group])

    assert unit_of_work.groups.group_of_id(group.id(), group.tenant_id()) == group
    assert unit_of_work.groups.group_of_id(new_group.id(), new_group.tenant_id()) == new_group


def test_save_all__empty_list(unit_of_work):
    unit_of_work.groups.save_all([])


@pytest.mark.usefixtures("add_groups")
def test_save_all__update_existing_group(unit_of_work, group):
    updated_group = GroupFactory.create(
        id_=group.id(),
        tenant_id=group.tenant_id(),
        name=group.name,
        document_types=[uuid4().hex for _ in range(3)],
    )

    unit_of_work.groups.save_all([updated_group])

    assert unit_of_work.groups.group_of_id(group.id(), group.tenant_id()) == updated_group


def test_save__success(unit_of_work, group):
    unit_of_work.groups.save(group)

    assert unit_of_work.groups.group_of_id(group.id(), group.tenant_id()) == group


@pytest.mark.usefixtures("add_groups")
def test_save__update_existing_group(unit_of_work, group):
    updated_group = GroupFactory.create(
        id_=group.id(),
        tenant_id=group.tenant_id(),
        name=group.name,
        document_types=[uuid4().hex for _ in range(3)],
    )

    unit_of_work.groups.save(updated_group)

    assert unit_of_work.groups.group_of_id(group.id(), group.tenant_id()) == updated_group


@pytest.mark.usefixtures("add_groups")
def test_save__update_existing_group__all_document_ids_deleted(unit_of_work, group):
    updated_group = GroupFactory.create(
        id_=group.id(),
        tenant_id=group.tenant_id(),
        document_types=[],
        name=group.name,
    )

    unit_of_work.groups.save(updated_group)

    assert unit_of_work.groups.group_of_id(group.id(), group.tenant_id()) == updated_group


@pytest.mark.usefixtures("add_groups")
def test_delete__success(unit_of_work, group):
    group.delete()

    unit_of_work.groups.delete(group)

    assert unit_of_work.groups.group_of_id(group.id(), group.tenant_id()) is None


@pytest.mark.usefixtures("add_groups")
def test_delete_document_type__existing_id__removed_from_groups(unit_of_work, group, document_type_id):
    unit_of_work.groups.delete_document_type(document_type_id())
    unit_of_work.commit()

    updated_group = unit_of_work.groups.group_of_id(group.id(), group.tenant_id())
    assert document_type_id() not in [dt() for dt in updated_group.document_types]


@pytest.mark.usefixtures("add_groups")
def test_delete_document_type__groups_with_doc_type__cascade_deleted(unit_of_work, test_groups, document_type_id):
    unit_of_work.groups.delete_document_type(document_type_id())
    unit_of_work.commit()

    for original_group in test_groups:
        updated_group = unit_of_work.groups.group_of_id(original_group.id(), original_group.tenant_id())
        assert document_type_id() not in [dt() for dt in updated_group.document_types]


def test_delete_document_type__non_existent_id__no_error(unit_of_work):
    non_existent_id = uuid4().hex

    unit_of_work.groups.delete_document_type(non_existent_id)
    unit_of_work.commit()
