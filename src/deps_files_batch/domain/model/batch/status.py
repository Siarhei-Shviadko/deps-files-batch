from ..shared import ExtendedEnum

__all__ = ["BatchStatus"]


class BatchStatus(ExtendedEnum):
    NEW = "new"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REVIEW = "review"
    FAILED = "failed"
    ABORTED = "aborted"
    CONSOLIDATION = "consolidation"
    VALIDATION = "validation"
    EXPORTING = "exporting"
    EXPORTED = "exported"

    def __call__(self, *args, **kwargs):
        return self.value
