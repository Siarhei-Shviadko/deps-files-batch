from more_itertools import first

from deps_files_batch.api import SerializedBatchInfo, SerializedFileInfo
from deps_files_batch.domain.model import BatchInfo


def test_batch_info__ok(batch_info: BatchInfo):
    info = SerializedBatchInfo(**batch_info)

    assert info.id == batch_info["id"]
    assert info.name == batch_info["name"]
    assert info.group == batch_info["group"]
    assert info.status == batch_info["status"]
    assert info.created_at == batch_info["created_at"]
    assert isinstance(first(info.files), SerializedFileInfo)


def test_file_info__ok(file_info):
    info = SerializedFileInfo(**file_info)

    assert info.id == file_info["id"]
    assert info.name == file_info["name"]
    assert info.status == file_info["status"]
    assert info.document_id == file_info["document_id"]
    assert info.document_type_id == file_info["document_type_id"]
    assert info.engine == file_info["engine"]
    assert info.llm_type == file_info["llm_type"]
    assert info.parsing_features == file_info["parsing_features"]
    assert info.error == file_info["error"]
