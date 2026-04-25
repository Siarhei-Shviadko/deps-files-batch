from datetime import timedelta, timezone
from random import choice, randint
from uuid import uuid4

import factory
from faker import Faker

from deps_files_batch.domain.model import Batch, BatchId, BatchStatus, GroupId, TenantId

from .file import FileFactory

__all__ = ["BatchFactory"]

faker = Faker()


class BatchFactory(factory.Factory):
    class Meta:
        model = Batch

    id_ = factory.LazyFunction(lambda: BatchId().value)
    tenant_id = factory.LazyFunction(lambda: TenantId().value)
    name = factory.LazyFunction(lambda: uuid4().hex)
    status = factory.Faker("random_element", elements=BatchStatus)
    metadata = faker.random_element(elements=(faker.pydict(allowed_types=(str,)), None))
    created_at = factory.Faker("date_time", tzinfo=timezone.utc)
    updated_at = factory.LazyAttribute(lambda obj: obj.created_at + timedelta(days=randint(1, 10)))
    group_id = factory.LazyFunction(lambda: choice((GroupId().value, None)))
    files = factory.LazyFunction(lambda: [FileFactory() for _ in range(randint(1, 10))])

    @factory.post_generation
    def synchronize_batch_status(self, create, extracted, **kwargs) -> None:
        if create:
            self._synchronize_status()
