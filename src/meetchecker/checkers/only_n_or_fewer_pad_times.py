from .base import BaseChecker


class Checker(BaseChecker):
    def __init__(self, n=1, **kwargs):
        super().__init__(**kwargs)
        self.n = n

    def get_reason(self, row):
        return f"Only got {row.num_pad_times} electronic times"

    def check(self, data):
        entries = data["entries"]
        return entries[
            (entries.fin_stat != "R")
            & (entries.num_pad_times <= self.n)
            & (entries.num_pad_times > 0)
        ]
