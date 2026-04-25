from typing import TypedDict

__all__ = ["ErrorInfo"]


class ErrorInfo(TypedDict):
    message: str
    code: str
