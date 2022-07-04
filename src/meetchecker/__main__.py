import argparse
import logging
import pathlib
import yaml

from meetchecker.core import run
from meetchecker.daemon import Daemon

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default=None)
    parser.add_argument("--console", action="store_true", default=False)
    parser.add_argument(
        "-d",
        "--daemon",
        action="store_true",
        default=False,
        help="Daemon mode, refresh on an interval",
    )
    parser.add_argument(
        "-i", "--interval", type=int, default=60, help="Refresh interval in seconds"
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


def find_config_file():
    path = pathlib.Path("./checkmeet.yaml")
    if path.exists():
        return path


def get_config(path):
    config_path = pathlib.Path(path) if path else find_config_file()
    if not config_path:
        raise ValueError("No config file specified, and could not find one")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def main():
    args = parse_args()
    logging.basicConfig(level=args.loglevel)
    config = get_config(args.config)
    if args.daemon:
        Daemon(config, args.interval).run()
    else:
        run(config["file"], config["output"], config["checks"])
