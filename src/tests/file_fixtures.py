from random import choice
from uuid import uuid4

import pytest
from faker.proxy import Faker
from more_itertools import first, last

from deps_files_batch.application import DocumentCreationResult
from deps_files_batch.domain.model import (
    DATA_EXTRACTION_ERROR_CODE,
    DATA_EXTRACTION_ERROR_MESSAGE,
    EXPORTING_ERROR_CODE,
    EXPORTING_ERROR_MESSAGE,
    IDENTIFICATION_ERROR_CODE,
    IDENTIFICATION_ERROR_MESSAGE,
    IMAGE_PREPROCESSING_ERROR_CODE,
    IMAGE_PREPROCESSING_ERROR_MESSAGE,
    PARSING_ERROR_CODE,
    PARSING_ERROR_MESSAGE,
    POSTPROCESSING_ERROR_CODE,
    POSTPROCESSING_ERROR_MESSAGE,
    PREPROCESSING_ERROR_CODE,
    PREPROCESSING_ERROR_MESSAGE,
    UNIFICATION_ERROR_CODE,
    UNIFICATION_ERROR_MESSAGE,
    VALIDATION_ERROR_CODE,
    VALIDATION_ERROR_MESSAGE,
    VERSION_IDENTIFICATION_ERROR_CODE,
    VERSION_IDENTIFICATION_ERROR_MESSAGE,
    DocumentId,
    DocumentTypeId,
    ErrorInfo,
    File,
    FileCreationData,
    FileCreationDataDict,
    FileId,
    FileInfo,
    FileStatus,
    ListBatchFileInfo,
    ParsingFeature,
    ProcessingParametersDict,
)

__all__ = [
    "file_path",
    "file_creation_data",
    "processing_params",
    "document_type_id",
    "document_id",
    "file",
    "file_without_document_type",
    "documents_creation_result_with_document_id",
    "error_info",
    "file_id",
    "file_id_without_document_type",
    "list_batch_file_info",
    "file_info",
    "error_code",
    "error_message",
    "file_with_document_id",
    "file_with_document_id_without_document_type",
    "file_name",
    "file_creation_data_dict",
    "_error_code_and_error_message",
    "aborted_file",
    "failed_file",
    "file_creation_data_without_document_type",
    "file_creation_data_without_document_type_dict",
]


@pytest.fixture
def document_type_id() -> DocumentTypeId:
    return DocumentTypeId()


@pytest.fixture
def document_id() -> DocumentId:
    return DocumentId()


@pytest.fixture
def file_path() -> str:
    return f"{uuid4().hex}.pdf"


@pytest.fixture
def file_name(faker: Faker) -> str:
    return faker.file_name(extension="pdf")


@pytest.fixture
def file_creation_data_dict(file_name, file_path, document_type_id, processing_params) -> FileCreationDataDict:
    return FileCreationDataDict(
        name=file_name,
        file_path=file_path,
        processing_params=processing_params,
        document_type_id=document_type_id(),
    )


@pytest.fixture
def file_creation_data_without_document_type_dict(file_name, file_path, processing_params) -> FileCreationDataDict:
    return FileCreationDataDict(
        name=file_name,
        file_path=file_path,
        processing_params=processing_params,
        document_type_id=None,
    )


@pytest.fixture
def file_creation_data(file_creation_data_dict) -> FileCreationData:
    return FileCreationData(
        name=file_creation_data_dict["name"],
        file_path=file_creation_data_dict["file_path"],
        processing_params=file_creation_data_dict["processing_params"],
        document_type_id=file_creation_data_dict["document_type_id"],
    )


@pytest.fixture
def file_creation_data_without_document_type(file_creation_data_without_document_type_dict) -> FileCreationData:
    return FileCreationData(
        name=file_creation_data_without_document_type_dict["name"],
        file_path=file_creation_data_without_document_type_dict["file_path"],
        processing_params=file_creation_data_without_document_type_dict["processing_params"],
        document_type_id=file_creation_data_without_document_type_dict["document_type_id"],
    )


