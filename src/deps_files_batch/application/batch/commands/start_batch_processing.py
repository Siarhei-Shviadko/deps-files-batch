from dataclasses import dataclass
from typing import TypeAlias

from deps_message_flow.commands.common import Command

__all__ = ["StartBatchProcessing"]

DocumentId: TypeAlias = str


@dataclass(slots=True)
class StartBatchProcessing(Command):
    documents: list[DocumentId]
