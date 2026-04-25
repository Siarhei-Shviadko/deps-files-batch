from deps_files_batch.domain.model import Group, IQueryGroupRepository


def test_exists_group_of_id__exists(
    query_group_repository: IQueryGroupRepository,
    group: Group,
    add_groups,
):
    group_exists = query_group_repository.exists_group_of_id(group_id=group.id(), tenant_id=group.tenant_id())

    assert group_exists


def test_exists_group_of_id__doesnt_exist(query_group_repository: IQueryGroupRepository, group: Group):
    group_exists = query_group_repository.exists_group_of_id(group_id=group.id(), tenant_id=group.tenant_id())

    assert not group_exists
