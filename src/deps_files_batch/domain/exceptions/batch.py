from deps_files_batch.domain.exceptions import NotFoundError

__all__ = ["BatchNotFound", "FileNotFound"]


class BatchNotFound(NotFoundError):
    code = "batch_not_found"

    def __init__(self, batch_id: str) -> None:
        super().__init__(f"Batch with id `{batch_id}` not found.")


class FileNotFound(NotFoundError):
    code = "file_not_found"

    def __init__(self, file_id: str) -> None:
        super().__init__(f"File with id `{file_id}` not found.")
