from ...shared import ExtendedEnum

__all__ = ["FileStatus"]


class FileStatus(ExtendedEnum):
    NEW = "new"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REVIEW = "review"
    FAILED = "failed"
    ABORTED = "aborted"
    EXPORTED = "exported"

    def __call__(self, *args, **kwargs):
        return self.value
