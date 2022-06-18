from .base import BaseChecker


class Checker(BaseChecker):
    def __init__(self, n=1, **kwargs):
        super().__init__(**kwargs)
        self.n = n

    def get_reason(self, row):
        return f"Only got {row.num_pad_times} electronic times"

    def check(self, data):
        entry = data["entry"]
        return entry[
            (entry.fin_stat != "R")
            & (entry.num_pad_times <= self.n)
            & (entry.num_pad_times > 0)
        ]
