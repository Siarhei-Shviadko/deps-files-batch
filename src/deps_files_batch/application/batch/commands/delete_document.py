from dataclasses import dataclass
from typing import TypeAlias

from deps_message_flow.commands.common import Command

__all__ = ["DeleteBatchDocument", "DeleteBatchesWithDocuments"]

DocumentId: TypeAlias = str


@dataclass(slots=True)
class DeleteBatchDocument(Command):
    document: DocumentId


@dataclass(slots=True)
class DeleteBatchesWithDocuments(Command):
    batch_ids: list[str]
