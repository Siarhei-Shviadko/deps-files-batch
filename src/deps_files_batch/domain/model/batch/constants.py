from .status import BatchStatus

__all__ = [
    "MAX_BATCH_FILES_AMOUNT",
    "MAX_BATCH_NAME_LENGTH",
    "MIN_BATCH_FILES_AMOUNT",
    "END_STATUSES",
    "ERROR_STATUSES",
]

MIN_BATCH_FILES_AMOUNT: int = 1
MAX_BATCH_FILES_AMOUNT: int = 50
MAX_BATCH_NAME_LENGTH: int = 255

END_STATUSES = frozenset((BatchStatus.COMPLETED, BatchStatus.EXPORTED, BatchStatus.FAILED, BatchStatus.ABORTED))
ERROR_STATUSES = frozenset((BatchStatus.FAILED, BatchStatus.ABORTED))
