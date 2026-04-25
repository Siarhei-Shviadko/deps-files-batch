from functools import partial, reduce
from typing import List

from deps_files_batch.domain.model import (
    Batch,
    BatchFiltering,
    BatchInfo,
    BatchSortBy,
    BatchSorting,
    BatchSortOrder,
    File,
    FileInfo,
    ListBatchFileInfo,
    ListBatchUnit,
    Pagination,
)


def sort_entities_by_id(entities):
    return sorted(entities, key=lambda e: e.id())


def compare_batches(batch1: Batch, batch2: Batch) -> None:
    def compare_files(file1: File, file2: File):
        assert file1.name == file2.name, f"{file1.name} != {file2.name}"
        assert file1.file_path == file2.file_path, f"{file1.file_path} != {file2.file_path}"
        assert file1.document_type_id == file2.document_type_id, f"{file1.document_type_id} != {file2.document_type_id}"
        assert file1.status == file2.status, f"{file1.status} != {file2.status}"
        assert file1.document_id == file2.document_id, f"{file1.document_id} != {file2.document_id}"
        assert file1.error == file2.error, f"{file1.error} != {file2.error}"

    assert batch1.id == batch2.id, f"{batch1.id} != {batch2.id}"
    assert batch1.tenant_id == batch2.tenant_id, f"{batch1.tenant_id} != {batch2.tenant_id}"
    assert batch1.name == batch2.name, f"{batch1.name} != {batch2.name}"
    assert batch1.status == batch2.status, f"{batch1.status} != {batch2.status}"
    assert batch1.metadata == batch2.metadata, f"{batch1.metadata} != {batch2.metadata}"
    assert batch1.created_at == batch2.created_at, f"{batch1.created_at} != {batch2.created_at}"
    assert batch1.updated_at == batch2.updated_at, f"{batch1.updated_at} != {batch2.updated_at}"
    assert len(batch1.files) == len(batch2.files), f"Mismatched file counts: {len(batch1.files)} != {len(batch2.files)}"
    for file1, file2 in zip(sort_entities_by_id(batch1.files), sort_entities_by_id(batch2.files)):
        compare_files(file1, file2)


def compare_batch_and_batch_info(*, batch: Batch, batch_info: BatchInfo, group_name: str) -> None:
    def compare_file_and_file_info(file: File, file_info: FileInfo):
        assert file.id() == file_info["id"], f"{file.id()} != {file_info['id']}"

        expected_doc_id = (_w := file.document_id) and _w()
        assert expected_doc_id == file_info["document_id"], f"{expected_doc_id} != {file_info['document_id']}"

        assert file.name == file_info["name"], f"{file.name} != {file_info['name']}"
        assert file.status() == file_info["status"], f"{file.status()} != {file_info['status']}"
        assert file.error == file_info["error"], f"{file.error} != {file_info['error']}"

        document_type_id = (_v := file.document_type_id) and _v()
        assert (
            document_type_id == file_info["document_type_id"]
        ), f"{document_type_id} != {file_info['document_type_id']}"

        pps = file.processing_params
        assert pps.engine == file_info["engine"], f"{pps.engine} != {file_info['engine']}"
        assert pps.llm_type == file_info["llm_type"], f"{pps.llm_type} != {file_info['llm_type']}"

        file_pfs = pfs if (pfs := pps.parsing_features) is None else {pf.value for pf in pfs}
        file_info_pfs = pfs if (pfs := file_info["parsing_features"]) is None else {*pfs}
        assert file_pfs == file_info_pfs, f"{file_pfs} != {file_info_pfs}"

    assert batch.id() == batch_info["id"], f"{batch.id()} != {batch_info['id']}"
    assert batch.name == batch_info["name"], f"{batch.name} != {batch_info['name']}"
    if batch.group_id:
        assert group_name == batch_info["group"]["name"], f"{group_name} != {batch_info['group']}"
        assert batch.group_id() == batch_info["group"]["id"], f"{group_name} != {batch_info['group']}"

    assert batch.status() == batch_info["status"], f"{batch.status()} != {batch_info['status']}"
    assert batch.created_at == batch_info["created_at"], f"{batch.created_at} != {batch_info['created_at']}"
    assert len(batch.files) == len(batch_info["files"]), f"{len(batch.files)} != {len(batch_info['files'])}"
    assert batch.metadata == batch_info["metadata"], f"{batch.metadata} != {batch_info['metadata']}"

    sorted_file_infos = sorted(batch_info["files"], key=lambda fi: fi["id"])
    for file, file_info in zip(sort_entities_by_id(batch.files), sorted_file_infos):
        compare_file_and_file_info(file, file_info)


