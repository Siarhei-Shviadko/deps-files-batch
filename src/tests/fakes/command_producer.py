from typing import NamedTuple

from deps_message_flow.commands.common import Command as PubSubCommand

__all__ = ["FakeCommandProducer", "Command"]


class Command(NamedTuple):
    channel: str
    command: PubSubCommand
    reply_to: str


class FakeCommandProducer:
    def __init__(self) -> None:
        self._sent: list[Command] = []

    @property
    def sent(self) -> list[Command]:
        return self._sent

    def send(self, channel: str, command: PubSubCommand, reply_to: str, **kwargs) -> None:
        self.sent.append(Command(channel=channel, command=command, reply_to=reply_to))
