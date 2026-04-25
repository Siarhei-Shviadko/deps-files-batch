from typing import TYPE_CHECKING, Self

from .file import File

if TYPE_CHECKING:
    from ..factory import BatchBuilder
    from .processing_parameters import ProcessingParametersDict

__all__ = ["FileBuilder"]


class FileBuilder:
    def __init__(self, parent: "BatchBuilder" = None, collection: list[File] = None) -> None:
        self._collection = collection
        self._parent = parent
        self._name: str | None = None
        self._path: str | None = None
        self._processing_params: "ProcessingParametersDict" = {}
        self._document_type_id: str | None = None

    def with_name(self, name: str) -> Self:
        self._name = name
        return self

    def with_path(self, path: str) -> Self:
        self._path = path
        return self

    def with_document_type_id(self, document_type_id: str | None) -> Self:
        self._document_type_id = document_type_id
        return self

    def with_processing_params(self, processing_params: "ProcessingParametersDict") -> Self:
        self._processing_params = processing_params
        return self

    def with_file(self) -> "FileBuilder":
        new_file = self._build()
        self._collection.append(new_file)
        return self._parent.with_file()

    def build(self):
        new_file = self._build()
        if not self._has_parents():
            return new_file
        self._collection.append(new_file)
        return self._parent.build()

    def _build(self) -> File:
        return File(
            name=self._name,
            file_path=self._path,
            processing_params=self._processing_params,
            document_type_id=self._document_type_id,
        )

    def _has_parents(self) -> bool:
        return self._collection is not None and self._parent is not None
