import argparse
import logging
import pathlib
import yaml

from rich.logging import RichHandler

from meetchecker.core import run
from meetchecker.daemon import Daemon
from meetchecker.files import DotFile
from meetchecker.files import Locations

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("database", nargs="?", default=None)
    parser.add_argument("--ask", action="store_true", default=False)
    parser.add_argument("-o", "--output", default=None)
    parser.add_argument(
        "--dotfile", default=pathlib.Path("~/.meetchecker.yaml").expanduser()
    )
    parser.add_argument("--checks", default=None)
    parser.add_argument(
        "-d",
        "--daemon",
        action="store_true",
        default=False,
        help="Daemon mode, refresh on an interval",
    )
    parser.add_argument(
        "-i", "--interval", type=int, default=120, help="Refresh interval in seconds"
    )
    parser.add_argument(
        "-q",
        "--quiet",
        help="Only warnings or errors",
        action="store_const",
        dest="loglevel",
        const=logging.WARNING,
        default=logging.INFO,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Be verbose",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
    )
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(
        level=args.loglevel,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )

    dotfile = DotFile(args.dotfile)
    locations = Locations(dotfile.workdir)

    database = locations.resolve_database(
        args.database, args.ask, dotfile.last_database
    )
    output = locations.resolve_output(args.output, database)
    checks_file = locations.resolve_checks(args.checks, dotfile.checks)

    logging.info(f"DATABASE: {database}")
    logging.info(f"OUTPUT: {output}")
    logging.info(f"CHECKS: {checks_file}")

    dotfile.last_database = str(database)

    with open(checks_file) as f:
        checks = yaml.safe_load(f)

    if args.daemon:
        Daemon(database, output, checks, args.interval).run()
    else:
        run(database, output, checks)


if __name__ == "__main__":
    main()
