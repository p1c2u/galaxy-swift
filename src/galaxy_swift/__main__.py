import logging

from galaxy_swift.cli.commands import BaseCommand
from galaxy_swift.cli.parsers import RootParser, CommandParser
from galaxy_swift.exceptions import GalaxySwiftError

prog_name = 'galaxy_swift'
log = logging.getLogger(prog_name)


def setup_logging(level=logging.INFO):
    sh = logging.StreamHandler()
    log.addHandler(sh)
    log.setLevel(level)


def main(args=None):
    root_parser = RootParser(prog_name, BaseCommand.commands)
    root_namespace = root_parser.parse_args(args)

    setup_logging(root_namespace.log_level.value)

    log.debug("Parsing sub command")
    command = BaseCommand.create(root_namespace.command)
    command_parser = CommandParser(prog_name, command)
    command_namespace = command_parser.parse_args(root_namespace.args)

    log.debug("Handling command")
    try:
        command.handle(command_namespace)
    except GalaxySwiftError as exc:
        log.exception("%s: error: %s", prog_name, exc)
        raise SystemExit(2)

# run plugin event loop
if __name__ == "__main__":
    main()
