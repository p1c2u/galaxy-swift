import abc
import os
import sys

from galaxy_swift.clients import ClientStub
from galaxy_swift.paths import PluginPath
from galaxy_swift.runners import SubprocessRunner


class BaseCommand(abc.ABC):

    help = NotImplemented
    argument = NotImplemented

    commands = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.commands[cls.command] = cls

    def __init__(self, plugin_dir=None, stdout=None, stderr=None):
        self.plugin_dir = plugin_dir or os.getcwd()
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr

    @classmethod
    def add_arguments(cls, parser):
        pass

    @property
    def plugin_path(self):
        return PluginPath(self.plugin_dir)


class InfoCommand(BaseCommand):

    help = 'Print plugin info'
    command = 'info'

    def handle(self, *args, **options):
        manifest = self.plugin_path.get_manifest()

        self.stdout.writelines([
            'Info: \n',
            ' Name: %s\n' % manifest.name,
            ' Platform: %s\n' % manifest.platform,
            ' Guid: %s\n' % manifest.guid,
            ' Version: %s\n' % manifest.version,
            ' Description: %s\n' % manifest.description,
            ' Author: %s\n' % manifest.author,
            ' Email: %s\n' % manifest.email,
            ' Url: %s\n' % manifest.url,
            ' Script: %s\n' % manifest.script,
        ])


class RunCommand(BaseCommand):

    help = 'Run plugin'
    command = 'run'

    @property
    def runner(self):
        return SubprocessRunner(
            stdout=self.stdout, stderr=self.stderr)

    def handle(self, *args, **options):
        self.runner.integrate_plugin(self.plugin_path)

        self.stdout.write('Done')