def compare_batch_and_list_batch_unit(*, batch: Batch, batch_info: ListBatchUnit, group_name: str) -> None:
    def compare_file_and_list_file_unit(file: File, file_info: ListBatchFileInfo):
        assert file.name == file_info["name"], f"{file.name} != {file_info['name']}"
        assert file.status() == file_info["status"], f"{file.status()} != {file_info['status']}"

        file_error = (er_ := file.error) and {"code": er_.code, "message": er_.message}
        assert file_error == file_info["error"], f"{file_error} != {file_info['error']}"

    assert batch.id() == batch_info["id"], f"{batch.id()} != {batch_info['id']}"
    assert batch.name == batch_info["name"], f"{batch.name} != {batch_info['name']}"
    if batch.group_id:
        assert group_name == batch_info["group"]["name"], f"{group_name} != {batch_info['group']['name']}"
        assert batch.group_id() == batch_info["group"]["id"], f"{group_name} != {batch_info['group']['id']}"
    assert batch.status() == batch_info["status"], f"{batch.status()} != {batch_info['status']}"
    assert batch.created_at == batch_info["created_at"], f"{batch.created_at} != {batch_info['created_at']}"
    assert len(batch.files) == len(batch_info["files"]), f"{len(batch.files)} != {len(batch_info['files'])}"

    sorted_batch_files = sorted(batch.files, key=lambda fi: fi.name)
    sorted_file_infos = sorted(batch_info["files"], key=lambda fi: fi["name"])
    for file, file_info in zip(sorted_batch_files, sorted_file_infos):
        compare_file_and_list_file_unit(file, file_info)


def _apply_filtering(batches: list[Batch], filtering: BatchFiltering) -> list[Batch]:
    result = batches
    if filtering.tenant_id:
        result = [*filter(lambda b: b.tenant_id() == filtering.tenant_id, result)]
    if filtering.name:
        result = [*filter(lambda b: b.name == filtering.name, result)]
    if filtering.status:
        result = [*filter(lambda b: b.status() in filtering.status, result)]
    if filtering.group:
        result = result  # expecting group to be group_id
    if filtering.date_start:
        result = [*filter(lambda b: b.created_at >= filtering.date_start, result)]
    if filtering.date_end:
        result = [*filter(lambda b: b.created_at <= filtering.date_end, result)]
    return result


def _apply_sorting(batches: list[Batch], sorting: BatchSorting) -> list[Batch]:
    MAX_UUID_VALUE = "ffffffff-ffff-ffff-ffff-ffffffffffff"
    descending = sorting.sort_order is BatchSortOrder.DESC
    sorting_key_mapping = {
        BatchSortBy.CREATED_AT: lambda b: b.created_at,
        BatchSortBy.NAME: lambda b: b.name,
        BatchSortBy.STATUS: lambda b: (b.status(), b.created_at),
        BatchSortBy.GROUP: lambda b: (MAX_UUID_VALUE if b.group_id is None else b.group_id(), b.created_at),
    }
    return sorted(batches, key=sorting_key_mapping[sorting.sort_by], reverse=descending)


def _apply_pagination(batches: list[Batch], pagination: Pagination) -> list[Batch]:
    offset = pagination.per_page * pagination.page
    limit = pagination.per_page
    batches_len = len(batches)
    last_element = offset + limit

    if offset > batches_len:
        return []
    if last_element > batches_len:
        last_element = batches_len
    return batches[offset:last_element]


def calculate_total_records_from_batches(batches: List[Batch], filtering: BatchFiltering) -> int:
    return len(_apply_filtering(batches, filtering))


def apply_sorting_filtering_and_pagination_to_batches(
    batches: list[Batch], filtering: BatchFiltering, sorting: BatchSorting, pagination: Pagination
) -> list[Batch]:
    return reduce(
        lambda val, func: func(val),
        [
            partial(_apply_filtering, filtering=filtering),
            partial(_apply_sorting, sorting=sorting),
            partial(_apply_pagination, pagination=pagination),
        ],
        batches,
    )
