import asyncio
import logging
import pathlib

from galaxy_swift.paths import PluginPath
from galaxy_swift.tokens.generators import UUIDTokenGenerator

log = logging.getLogger(__name__)


class ClientStub:

    async def run(self, port: int):
        log.info("Starting server on %s", port)
        return asyncio.start_server(self.on_client_connected, port=port)

    async def on_client_connected(self, reader, writer):
        log.info("Client connected")
        data = await reader.read(100)
        message = data.decode()
        addr = writer.get_extra_info('peername')

        writer.write(data)
        await writer.drain()

        writer.close()
