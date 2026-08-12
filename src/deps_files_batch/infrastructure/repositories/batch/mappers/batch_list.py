from collections import defaultdict
from pathlib import Path
from typing import Iterable

from sqlalchemy import Row

from deps_files_batch.domain.model import (
    ListBatchFileInfo,
    ListBatchGroupInfo,
    ListBatchInfo,
    ListBatchUnit,
    PaginatedResultMetadataInfo,
)

from ...tables import BatchTable, FileTable

__all__ = ["BatchListMapper"]

BatchTableMapping = dict[str, BatchTable]
BatchFilesMapping = defaultdict[str, list[Row]]
BatchGroupMapping = dict[str, dict]


class ListBatchGroupInfoMapper:
    @classmethod
    def from_row(cls, group_row: dict) -> ListBatchGroupInfo | None:
        if group_row is None:
            return None
        return ListBatchGroupInfo(id=group_row["id"], name=group_row["name"])


class ListFileUnitMapper:
    @classmethod
    def from_row(cls, file_row: Row["FileTable"]) -> "ListBatchFileInfo":
        return {"name": file_row.name, "status": file_row.file_status, "error": file_row.error}


class ListBatchUnitMapper:
    @classmethod
    def parse_rows_to_batch_units(cls, rows: Iterable[Row["BatchTable"]]) -> list["ListBatchUnit"]:
        batch_mapping, files_mapping, group_mapping = cls._group_rows_data(rows)
        return [
            cls._build_batch_unit(
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
            group = {"id": row.group_id, "name": row.group_name} if row.group_id else None
            batch_mapping[batch_fields.id] = batch_fields
            batch_files_mapping[batch_fields.id].append(row)
            batch_group_mapping[batch_fields.id] = group

        return batch_mapping, batch_files_mapping, batch_group_mapping

    @classmethod
    def _build_batch_unit(cls, batch_data, group, files_data) -> ListBatchUnit:
        files = [*map(ListFileUnitMapper.from_row, files_data)]
        return ListBatchUnit(
            id=batch_data.id,
            name=batch_data.name,
            group=ListBatchGroupInfoMapper.from_row(group),
            status=batch_data.status,
            created_at=batch_data.created_at,
            files=files,
            source_file_id=batch_data.source_file_id,
        )


class BatchListMapper:
    @classmethod
    def parse_rows_to_batch_infos(cls, rows: Iterable[Row], total: int) -> ListBatchInfo:
        batch_infos = ListBatchUnitMapper.parse_rows_to_batch_units(rows)
        metadata = PaginatedResultMetadataInfo(total=total, size=len(batch_infos))
        return ListBatchInfo(batches=batch_infos, metadata=metadata)
