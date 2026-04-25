from collections import UserDict

from ..constants import MAX_BATCH_FILES_AMOUNT, MIN_BATCH_FILES_AMOUNT
from .exceptions import FileLimitViolated

__all__ = ["LimitedFilesDict"]


class LimitedFilesDict(UserDict):
    def __init__(self, *args, **kwargs) -> None:
        self.min_files: int = MIN_BATCH_FILES_AMOUNT
        self.max_files: int = MAX_BATCH_FILES_AMOUNT

        initial_data = dict(*args, **kwargs)
        self._verify_item_size(len(initial_data))
        super().__init__(initial_data)

    def __setitem__(self, key, value):
        self.data[key] = value
        self._verify_item_size(len(self.data))

    def __delitem__(self, key):  # noqa: WPS603
        self.data.pop(key, None)
        self._verify_item_size(len(self.data))

    def _verify_item_size(self, item_size: int):
        if self.min_files > item_size:
            raise FileLimitViolated(f"Cannot save less than {self.min_files} files.")
        if item_size > self.max_files:
            raise FileLimitViolated(f"Cannot save more than {self.max_files} files.")
