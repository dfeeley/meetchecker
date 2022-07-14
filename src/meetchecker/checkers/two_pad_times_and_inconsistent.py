from .base import BaseChecker
from ..utils import emphasis as _


class Checker(BaseChecker):
    def __init__(self, threshold=0.3, **kwargs):
        super().__init__(**kwargs)
        self.threshold = threshold

    def get_reason(self, row):
        return "".join(
            [
                "Only got 2 electronic times and they were ",
                _(f"{row.pad_time_spread:.2f} seconds"),
                f" apart (which is more than our threshold of {self.threshold:.2f} seconds)",
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
        ]
