import pytest
from sqlalchemy import text

from deps_files_batch.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


@pytest.fixture
def unit_of_work(containers):
    uow = containers.unit_of_work()
    with uow:
        yield uow


@pytest.fixture(autouse=True)
def empty_unit_of_work(unit_of_work: SqlAlchemyUnitOfWork):
    try:
        unit_of_work._session.execute(text("DELETE FROM batch"))
        unit_of_work.groups.erase_all_groups()
        unit_of_work.commit()
    except Exception as exception:
        raise exception

    yield

    try:
        unit_of_work._session.execute(text("DELETE FROM batch"))
        unit_of_work.groups.erase_all_groups()
        unit_of_work.commit()
    except Exception:
        pass


@pytest.fixture
def query_group_repository(repositories):
    return repositories.query_group()


@pytest.fixture
def query_batch_repository(repositories):
    return repositories.query_batch()


@pytest.fixture()
def add_groups(unit_of_work, test_groups):
    for group in test_groups:
        unit_of_work.groups.save(group)

    unit_of_work.commit()


@pytest.fixture
def save_batch(batch, fake_query_batch_repository) -> None:
    fake_query_batch_repository.save(batch)


@pytest.fixture
def save_batches(batches, fake_query_batch_repository) -> None:
    for batch in batches:
        fake_query_batch_repository.save(batch)
