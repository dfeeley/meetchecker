from .base import BaseChecker

from meetchecker.utils import approx_equals


class Checker(BaseChecker):
    def __init__(self, threshold=1.0, **kwargs):
        super().__init__(**kwargs)
        self.threshold = threshold
        self.n = 2

    def get_reason(self, row):
        return "".join(
            [
                f"Incorrectly used average ({row.fin_time:.2f}) of 2 electronic times ",
                f"({row.min_pad_time:.2f}, {row.max_pad_time:.2f}) that were far apart ",
                f"({row.pad_time_spread:.2f} secs). Instead you should check time sheets and pick whichever ",
                "electronic time looks better.",
            ]
        )

    def check(self, data):
        entry = data["entry"]
        return entry[
            (entry.fin_stat != "R")
            & (entry.fin_stat != "Q")
            & (entry.fin_heat != 0)
            & (entry.num_pad_times == 2)
            & (entry.pad_time_spread > self.threshold)
            & (
                approx_equals(
                    entry.fin_time, (entry["max_pad_time"] + entry["min_pad_time"]) / 2
                )
            )
        ]
