import asyncio
import logging
import subprocess
import threading

from galaxy_swift.api.clients import GalaxyClientStub, GalaxyAsyncClientStub
from galaxy_swift.exceptions import GalaxySwiftError
from galaxy_swift.paths import PluginPath


class PluginSubprocessRunner(threading.Thread):

    def __init__(self, stdout=None, stderr=None):
        threading.Thread.__init__(self)
        self.stdout = stdout
        self.stderr = stderr

        self.proc = None

        self.plugin_path = None
        self.token = None
        self.port = None

    def bind(self, plugin_path: PluginPath, token: str, port: str):
        logging.info(
            "Binding %s plugin directory on port %s with token %s",
            plugin_path, port, token,
        )
        self.plugin_path = plugin_path
        self.token = token
        self.port = port

    def run(self):
        logging.info("Starting %s plugin directory", self.plugin_path)
        if self.plugin_path is None:
            raise RuntimeError("runner.bind() not called")

        manifest = self.plugin_path.get_manifest()

        # TODO: add plugin dir to pythonpath
        self.proc = subprocess.Popen(
            ['python', manifest.script, self.token, self.port],
            cwd=self.plugin_path,
            stdout=self.stdout, stderr=self.stderr,
            text=True,
        )
        statuscode = self.proc.wait()
        self.on_exit(statuscode)

        # return proc

    def on_exit(self, statuscode):
        if statuscode > 0:
            raise GalaxySwiftError(
                f'Error while running plugin. Status code: {statuscode}')
        logging.info("Plugin stopped")

    def terminate(self):
        logging.info("Terminating plugin")
        self.proc.terminate()


class ClientStubRunner(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self, daemon=True)

        self.client = None

        self.port = None
        self.token = None

        self._loop = None

    def bind(self, token: str, port: int, loop=None):
        logging.info("Binding client on %s port with %s token", port, token)
        self.port = int(port)
        self.token = token

        self._loop = loop

    def run(self):
        logging.info("Starting client")
        self.client = GalaxyClientStub(self.token, self.port)
        self.client.run()

    def terminate(self):
        logging.info("Terminating client")
        self.client.terminate()


class AsyncClientStubRunner(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self, daemon=True)

        self.client = None

        self.port = None
        self.token = None

        self._loop = None

    def bind(self, token: str, port: int, loop=None):
        logging.info("Binding client on %s port with %s token", port, token)
        self.port = int(port)
        self.token = token

        self._loop = loop

    def run(self):
        logging.info("Starting client")
        self.client = GalaxyAsyncClientStub(self.token, self.port)
        asyncio.run(self.client.run())

    def terminate(self):
        logging.info("Terminating client")
        self.client.terminate()
