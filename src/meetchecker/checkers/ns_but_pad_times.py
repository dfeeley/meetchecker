from .base import BaseChecker


class Checker(BaseChecker):
    def __init__(self, num_times=1, **kwargs):
        super().__init__(**kwargs)
        self.num_times = num_times

    def get_reason(self, row):
        return f"NS but yet we got {row.num_pad_times} electronic time(s)"

    def check(self, data):
        entry = data["entry"]
        breakpoint()
        return entry.loc[
            ((entry.fin_stat == "R") | (entry.fin_heat == 0))
            & (entry.num_pad_times >= self.num_times)
        ]
