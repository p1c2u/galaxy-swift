import sys

from galaxy.api.consts import Platform, PresenceState
from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.types import UserInfo, Presence


class DummyPlugin(Plugin):

    PLATFORM = Platform.Generic
    VERSION = '0.1.0'

    def __init__(self, reader, writer, token):
        super().__init__(
            self.PLATFORM,
            self.VERSION,
            reader,
            writer,
            token
        )

    # implement methods
    async def authenticate(self, stored_credentials=None):
        pass

    async def get_users(self):
        return [
            UserInfo(
                "5", False, "Ula", "http://avatar.png",
                Presence(PresenceState.Offline),
            )
        ]


def main():
    create_and_run_plugin(DummyPlugin, sys.argv)

# run plugin event loop
if __name__ == "__main__":
    main()
