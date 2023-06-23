import argparse
import logging
import pathlib


from meetchecker.datasourcing import get_data_from_csvs


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--day1",
        type=pathlib.Path,
        default=pathlib.Path("~/Projects/meetchecker/resources/ttday1").expanduser(),
    )
    parser.add_argument(
        "--day2",
        type=pathlib.Path,
        default=pathlib.Path("~/Projects/meetchecker/resources/ttday2").expanduser(),
    )
    parser.add_argument(
        "--manual",
        type=pathlib.Path,
        default=pathlib.Path(
            "~/Projects/meetchecker/resources/ttday2_populated"
        ).expanduser(),
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


def format_seconds_as_time(raw):
    if raw == 0:
        return "NS"
    minutes, seconds = divmod(int(raw), 60)
    millis = raw - (minutes * 60 + seconds)
    millis = int(round(millis, 3) * 1000)
    if minutes:
        return f"{minutes}:{seconds:02.0f}.{millis:03d}"
    return f"{seconds:02.0f}.{millis:03d}"


def prepare(day1_path, day2_path):
    day1 = get_data_from_csvs(day1_path)["entry"]
    day2 = get_data_from_csvs(day2_path)["entry"]

    day1_subset = day1[day1.event_no >= 33]
    day2_subset = day2[["event_no", "athlete_name", "fin_time"]]
    merged = day1_subset.merge(
        day2_subset,
        left_on=["event_no", "athlete_name"],
        right_on=["event_no", "athlete_name"],
        suffixes=["_day1", "_day2"],
    )
    merged.sort_values(["event_no", "fin_heat", "fin_lane"], inplace=True)
    merged["fin_time_formatted"] = merged.fin_time_day2.apply(format_seconds_as_time)
    print(merged)
    merged[
        [
            "event_name",
            "event_no",
            "fin_heat",
            "fin_lane",
            "athlete_name",
            "fin_time_formatted",
        ]
    ].to_csv("/tmp/merged.csv")


def check(day2_path, manual_path):
    day2 = get_data_from_csvs(day2_path)["entry"]
    manual = get_data_from_csvs(manual_path)["entry"]

    manual_subset = manual[["event_no", "athlete_name", "fin_time"]]

    merged = day2.merge(
        manual_subset,
        left_on=["event_no", "athlete_name"],
        right_on=["event_no", "athlete_name"],
        suffixes=["_day2", "_manual"],
    )

    merged["time_diff"] = merged.fin_time_day2 - merged.fin_time_manual

    differences = merged[merged.time_diff != 0]
    differences = differences[
        [
            "event_name",
            "event_no",
            "fin_heat",
            "fin_lane",
            "athlete_name",
            "fin_time_day2",
            "fin_time_manual",
        ]
    ]
    differences.sort_values(["event_no", "fin_heat", "fin_lane"], inplace=True)
    print(differences)


if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(level=args.loglevel)
    # prepare(args.day1, args.day2)
    check(args.day2, args.manual)
