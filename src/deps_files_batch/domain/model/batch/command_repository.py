from typing import Optional, Protocol

from .batch import Batch

__all__ = ["ICommandBatchRepository"]


class ICommandBatchRepository(Protocol):
    def batch_of_id(self, batch_id: str, tenant_id: str) -> Optional[Batch]:
        pass

    def save(self, batch: Batch) -> None:
        pass

    def batches_of_ids(self, ids: set[str], tenant_id: str) -> list[Batch]:
        pass

    def delete_all(self, batches: list[Batch]) -> None:
        pass
