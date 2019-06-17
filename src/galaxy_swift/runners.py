import logging
import subprocess

from galaxy_swift.paths import PluginPath
from galaxy_swift.tokens.generators import UUIDTokenGenerator

log = logging.getLogger(__name__)


class SubprocessRunner:

    def __init__(self, stdout=None, stderr=None, token_generator=None):
        self.stdout = stdout
        self.stderr = stderr
        self.token_generator = token_generator or UUIDTokenGenerator()

    @property
    def client(self):
        return ClientStub()

    def run_client(self):
        self.client.run()

    def integrate_plugin(self, plugin_path: PluginPath):
        log.info("Integrating %s plugin directory", plugin_path)

        manifest = plugin_path.get_manifest()
        token = self.token_generator.generate()
        port = '5431'

        # TODO: add plugin dir to pythonpath
        proc = subprocess.run(
            ['python', manifest.script, token, port],
            cwd=plugin_path,
            stdout=self.stdout, stderr=self.stderr,
            text=True,
        )
