from dataclasses import dataclass
from typing import TypedDict

from .processing_parameters import ProcessingParametersDict

__all__ = ["FileCreationData", "FileCreationDataDict"]


class FileCreationDataDict(TypedDict):
    name: str
    file_path: str
    processing_params: ProcessingParametersDict
    document_type_id: str | None


@dataclass(slots=True)
class FileCreationData:
    name: str
    file_path: str
    processing_params: ProcessingParametersDict
    document_type_id: str | None = None
