import asyncio
import json
import logging
import pathlib
import queue
import socketserver

from galaxy_swift.api.exceptions import ClientError
from galaxy_swift.api.handlers import GalaxyTCPHandler
from galaxy_swift.api.models import Response
from galaxy_swift.jsonrpc.exceptions import JsonRpcError
from galaxy_swift.jsonrpc.parsers import JsonRpcParser
from galaxy_swift.paths import PluginPath
from galaxy_swift.tokens.generators import UUIDTokenGenerator


class BaseGalaxyClientStub:

    host = '127.0.0.1'

    def __init__(self, token, port):
        self.token = token
        self.port = port
        self.parser = JsonRpcParser()

        self.reader = None
        self.writer = None
        self.responses = queue.Queue()

    def _handle_input(self, data):
        try:
            parsed_data =self.parser.parse(data)
            logging.info("Received data: %s", parsed_data)
            response = Response(**parsed_data)
        except JsonRpcError as exc:
            logging.error(exc)
            return
        except TypeError as exc:
            logging.error(exc)
            return

        return self._handle_response(response)

    def _handle_response(self, response):
        return response


class GalaxyClientStub(socketserver.TCPServer, BaseGalaxyClientStub):

    def __init__(self, token, port):
        BaseGalaxyClientStub.__init__(self, token, port)
        socketserver.TCPServer.__init__(
            self, self.address, GalaxyTCPHandler, bind_and_activate=False)

    @property
    def address(self):
        return (self.host, self.port)

    def run(self):
        logging.info("Running client")
        logging.info("Binding client on %s", self.server_address)
        self.server_bind()
        logging.info("Activating client")
        self.server_activate()
        logging.info("Serving client")
        self.serve_forever()
        logging.info("Terminated client")

    def terminate(self):
        self.server_close()
        self.shutdown()

    def send(self, method, request_id):
        if not self.writer:
            raise ClientError("No plugin connected")
        data_dict = {
            'jsonrpc': '2.0',
            'id': request_id,
            'method': 'get_capabilities',
        }
        data = json.dumps(data_dict)
        data_bytes = (data + "\n").encode("utf-8")
        self.writer.write(data_bytes)
        logging.info("Sent data")

    def read(self):
        data = self.reader.readline()
        self.responses.put(data)

    def receive(self):
        logging.info("Receiving data")
        data = self.responses.get()
        addr = self.writer._sock.getpeername()
        logging.info("Received %d bytes of data from %s", len(data), addr)
        data_stripped= data.strip()
        return self._handle_input(data_stripped)

    def get_capabilities(self):
        logging.info("Send get capabilities")
        self.send('get_capabilities', 123)
        return self.receive()


class GalaxyAsyncClientStub(BaseGalaxyClientStub):

    def __init__(self, token, port, loop=None):
        super().__init__(token, port)

        self._active = False
        self._connected = False
        self._loop = loop

    async def run(self):
        logging.info("Running client")
        self._active = True
        await asyncio.gather(
            self.pass_control(),
            self.start_server(loop=self._loop),
            loop=self._loop,
        )

    def stop(self):
        logging.info("Stopping client")
        self._active = False

    def disconnect(self):
        logging.info("Plugin disconnected from server")
        self._connected = False

        self.reader = None
        self.writer = None

    async def start_server(self, loop=None):
        logging.info("Starting server on %s", self.port)
        server = await asyncio.start_server(
            self.on_plugin_connected,
            host=self.host, port=self.port, loop=loop,
        )
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
            await self.read()

            # logging.info("Send: %r" % message)
            # writer.write(data)
            # await writer.drain()

            # logging.info('Close the client socket')
            # writer.close()

    async def read(self):
        data = await self.reader.readline()
        self.responses.put(data)

    def receive(self):
        logging.info("Receiving data")
        disconnect = False
        try:
            logging.info("Reading data")
            data = self.responses.get()
            logging.info("Reading data 2")
            addr = self.writer.get_extra_info('peername')
            logging.info("Received %d bytes of data from %s", len(data), addr)

            if not data:
                disconnect = True
        except Exception as exc:
            logging.error(exc)
            disconnect = True

        if disconnect:
            self.disconnect()
            return

        data_stripped= data.strip()
        return self._handle_input(data_stripped)

    def send(self, method, request_id=None):
        if not self._connected:
            raise ClientError("No plugin connected")
        data_dict = {
            'jsonrpc': '2.0',
            'id': request_id,
            'method': 'get_capabilities',
        }
        data = json.dumps(data_dict)
        data_bytes = (data + "\n").encode("utf-8")
        self.writer.write(data_bytes)

    def terminate(self):
        logging.info("Shutting down server")
        self._active = False

    def get_capabilities(self):
        logging.info("Send get capabilities")
        self.send('get_capabilities', 123)
        return self.receive()

    def shutdown(self):
        logging.info("Send shutdown")
        self.send('shutdown', 123)
        return self.receive()
