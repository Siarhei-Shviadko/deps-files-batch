from dataclasses import dataclass

from deps_message_flow.commands.common import Command

__all__ = ["GetDocumentTypes", "GetDocumentTypesReply"]


class GetDocumentTypes(Command):
    pass  # noqa: WPS604, WPS420


@dataclass
class GetDocumentTypesReply(Command):
    document_types: list[dict[str, str]]
