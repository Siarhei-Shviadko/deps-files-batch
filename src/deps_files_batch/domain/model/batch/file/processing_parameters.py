from enum import Enum
from typing import Iterable, TypedDict

from ...shared import Guard, ImmutableCheck

__all__ = ["ProcessingParameters", "ParsingFeature", "ProcessingParametersDict"]


class ParsingFeature(str, Enum):
    TABLES = "tables"
    IMAGES = "images"
    KEY_VALUE_PAIRS = "kvps"
    TEXT = "text"


class ProcessingParametersDict(TypedDict, total=False):
    engine: str | None
    language: str | None
    llm_type: str | None
    parsing_features: list[str] | None


class ProcessingParameters:
    engine = Guard[str](str, ImmutableCheck())
    language = Guard[str](str, ImmutableCheck())
    llm_type = Guard[str](str, ImmutableCheck())
    parsing_features = Guard[set[ParsingFeature]](set, ImmutableCheck())

    def __init__(
        self,
        engine: str | None = None,
        language: str | None = None,
        llm_type: str | None = None,
        parsing_features: Iterable[str | ParsingFeature] | None = None,
    ) -> None:
        if engine:
            self.engine = engine
        if language:
            self.language = language
        if llm_type:
            self.llm_type = llm_type
        if parsing_features:
            self.parsing_features = {*map(ParsingFeature, parsing_features)}

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)  # noqa: WPS222
            and self.engine == other.engine
            and self.language == other.language
            and self.llm_type == other.llm_type
            and self.parsing_features == other.parsing_features
        )

    def __repr__(self) -> str:
        return " ".join(
            (
                f"{self.__class__.__name__}(engine={self.engine!r},",
                f"language={self.language!r},",
                f"llm_type={self.llm_type!r},",
                f"parsing_features={self.parsing_features})",
            ),
        )
