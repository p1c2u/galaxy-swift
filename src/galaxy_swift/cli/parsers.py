from argparse import ArgumentParser, REMAINDER


class RootParser(ArgumentParser):

    def __init__(self, prog, commands, **kwargs):
        super().__init__(
            prog=prog,
            **kwargs,
        )
        self.add_argument(
            'command',
            choices=commands,
            help='the command to run',
            metavar='command',
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
