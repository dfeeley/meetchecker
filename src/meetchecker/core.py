from collections import defaultdict, namedtuple
import importlib
import itertools
import logging
from operator import attrgetter
import pathlib

from meetchecker.datasourcing import get_data
from meetchecker.check import CheckRecord
from meetchecker.checkers.base import BaseChecker
from meetchecker.report import create_html_report
from meetchecker.color_wheel import ColorWheel

logger = logging.getLogger(__name__)


NameReasonColor = namedtuple("NameReason", "name reason color")


class LaneResult:
    def __init__(self):
        self._result = None
        self.name_reasons = []

    def accumulate(self, check_result):
        if self._result is None:
            self._result = check_result
        self.name_reasons.append(
            NameReasonColor(
                check_result.check_name, check_result.reason, check_result.color
            )
        )

    def num_exceptions(self):
        return len(self.name_reasons)

    def checks_as_str(self):
        return "\n".join([f"    * {nr.name}: {nr.reason}" for nr in self.name_reasons])

    def __getattr__(self, attr):
        return getattr(self._result, attr)


def accumulate_checks_by_lane(check_results):
    accumulated = defaultdict(LaneResult)
    key_fn = attrgetter("event_no", "fin_heat", "fin_lane")
    for result in check_results:
        key = key_fn(result)
        accumulated[key].accumulate(result)
    return accumulated


def sort_results_normal(record):
    return (record.event_no, record.fin_heat, record.fin_lane)


def sort_results_reversed(record):
    return (-record.event_no, record.fin_heat, record.fin_lane)


def get_checker(name, config):
    checker_module = config["checker"]
    try:
        module = importlib.import_module(checker_module)
        params = config.get("params") or {}
        cls = getattr(module, "Checker")
        if issubclass(cls, BaseChecker):
            return cls(name=name, **params)
        logger.error(f"{cls} is not a subclass of BaseChecker")
    except (ModuleNotFoundError,):
        logger.error(f"Module {checker_module!r} not found for check name {name!r}")
    except (AttributeError,):
        logger.error(f"No Checker class defined in module {checker_module!r}")


def console_output(lane_results):
    for event_no, event_records_iter in itertools.groupby(
        lane_results, key=attrgetter("event_no")
    ):
        event_records = list(event_records_iter)
        print(f"\nEvent {event_records[0].event_no}: {event_records[0].event_name}")

        for fin_heat, heat_records_iter in itertools.groupby(
            event_records, key=attrgetter("fin_heat")
        ):
            heat_records = list(heat_records_iter)
            print(f"Heat: {heat_records[0].fin_heat}")

            for lane_result in heat_records:
                print(f"  Lane {lane_result.fin_lane} {lane_result.athlete_name}")
                print(lane_result.checks_as_str())


def run_checks(data, checks):
    results = []
    color_wheel = ColorWheel.from_checks(checks)
    for name, check_config in checks.items():
        if not check_config.get("run", True):
            logger.info(f"{name!r} is set not to run, skipping it")
            continue

        checker = get_checker(name, check_config)
        if checker.color is None:
            checker.color = next(color_wheel)
        if not checker:
            continue
        try:
            these_results = checker.run(data)
            if these_results is None:
                logger.info(f"Check: {name}, no results!")
                continue
            adapted = CheckRecord.from_records(
                these_results.to_dict(orient="records"), color=checker.color
            )
            logger.info(f"Check: {name}, {len(adapted)} results")
            results.extend(adapted)
        except (ValueError,) as ex:
            logger.error(f"Failed to run checker {name} with exception: {ex}")
    return results


def run(mdb_file, output_file, checks, console_output=False):
    data = get_data(mdb_file)

    check_results = run_checks(data, checks)

    lane_results = list(accumulate_checks_by_lane(check_results).values())

    lane_results.sort(key=sort_results_normal)
    output = pathlib.Path(output_file)
    create_html_report(lane_results, meetfile=mdb_file, output=output)

    if console_output:
        console_output(lane_results)

    # also output results in event-reversed order so that auto refresh puts latest results on top
    lane_results.sort(key=sort_results_reversed)
    reversed_output = output.parent / f"{output.stem}_rev{output.suffix}"
    create_html_report(lane_results, meetfile=mdb_file, output=reversed_output)
