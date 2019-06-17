import sys

from galaxy.api.plugin import Plugin, create_and_run_plugin
from galaxy.api.consts import Platform


class PluginExample(Plugin):

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

def main():
    create_and_run_plugin(PluginExample, sys.argv)

# run plugin event loop
if __name__ == "__main__":
    main()
