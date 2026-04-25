from uuid import uuid4

import pytest

from deps_files_batch.domain.model import DocumentTypeId, GroupFactory, GroupId

__all__ = ["group", "test_groups", "group_id", "save_group", "group_name"]


@pytest.fixture
def group_id() -> GroupId:
    return GroupId()


@pytest.fixture
def group_name(faker) -> str:
    return faker.word()


@pytest.fixture
def group(group_id, tenant_id, document_type_id, group_name):
    return GroupFactory.create(
        id_=group_id(), tenant_id=tenant_id(), name=group_name, document_types=[document_type_id()]
    )


@pytest.fixture
def save_group(group, fake_unit_of_work):
    fake_unit_of_work.groups.save(group)

    return group


@pytest.fixture
def test_groups(group):
    return [group]
