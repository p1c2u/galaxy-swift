import asyncio
import json
import logging
import pathlib

from galaxy_swift.api.exceptions import ClientError
from galaxy_swift.api.models import Response
from galaxy_swift.jsonrpc.exceptions import JsonRpcError
from galaxy_swift.jsonrpc.parsers import JsonRpcParser
from galaxy_swift.paths import PluginPath
from galaxy_swift.tokens.generators import UUIDTokenGenerator


class GalaxyClientStub:

    host = '127.0.0.1'

    def __init__(self, token, port):
        self.token = token
        self.port = port

        self.parser = JsonRpcParser()

        self._active = False
        self._connected = False

        self.reader = None
        self.write = None

    async def run(self):
        logging.info("Running client")
        self._active = True
        await asyncio.gather(self.pass_control(), self.start_server())

    def stop(self):
        logging.info("Stopping client")
        self._active = False

    def disconnect(self):
        logging.info("Plugin disconnected from server")
        self._connected = False

        self.reader = None
        self.writer = None

    async def start_server(self):
        logging.info("Starting server on %s", self.port)
        server = await asyncio.start_server(
            self.on_plugin_connected, host=self.host, port=self.port)
        logging.info('Server running: %s', server)

    async def pass_control(self):
        while self._active:
            try:
                self.tick()
            except Exception:
                logging.exception("Unexpected exception raised in plugin tick")
            await asyncio.sleep(1)

    def tick(self):
        # logging.info("tick")
        return

    async def on_plugin_connected(self, reader, writer):
        logging.info("Plugin connected to server")
        self._connected = True

        self.reader = reader
        self.writer = writer

        while self._connected:
            try:
                data = await self.reader.readline()
                addr = self.writer.get_extra_info('peername')
                logging.info("Received %d bytes of data from %s", len(data), addr)

                if not data:
                    self.disconnect()
                    continue
            except Exception as exc:
                logging.error(exc)
                self.disconnect()
                continue

            data_stripped= data.strip()
            self._handle_input(data_stripped)

            # logging.info("Send: %r" % message)
            # writer.write(data)
            # await writer.drain()

            # logging.info('Close the client socket')
            # writer.close()

    def terminate(self):
        logging.info("Shutting down server")
        self._active = False

    def get_capabilities(self):
        logging.info("Send get capabilities")
        if not self._connected:
            raise ClientError("No plugin connected")
        data_dict = {
            'jsonrpc': '2.0',
            'id': 123,
            'method': 'get_capabilities',
        }
        data = json.dumps(data_dict)
        data_bytes = (data + "\n").encode("utf-8")
        self.writer.write(data_bytes)

    def shutdown(self):
        logging.info("Send shutdown")
        if not self._connected:
            raise ClientError("No plugin connected")
        data_dict = {
            'jsonrpc': '2.0',
            'id': 123,
            'method': 'shutdown',
        }
        data = json.dumps(data_dict)
        data_bytes = (data + "\n").encode("utf-8")
        self.writer.write(data_bytes)

    def _handle_input(self, data):
        try:
            parsed_data =self.parser.parse(data)
            logging.info("Received data: %s", parsed_data)
            request = Response(**parsed_data)
        except JsonRpcError as exc:
            logging.error(exc)
            return
        except TypeError as exc:
            logging.error(exc)
            return

        self._handle_request(request)

    def _handle_request(self, request):
        return
