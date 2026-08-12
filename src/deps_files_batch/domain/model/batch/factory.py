from typing import Any, Self

from ..shared import EntityId
from .batch import Batch
from .events import BatchCreated
from .file import File
from .file.builder import FileBuilder

__all__ = ["BatchBuilder"]


class BatchBuilder:
    def __init__(self, tenant_id: str) -> None:
        self._tenant_id: str = tenant_id
        self._name: str | None = None
        self._group_id: str | None = None
        self._metadata: dict[str, Any] | None = None
        self._source_file_id: str | None = None
        self._files: list["File"] = []

    @classmethod
    def for_tenant(cls, tenant_id: str) -> Self:
        return cls(tenant_id)

    def with_name(self, name: str) -> Self:
        self._name = name
        return self

    def with_group_id(self, group_id: str) -> Self:
        self._group_id = group_id
        return self

    def with_file(self) -> "FileBuilder":
        return FileBuilder(parent=self, collection=self._files)

    def with_metadata(self, metadata: dict[str, Any] | None) -> Self:
        self._metadata = metadata
        return self

    def with_source_file_id(self, source_file_id: str | None) -> Self:
        self._source_file_id = source_file_id
        return self

    def build(self) -> Batch:
        batch_id = EntityId().value
        return Batch(
            id_=batch_id,
            tenant_id=self._tenant_id,
            name=self._name,
            metadata=self._metadata,
            group_id=self._group_id,
            source_file_id=self._source_file_id,
            files=self._files,
            events=[
                BatchCreated(
                    id=batch_id,
                    name=self._name,
                    group_id=self._group_id,
                    files=[file.id() for file in self._files],
                ),
            ],
        )
