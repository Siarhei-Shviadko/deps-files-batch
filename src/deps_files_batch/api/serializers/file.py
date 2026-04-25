from pydantic import Field

from deps_files_batch.domain.model import FileCreationData

from .batch import FileRequestSerializer
from .configured_base_serializer import ConfiguredSerializer

__all__ = ["AddBatchFilesRequest"]


class AddBatchFilesRequest(ConfiguredSerializer):
    files: list[FileRequestSerializer] = Field(..., min_items=1)

    @property
    def files_parameters(self) -> list[FileCreationData]:
        return [
            FileCreationData(
                name=fp.name,
                file_path=fp.path,
                processing_params=fp.processing_params.dict(by_alias=False),
                document_type_id=fp.document_type_id,
            )
            for fp in self.files
        ]
