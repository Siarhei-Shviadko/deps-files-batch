from typing import Type

from deps_files_batch.domain.model import (
    Batch,
    File,
    ListBatchFileInfo,
    ListBatchGroupInfo,
    ListBatchInfo,
    ListBatchUnit,
    PaginatedResultMetadataInfo,
)

__all__ = ["ListBatchInfoMapper"]


class ListBatchInfoMapper:
    class ListBatchFileInfoMapper:
        @classmethod
        def from_model(cls, file: File) -> ListBatchFileInfo:
            return ListBatchFileInfo(
                name=file.name,
                status=file.status(),
                error=(err := file.error) and {"code": err.code, "message": err.message},
            )

    class ListBatchGroupInfoMapper:
        @classmethod
        def from_model(cls, batch: Batch, group_name: str) -> ListBatchGroupInfo | None:
            if not batch.group_id:
                return None
            return ListBatchGroupInfo(id=batch.group_id(), name=group_name)

    class ListBatchUnitMapper:
        @classmethod
        def from_model(cls, batch: Batch, group_name: str, result_mapper: Type["ListBatchInfoMapper"]) -> ListBatchUnit:
            return ListBatchUnit(
                id=batch.id(),
                name=batch.name,
                status=batch.status,
                created_at=batch.created_at,
                group=result_mapper.ListBatchGroupInfoMapper.from_model(batch=batch, group_name=group_name),
                files=[*map(result_mapper.ListBatchFileInfoMapper.from_model, batch.files)],
            )

    @classmethod
    def from_models(cls, batches: list[Batch], group_names: list[str], total: int) -> ListBatchInfo:
        batches = [
            cls.ListBatchUnitMapper.from_model(batch=batch, group_name=group_name, result_mapper=cls)
            for batch, group_name in zip(batches, group_names)
        ]
        metadata = PaginatedResultMetadataInfo(size=len(batches), total=total)
        return ListBatchInfo(batches=batches, metadata=metadata)