@pytest.fixture
def processing_params(faker) -> ProcessingParametersDict:
    return {
        "engine": faker.word(),
        "language": faker.word(),
        "llm_type": faker.word(),
        "parsing_features": [*faker.random_sample(elements=[*ParsingFeature], length=2)],
    }


@pytest.fixture
def file(batch) -> File:
    return first(batch.files)


@pytest.fixture
def file_without_document_type(batch_without_document_type) -> File:
    return first(batch_without_document_type.files)


@pytest.fixture
def documents_creation_result_with_document_id(file, document_id) -> DocumentCreationResult:
    return DocumentCreationResult(id=file.id(), document_id=document_id(), error=None)


@pytest.fixture
def _error_code_and_error_message() -> tuple[str, str]:
    return choice(
        (
            (PREPROCESSING_ERROR_CODE, PREPROCESSING_ERROR_MESSAGE),
            (IDENTIFICATION_ERROR_CODE, IDENTIFICATION_ERROR_MESSAGE),
            (DATA_EXTRACTION_ERROR_CODE, DATA_EXTRACTION_ERROR_MESSAGE),
            (VALIDATION_ERROR_CODE, VALIDATION_ERROR_MESSAGE),
            (UNIFICATION_ERROR_CODE, UNIFICATION_ERROR_MESSAGE),
            (IMAGE_PREPROCESSING_ERROR_CODE, IMAGE_PREPROCESSING_ERROR_MESSAGE),
            (PARSING_ERROR_CODE, PARSING_ERROR_MESSAGE),
            (VERSION_IDENTIFICATION_ERROR_CODE, VERSION_IDENTIFICATION_ERROR_MESSAGE),
            (POSTPROCESSING_ERROR_CODE, POSTPROCESSING_ERROR_MESSAGE),
            (EXPORTING_ERROR_CODE, EXPORTING_ERROR_MESSAGE),
        ),
    )


@pytest.fixture
def error_code(_error_code_and_error_message) -> str:
    return first(_error_code_and_error_message)


@pytest.fixture
def error_message(_error_code_and_error_message) -> str:
    return last(_error_code_and_error_message)


@pytest.fixture
def error_info(error_code, error_message) -> ErrorInfo:
    return ErrorInfo(code=error_code, message=error_message)


@pytest.fixture
def file_id(file) -> FileId:
    return file.id


@pytest.fixture
def file_id_without_document_type(file_with_document_id_without_document_type) -> FileId:
    return file_with_document_id_without_document_type.id


@pytest.fixture
def file_info(file_with_document_id, error_info) -> FileInfo:
    return FileInfo(
        id=file_with_document_id.id(),
        name=file_with_document_id.name,
        status=file_with_document_id.status,
        engine=file_with_document_id.processing_params.engine,
        document_id=file_with_document_id.document_id(),
        document_type_id=file_with_document_id.document_type_id(),
        llm_type=file_with_document_id.processing_params.llm_type,
        parsing_features=[f.value for f in file_with_document_id.processing_params.parsing_features],
        error=error_info,
    )


@pytest.fixture
def list_batch_file_info(file) -> ListBatchFileInfo:
    return ListBatchFileInfo(
        name=file.name,
        status=file.status,
        error=file.error,
    )


@pytest.fixture
def file_with_document_id(batch_with_file_with_document_id):
    return first(batch_with_file_with_document_id.files)


@pytest.fixture
def file_with_document_id_without_document_type(batch_with_file_with_document_id_without_document_type):
    return first(batch_with_file_with_document_id_without_document_type.files)


@pytest.fixture
def aborted_file(file):
    file.update_status(FileStatus.ABORTED)

    return file


@pytest.fixture
def failed_file(file):
    file.update_status(FileStatus.FAILED)

    return file
