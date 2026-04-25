import pytest

from tests.fakes import (
    FakeCommandBatchRepository,
    FakeCommandGroupRepository,
    FakeQueryBatchRepository,
    FakeUnitOfWork,
)


@pytest.fixture
def postgres_session_mock(mocker, containers):
    mock = mocker.Mock(containers.datasources.postgres_session())
    containers.datasources.postgres_session.override(mock)

    yield mock

    containers.datasources.postgres_session.reset_override()


@pytest.fixture(autouse=True)
def fake_query_batch_repository(repositories):
    with repositories.query_batch.override(FakeQueryBatchRepository()) as repo:
        yield repo()


@pytest.fixture(autouse=True, scope="function")
def fake_unit_of_work(containers):
    fuow = FakeUnitOfWork(
        groups=FakeCommandGroupRepository(),
        batches=FakeCommandBatchRepository(),
    )

    containers.unit_of_work.override(fuow)

    yield fuow

    containers.unit_of_work.reset_override()
