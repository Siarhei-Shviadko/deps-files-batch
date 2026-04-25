from uuid import uuid4

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from deps_files_batch import api
from deps_files_batch.domain.model import TenantId
from deps_files_batch.entrypoint import create_fastapi
from deps_files_batch.infrastructure.access_management import user

from .batch_fixtures import *
from .fakes import (
    FakeCommandProducer,
    FakeDomainEventPublisher,
    FakeQueryBatchRepository,
)
from .file_fixtures import *
from .group_fixtures import *


@pytest.fixture(scope="session")
def app() -> FastAPI:
    fastapi_app = create_fastapi()
    yield fastapi_app


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def session_containers(app):
    return app.containers


@pytest.fixture
def containers(session_containers):
    with session_containers.reset_singletons():
        yield session_containers


@pytest.fixture(autouse=True)
def fake_domain_event_publisher(containers):
    with containers.domain_event_publisher.override(FakeDomainEventPublisher()) as publisher:
        yield publisher()


@pytest.fixture(autouse=True)
def fake_command_producer(containers):
    with containers.command_producer.override(FakeCommandProducer()) as producer:
        yield producer()


@pytest.fixture
def repositories(containers):
    return containers.repositories


@pytest.fixture
def query_user_service(containers):
    return containers.query_user_service()


@pytest.fixture
def command_user_service(containers):
    return containers.command_user_service()


@pytest.fixture
def group_service(containers):
    return containers.group_service()


@pytest.fixture
def batch_service(containers, fake_domain_event_publisher, fake_command_producer):
    return containers.batch_service()


@pytest.fixture
def tenant_id() -> TenantId:
    return TenantId()


@pytest.fixture
def deps_token(tenant_id):
    return {
        "organisation": tenant_id(),
        "subject": "subject",
        "roles": [],
        "groups": [tenant_id()],
    }


@pytest.fixture(autouse=True)
def set_user(deps_token):
    token = user.set(deps_token)
    yield
    user.reset(token)


def fake_query_batch_repository(repositories):
    with repositories.query_batch.override(FakeQueryBatchRepository()) as repo:
        yield repo()


@pytest.fixture(autouse=True)
def mocked_middleware(monkeypatch, mocker, deps_token):
    monkeypatch.setattr(api.auth, "set_user_from_token", mocker.Mock(deps_token))
