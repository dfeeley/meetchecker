from .base import BaseChecker


class Checker(BaseChecker):
    def __init__(self, threshold=0.3, **kwargs):
        super().__init__(**kwargs)
        self.threshold = threshold

    def get_reason(self, row):
        return (
            f"Only got 2 electronic times and they were {row.pad_time_spread:.2f} (which is more than "
            f"our threshold of {self.threshold:.2f}) apart"
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
