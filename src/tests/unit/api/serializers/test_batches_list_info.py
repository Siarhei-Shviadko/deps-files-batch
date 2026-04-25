from more_itertools import first

from deps_files_batch.api import SerializedListBatchFileInfo, SerializedListBatchInfo
from deps_files_batch.domain.model import BatchInfo, FileInfo, ListBatchFileInfo


def test_list_batch_info__ok(list_batch_info: BatchInfo):
    info = SerializedListBatchInfo(**list_batch_info)

    assert info.id == list_batch_info["id"]
    assert info.name == list_batch_info["name"]
    assert info.group == list_batch_info["group"]
    assert info.status == list_batch_info["status"]
    assert info.created_at == list_batch_info["created_at"]
    assert isinstance(first(info.files), SerializedListBatchFileInfo)


def test_list_batch_file_info__ok(list_batch_file_info: ListBatchFileInfo):
    info = SerializedListBatchFileInfo(**list_batch_file_info)

    assert info.name == list_batch_file_info["name"]
    assert info.status == list_batch_file_info["status"]
    assert info.error == list_batch_file_info["error"]
