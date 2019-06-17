import os
from optparse import OptionParser

from galaxy_swift.cli.commands import BaseCommand


USAGE = """galaxy <command>
Commands:
    create
        Create a new plugin project.
    run
        Run an kodiswift plugin from the command line.
Help:
    To see options for a command, run `galaxy <command> -h`
"""


def main(args=None):
    parser = OptionParser()
    if not args:
        parser.set_usage(USAGE)
        parser.error('At least one command is required.')

    # spy sys.argv[1] in order to use correct opts/args
    command = args[0]

    if command == '-h':
        parser.set_usage(USAGE)
        opts, args = parser.parse_args(args)

    if command not in BaseCommand.commands:
        parser.error('Invalid command')

    manager_class = BaseCommand.commands[command]
    manager_class.add_arguments(parser)
    if hasattr(manager_class, 'usage'):
        parser.set_usage(manager_class.usage)

    opts, parsed_args = parser.parse_args(args)
    manager = manager_class()
    manager.handle(opts, parsed_args)

# run plugin event loop
if __name__ == "__main__":
    main()
