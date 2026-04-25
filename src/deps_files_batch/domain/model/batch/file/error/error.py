from ....shared import Guard, ImmutableCheck

__all__ = ["Error"]


class Error:
    code = Guard[str](str, ImmutableCheck())
    message = Guard[str](str, ImmutableCheck())

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.code == self.code and other.message == self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code!r}, message={self.message!r})"
