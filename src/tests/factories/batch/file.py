from random import choice, randint
from uuid import uuid4

import factory
from faker import Faker

from deps_files_batch.domain.model import (
    DocumentId,
    DocumentTypeId,
    Error,
    File,
    FileId,
    FileStatus,
    ParsingFeature,
    ProcessingParametersDict,
)

__all__ = ["FileFactory", "ErrorFactory", "ProcessingParametersDictFactory"]

faker = Faker()


class ProcessingParametersDictFactory(factory.Factory):
    class Meta:
        model = ProcessingParametersDict

    engine = factory.LazyFunction(lambda: choice((faker.word(), None)))
    language = factory.LazyFunction(lambda: choice((faker.language_code(), None)))
    llm_type = factory.LazyFunction(lambda: choice((faker.word(), None)))
    parsing_features = factory.LazyFunction(
        lambda: choice(
            (
                faker.random_choices(elements=ParsingFeature, length=randint(1, 3)),
                None,
            ),
        ),
    )


class ErrorFactory(factory.Factory):
    class Meta:
        model = Error

    code = factory.Faker("word")
    message = factory.Faker("word")


class FileFactory(factory.Factory):
    class Meta:
        model = File

    id_ = factory.LazyFunction(lambda: FileId().value)
    name = factory.LazyFunction(lambda: f"{uuid4().hex}.pdf")
    file_path = factory.Faker("file_path")
    processing_params = factory.SubFactory(ProcessingParametersDictFactory)
    status = factory.Faker("random_element", elements=FileStatus)
    document_id = factory.LazyFunction(lambda: choice((DocumentId().value, None)))
    document_type_id = factory.LazyFunction(lambda: choice((DocumentTypeId().value, None)))
    error = factory.LazyAttribute(
        lambda obj: ErrorFactory() if obj.status in {FileStatus.FAILED, FileStatus.ABORTED} else None,
    )
