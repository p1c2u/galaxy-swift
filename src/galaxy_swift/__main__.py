import logging

from galaxy_swift.cli.commands import BaseCommand
from galaxy_swift.cli.parsers import RootParser, CommandParser
from galaxy_swift.exceptions import GalaxySwiftError


def setup_logging(level=logging.INFO):
    sh = logging.StreamHandler()
    sh.setLevel(level)
    logger = logging.getLogger()
    logger.addHandler(sh)
    logger.setLevel(level)


def main(args=None):
    prog_name = 'galaxy'
    setup_logging(logging.DEBUG)

    logging.debug("Parsing root command")
    root_parser = RootParser(prog_name, BaseCommand.commands)
    root_namespace = root_parser.parse_args(args)

    logging.debug("Parsing sub command")
    command = BaseCommand.create(root_namespace.command)
    command_parser = CommandParser(prog_name, command)
    command_namespace = command_parser.parse_args(root_namespace.args)

    logging.debug("Handling command")
    try:
        command.handle(command_namespace)
    except GalaxySwiftError as exc:
        logging.exception("%s: error: %s", prog_name, exc)
        raise SystemExit(2)

# run plugin event loop
if __name__ == "__main__":
    main()
