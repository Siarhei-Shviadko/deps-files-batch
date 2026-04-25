from collections import defaultdict
from typing import Iterable

from sqlalchemy import Row

from deps_files_batch.domain.model import BatchInfo, FileInfo, GroupInfo

from ...tables import BatchTable, FileTable

__all__ = ["BatchInfoMapper", "FileInfoMapper"]

BatchTableMapping = dict[str, BatchTable]
BatchFilesMapping = defaultdict[str, list[FileTable]]
BatchGroupMapping = dict[str, dict]


class GroupInfoMapper:
    @classmethod
    def from_row(cls, group_row: dict) -> GroupInfo | None:
        if group_row is None:
            return None
        return GroupInfo(id=group_row["id"], name=group_row["name"])


class FileInfoMapper:
    @classmethod
    def from_row(cls, file_row: Row["FileTable"]) -> FileInfo:
        return {
            "id": file_row.id,
            "name": file_row.name,
            "status": file_row.status,
            "document_id": file_row.document_id,
            "document_type_id": file_row.document_type_id,
            "engine": file_row.processing_parameters.get("engine"),
            "llm_type": file_row.processing_parameters.get("llm_type"),
            "parsing_features": file_row.processing_parameters.get("parsing_features"),
            "error": file_row.error,
        }


class BatchInfoMapper:
    @classmethod
    def parse_rows_to_batch_infos(cls, rows: Iterable[Row["BatchTable"]]) -> list[BatchInfo]:
        batch_mapping, files_mapping, group_mapping = cls._group_rows_data(rows)
        return [
            cls._build_batch_info(
                batch_data=batch_mapping[batch_id],
                group=group_mapping[batch_id],
                files_data=files_mapping[batch_id],
            )
            for batch_id in batch_mapping
        ]

    @classmethod
    def _group_rows_data(cls, rows: Iterable[Row]) -> tuple[BatchTableMapping, BatchFilesMapping, BatchGroupMapping]:
        batch_mapping: BatchTableMapping = {}
        batch_files_mapping: BatchFilesMapping = defaultdict(list)
        batch_group_mapping: BatchGroupMapping = {}

        for row in rows:
            batch_fields = row.BatchTable
            file_fields = row.FileTable
            group = {"id": row.group_id, "name": row.group_name} if row.group_id else None

            batch_mapping[batch_fields.id] = batch_fields
            batch_files_mapping[batch_fields.id].append(file_fields)
            batch_group_mapping[batch_fields.id] = group

        return batch_mapping, batch_files_mapping, batch_group_mapping

    @classmethod
    def _build_batch_info(cls, batch_data, group, files_data) -> BatchInfo:
        files = [*map(FileInfoMapper.from_row, files_data)]

        return BatchInfo(
            id=batch_data.id,
            name=batch_data.name,
            group=GroupInfoMapper.from_row(group),
            status=batch_data.status,
            created_at=batch_data.created_at,
            files=files,
            metadata=batch_data.batch_metadata,
        )
