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
from galaxy_swift.jsonrpc.generators import SeqIdGenerator
from galaxy_swift.jsonrpc.parsers import JsonRpcParser
from galaxy_swift.paths import PluginPath
from galaxy_swift.tokens.generators import UUIDTokenGenerator

log = logging.getLogger(__name__)


class BaseGalaxyClientStub:

    host = '127.0.0.1'

    def __init__(self, token, port):
        self.token = token
        self.port = port
        self.parser = JsonRpcParser()
        self.request_id_generator = SeqIdGenerator()

        self.reader = None
        self.writer = None
        self.responses = queue.Queue()

    def is_connected(self):
        raise NotImplementedError

    def get_peername(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def receive(self):
        log.info("Receiving data")
        try:
            data = self.responses.get()
            addr = self.get_peername()
            log.info("Received %d bytes of data from %s", len(data), addr)

            if not data:
                raise Exception("No data")
        except Exception as exc:
            log.error(exc)
            self.disconnect()
            return

        data_stripped = data.strip()
        return self._handle_input(data_stripped)

    def send(self, method, **params):
        if not self.is_connected():
            raise ClientError("No plugin connected")

        request_id = next(self.request_id_generator)
        data_dict = {
            'jsonrpc': '2.0',
            'id': request_id,
            'method': method,
            'params': params,
        }
        log.info("Sent data: %s", data_dict)
        data = json.dumps(data_dict)
        data_bytes = (data + "\n").encode("utf-8")
        addr = self.get_peername()
        log.info("Sent %d bytes of data to %s", len(data_bytes), addr)
        self.writer.write(data_bytes)

    def call(self, method, **params):
        log.info("Call %s", method)
        self.send(method, **params)
        return self.receive()

    # internal
    def shutdown(self):
        return self.call('shutdown')

    def get_capabilities(self):
        return self.call('get_capabilities')

    def initialize_cache(self, data: dict):
        return self.call('initialize_cache', data=data)

    def ping(self):
        return self.call('ping')

    # external
    def init_authentication(self):
        return self.call('init_authentication')

    def pass_login_credentials(self, step, credentials, cookies):
        return self.call(
            'pass_login_credentials',
            step=step, credentials=credentials, cookies=cookies,
        )

    def import_owned_games(self):
        return self.call('import_owned_games')

    def _handle_input(self, data):
        try:
            parsed_data =self.parser.parse(data)
            log.info("Received data: %s", parsed_data)
            response = Response(**parsed_data)
        except JsonRpcError as exc:
            log.error(exc)
            return
        except TypeError as exc:
            log.error(exc)
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
        log.info("Running client")
        log.info("Binding client on %s", self.server_address)
        self.server_bind()
        log.info("Activating client")
        self.server_activate()
        log.info("Serving client")
        self.serve_forever()
        log.info("Terminated client")

    def terminate(self):
        self.server_close()
        self.shutdown()

    def is_connected(self):
        return bool(self.writer)

    def read(self):
        data = self.reader.readline()
        self.responses.put(data)

    def get_peername(self):
        return self.writer._sock.getpeername()


class GalaxyAsyncClientStub(BaseGalaxyClientStub):

    def __init__(self, token, port, loop=None, connected_cb=None):
        super().__init__(token, port)

        self._active = False
        self._connected = False
        self._loop = loop

        self._connected_cb = connected_cb

    async def run(self):
        log.info("Running client")
        self._active = True
        await asyncio.gather(
            self.pass_control(),
            self.start_server(loop=self._loop),
            loop=self._loop,
        )

    def stop(self):
        log.info("Stopping client")
        self._active = False

    def disconnect(self):
        log.info("Plugin disconnected from server")
        self._connected = False

        self.reader = None
        self.writer = None

    async def start_server(self, loop=None):
        log.info("Starting server on %s", self.port)
        server = await asyncio.start_server(
            self.on_plugin_connected,
            host=self.host, port=self.port, loop=loop,
        )
        log.info('Server running: %s', server)

    async def pass_control(self):
        while self._active:
            try:
                self.tick()
            except Exception:
                log.exception("Unexpected exception raised in plugin tick")
            await asyncio.sleep(1)

    def tick(self):
        # log.info("tick")
        return

    async def on_plugin_connected(self, reader, writer):
        log.info("Plugin connected to server")
        self._connected = True
        if self._connected_cb is not None:
            self._connected_cb()

        self.reader = reader
        self.writer = writer

        while self._connected:
            await self.read()

            # log.info("Send: %r" % message)
            # writer.write(data)
            # await writer.drain()

            # log.info('Close the client socket')
            # writer.close()

    async def read(self):
        data = await self.reader.readline()
        self.responses.put(data)

    def get_peername(self):
        return self.writer.get_extra_info('peername')

    def is_connected(self):
        return self._connected

    def terminate(self):
        log.info("Shutting down server")
        self._active = False
