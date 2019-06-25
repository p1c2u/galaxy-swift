from json import loads
from pathlib import PosixPath as Path

from galaxy_swift.exceptions import InvalidPlugin
from galaxy_swift.types import Manifest


class PluginPath(Path):

    MANIFEST_FILENAME = 'manifest.json'

    @property
    def manifest_file(self):
        return self / self.MANIFEST_FILENAME

    def read_manifest(self):
        if not self.manifest_file.is_file():
            raise InvalidPlugin(f'Manifest file not found in {self} directory')

        with self.manifest_file.open() as f:
            return f.read()

    def get_manifest(self):
        if not self.is_dir():
            raise InvalidPlugin(f'{self} directory does not exist')

        content = self.read_manifest()
        data = loads(content)
        return Manifest(**data)
