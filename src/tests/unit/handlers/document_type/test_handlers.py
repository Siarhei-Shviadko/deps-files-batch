import pytest

from deps_files_batch.messaging.handlers import (
    document_type_created_handler,
    document_type_deleted_handler,
)


def test_document_type_created__created(
    document_type_created_dee,
    fake_unit_of_work,
    document_type_id,
):
    document_type_created_handler(document_type_created_dee)

    assert document_type_id() in fake_unit_of_work.groups._document_types


@pytest.mark.usefixtures("save_document_type")
def test_document_type_deleted__deleted(
    document_type_deleted_dee,
    fake_unit_of_work,
    document_type_id,
):
    document_type_deleted_handler(document_type_deleted_dee)

    assert document_type_id() not in fake_unit_of_work.groups._document_types
