from deps_files_batch.infrastructure.unit_of_work import AbstractUnitOfWork

from .command_batch_repository import FakeCommandBatchRepository
from .command_group_repository import *

__all__ = ["FakeUnitOfWork"]


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self, groups: FakeCommandGroupRepository, batches: FakeCommandBatchRepository) -> None:
        self.groups = groups
        self.batches = batches

    def __enter__(self) -> None:
        pass

    def commit(self):
        pass

    def rollback(self):
        pass
