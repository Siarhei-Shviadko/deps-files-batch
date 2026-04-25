from typing import Any

from deps_files_batch.domain.model import Batch, BatchBuilder, FileCreationData


def build_batch_with_file_params(
    batch_name: str,
    file_params: list[FileCreationData],
    group_id: str,
    tenant_id: str,
    batch_metadata: dict[str, Any] | None = None,
) -> Batch:
    batch_builder = (
        BatchBuilder.for_tenant(tenant_id).with_name(batch_name).with_group_id(group_id).with_metadata(batch_metadata)
    )
    for file in file_params:
        batch_builder = (
            batch_builder.with_file()
            .with_name(file.name)
            .with_path(file.file_path)
            .with_document_type_id(file.document_type_id)
            .with_processing_params(file.processing_params)
        )
    batch = batch_builder.build()
    return batch
