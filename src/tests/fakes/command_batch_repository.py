from deps_files_batch.domain.model import Batch
from deps_files_batch.domain.model.batch.command_repository import (
    ICommandBatchRepository,
)

__all__ = ["FakeCommandBatchRepository"]

BatchIdTenantId = tuple[str, str]


class FakeCommandBatchRepository(ICommandBatchRepository):
    def __init__(self) -> None:
        self._storage: dict[BatchIdTenantId, Batch] = {}

    def batch_of_id(self, batch_id: str, tenant_id: str) -> Batch | None:
        return self._storage.get((batch_id, tenant_id))

    def save(self, batch: Batch) -> None:
        self._storage[(batch.id(), batch.tenant_id())] = batch

    def batches_of_ids(self, ids: set[str], tenant_id: str) -> list[Batch]:
        return [b for b in self._storage.values() if b.id() in ids and b.tenant_id() == tenant_id]

    def delete_all(self, batches: list[Batch]) -> None:
        for batch in batches:
            del self._storage[(batch.id(), batch.tenant_id())]
