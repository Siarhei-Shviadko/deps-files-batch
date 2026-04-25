from collections import defaultdict
from typing import Iterable

from sqlalchemy import Row

from deps_files_batch.domain.model import Batch, Error, File

from ...tables import BatchTable, FileTable

__all__ = ["BatchMapper", "FileMapper"]
BatchTableMapping = dict[str, BatchTable]
BatchFilesMapping = defaultdict[str, list[FileTable]]
BatchGroupMapping = dict[str, str]


class FileMapper:
    @classmethod
    def to_domain(cls, file: FileTable) -> File:
        error = (e := file.error) and Error(code=e["code"], message=e["message"])
        return File(
            id_=file.id,
            name=file.name,
            file_path=file.file_path,
            status=file.status,
            document_id=file.document_id,
            document_type_id=file.document_type_id,
            error=error,
            processing_params=file.processing_parameters,
        )


class BatchMapper:
    @classmethod
    def parse_rows_to_batches(cls, rows: Iterable[Row]) -> list[Batch]:
        batch_mapping, batch_files_mapping = cls._group_rows_data(rows)
        return [
            cls._build_batch(batch_data=batch_mapping[batch_id], batch_files=batch_files_mapping[batch_id])
            for batch_id in batch_mapping
        ]

    @classmethod
    def _group_rows_data(cls, rows: Iterable[Row]) -> tuple[BatchTableMapping, BatchFilesMapping]:
        batch_mapping: dict[str, BatchTable] = {}
        batch_files_mapping: defaultdict[str, list[FileTable]] = defaultdict(list)
        for row in rows:
            batch_fields = row.BatchTable
            file_fields = row.FileTable
            batch_mapping[batch_fields.id] = batch_fields
            batch_files_mapping[batch_fields.id].append(file_fields)
        return batch_mapping, batch_files_mapping

    @classmethod
    def _build_batch(cls, batch_data: BatchTable, batch_files: list[FileTable]) -> Batch:
        files = [*map(FileMapper.to_domain, batch_files)]
        return Batch(
            id_=batch_data.id,
            tenant_id=batch_data.tenant_id,
            name=batch_data.name,
            status=batch_data.status,
            metadata=batch_data.batch_metadata,
            files=files,
            created_at=batch_data.created_at,
            updated_at=batch_data.updated_at,
            group_id=batch_data.group_id,
        )
