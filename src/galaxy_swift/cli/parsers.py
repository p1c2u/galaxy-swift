from argparse import ArgumentParser, REMAINDER

from galaxy_swift.cli.enums import LogLevel


class RootParser(ArgumentParser):

    def __init__(self, prog, commands, **kwargs):
        super().__init__(
            prog=prog,
            **kwargs,
        )
        commands_list = tuple(commands.keys())
        self.add_argument(
            'command',
            choices=commands,
            help=f'the command to run {commands_list}.',
            metavar='command',
        )
        levels_list = tuple(LogLevel.get_levels())
        self.add_argument(
            '-l', '--log-level',
            default='WARNING',
            dest='log_level',
            type=LogLevel.__getitem__,
            nargs='?',
            help=f'Set the logging output level {levels_list}.',
        )
        self.add_argument(
            'args',
            nargs=REMAINDER,
        )


class CommandParser(ArgumentParser):

    def __init__(self, prog, command, **kwargs):
        super().__init__(
            prog=f'{prog} {command.command}',
            description=command.help or None,
            **kwargs,
        )
        command.add_arguments(self)
