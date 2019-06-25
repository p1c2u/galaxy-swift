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

    def handle(self, namespace, **options):
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

    def add_arguments(self, parser):
        parser.add_argument(
            '-p', '--port',
            help=f'client-plugin connection port (default: 5431).',
            metavar='port',
            default='5431',
        )
        parser.add_argument(
            '-t', '--token',
            help=f'client-plugin connection token (default: random token).',
            metavar='token',
            default=None,
        )

    @property
    @lru_cache(1)
    def plugin_runner(self):
        return PluginSubprocessRunner(
            stdout=self.stdout, stderr=self.stderr)

    @property
    @lru_cache(1)
    def client_runner(self):
        return AsyncClientStubRunner()

    def handle(self, namespace, **options):
        if namespace.token is None:
            namespace.token = UUIDTokenGenerator().generate()

        self.client_runner.bind(
            namespace.token, namespace.port)
        self.client_runner.start()
        self.plugin_runner.bind(
            self.plugin_path, namespace.token, namespace.port)
        self.plugin_runner.start()
        self.client_runner.wait()

        shell = GalaxyInteractiveShellEmbed(exit_msg='Goodbye!')
        shell(self.client_runner.client)

        self.plugin_runner.terminate()
        self.client_runner.terminate()


class RunCommand(BaseCommand):

    help = 'Run one-off client method'
    command = 'run'
    methods = [
        'get_capabilities', 'ping', 'import_user_infos',
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '-p', '--port',
            help=f'client-plugin connection port.',
            metavar='port',
            default='5431',
        )
        parser.add_argument(
            '-t', '--token',
            help=f'client-plugin connection token (default: random token).',
            metavar='token',
            default=None,
        )
        methods_list = tuple(self.methods)
        parser.add_argument(
            'method',
            choices=self.methods,
            help=f'the client method to run {methods_list}.',
            metavar='method',
        )

    @property
    @lru_cache(1)
    def plugin_runner(self):
        return PluginSubprocessRunner(
            stdout=self.stdout, stderr=self.stderr)

    @property
    @lru_cache(1)
    def client_runner(self):
        return AsyncClientStubRunner()

    def handle(self, namespace, **options):
        if namespace.token is None:
            namespace.token = UUIDTokenGenerator().generate()

        self.client_runner.bind(
            namespace.token, namespace.port)
        self.client_runner.start()
        self.plugin_runner.bind(
            self.plugin_path, namespace.token, namespace.port)
        self.plugin_runner.start()
        self.client_runner.wait()

        ret = self.client_runner.execute(namespace.method)

        self.stdout.write(f'{ret}\n')

        self.plugin_runner.terminate()
        self.client_runner.terminate()
 