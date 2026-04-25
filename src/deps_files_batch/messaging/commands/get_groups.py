from dataclasses import dataclass

from deps_message_flow.commands.common import Command

from deps_files_batch.domain.model import GroupInfo

__all__ = ["GetGroups", "GetGroupsReply"]


class GetGroups(Command):
    pass


@dataclass
class GetGroupsReply(Command):
    groups: list[GroupInfo]
