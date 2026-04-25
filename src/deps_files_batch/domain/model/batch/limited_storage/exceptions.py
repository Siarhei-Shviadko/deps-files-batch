from deps_files_batch.domain.exceptions import LimitExceeded

__all__ = ["FileLimitViolated"]


class FileLimitViolated(LimitExceeded):
    code = "file_limit_exceeded"
