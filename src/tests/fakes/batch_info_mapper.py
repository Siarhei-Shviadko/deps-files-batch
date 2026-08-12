from deps_files_batch.domain.model import (
    Batch,
    BatchInfo,
    Error,
    ErrorInfo,
    File,
    FileInfo,
    GroupInfo,
)

__all__ = ["BatchInfoMapper"]


class BatchInfoMapper:
    class FileInfoMapper:
        class ErrorInfoMapper:
            @classmethod
            def from_model(cls, error: Error) -> ErrorInfo:
                return ErrorInfo(code=error.code, message=error.message)

        @classmethod
        def from_model(cls, file: File) -> FileInfo:
            parsing_features = (
                [f.value for f in parsing_features]
                if (parsing_features := file.processing_params.parsing_features)
                else None
            )
            return FileInfo(
                id=file.id(),
                name=file.name,
                status=file.status(),
                engine=file.processing_params.engine,
                document_id=(document_id := file.document_id) and document_id(),
                document_type_id=(document_type_id := file.document_type_id) and document_type_id(),
                llm_type=file.processing_params.llm_type,
                parsing_features=parsing_features,
                error=cls.ErrorInfoMapper.from_model(file.error) if file.error else None,
            )

    class GroupInfoMapper:
        @classmethod
        def from_model(cls, batch: Batch, group_name: str) -> GroupInfo | None:
            if not batch.group_id:
                return None
            return GroupInfo(id=batch.group_id(), name=group_name)

    @classmethod
    def from_model(cls, batch: Batch, group_name: str) -> BatchInfo:
        return BatchInfo(
            id=batch.id(),
            name=batch.name,
            group=cls.GroupInfoMapper.from_model(batch=batch, group_name=group_name),
            status=batch.status,
            created_at=batch.created_at,
            files=[*map(cls.FileInfoMapper.from_model, batch.files)],
            metadata=batch.metadata,
            source_file_id=batch.source_file_id,
        )
