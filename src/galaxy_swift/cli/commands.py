import abc
import asyncio
import os
import sys
from functools import lru_cache

from galaxy_swift.cli.shells import GalaxyInteractiveShellEmbed
from galaxy_swift.paths import PluginPath
from galaxy_swift.runners import (
    PluginSubprocessRunner, ClientStubRunner, AsyncClientStubRunner,
)
from galaxy_swift.tokens.generators import UUIDTokenGenerator


class BaseCommand(abc.ABC):

    help = NotImplemented
    argument = NotImplemented

    commands = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.commands[cls.command] = cls  # pylint: disable=no-member

    def __init__(self, plugin_dir=None, stdout=None, stderr=None):
        self.plugin_dir = plugin_dir or os.getcwd()
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr

    @classmethod
    def create(cls, command):
        assert command in cls.commands

        command_cls = cls.commands[command]
        return command_cls()

    def add_arguments(self, parser):
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


class ShellCommand(BaseCommand):

    help = 'Run interactive shell'
    command = 'shell'

    @property
    @lru_cache(1)
    def plugin_runner(self):
        return PluginSubprocessRunner(
            stdout=self.stdout, stderr=self.stderr)

    @property
    @lru_cache(1)
    def client_runner(self):
        return AsyncClientStubRunner()

    def handle(self, *args, **options):
        token = UUIDTokenGenerator().generate()
        port = '5431'

        self.client_runner.bind(token, port)
        self.client_runner.start()
        # asyncio.run(self.runner.start_client(), debug=True)
        self.plugin_runner.bind(self.plugin_path, token, port)
        self.plugin_runner.start()

        # self.stdout.write('Done')

        shell = GalaxyInteractiveShellEmbed(exit_msg='Goodbye!')
        shell(self.client_runner.client)

        self.plugin_runner.terminate()
        self.client_runner.terminate()
