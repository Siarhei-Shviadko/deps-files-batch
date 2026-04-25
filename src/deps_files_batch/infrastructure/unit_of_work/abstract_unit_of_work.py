import abc

from deps_files_batch.domain.model import (
    ICommandBatchRepository,
    ICommandGroupRepository,
)

__all__ = ["AbstractUnitOfWork"]


class AbstractUnitOfWork(abc.ABC):
    groups: ICommandGroupRepository
    batches: ICommandBatchRepository

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError
