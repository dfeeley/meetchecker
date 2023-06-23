import argparse
import logging
import pathlib

from datasourcing import extract_tables_from_mdb, dump_tables, get_data_from_csvs


def dump(meet_file, output_dir, force=False):
    tables = extract_tables_from_mdb(meet_file)
    dump_tables(tables, output_dir, overwrite=force)


def load(output_dir):
    data = get_data_from_csvs(output_dir)
    breakpoint()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--meet", type=pathlib.Path, dest="meet_file", required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--force", action="store_const", const=True, default=False)
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
    logging.basicConfig(level=args.loglevel)
    if not args.output.exists():
        raise ValueError(f"Path {args.output} does not exist")
    if not args.output.is_dir():
        raise ValueError(f"Path {args.output} is not a directory")

    if not args.meet_file.exists():
        raise ValueError(f"Meet file at {args.meet_file} does not exist")
    dump(args.meet_file, args.output, args.force)


if __name__ == "__main__":
    main()
