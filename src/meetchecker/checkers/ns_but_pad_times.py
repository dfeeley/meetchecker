from .base import BaseChecker


class Checker(BaseChecker):
    def get_reason(self, row):
        return f"NS but yet we got {row.num_pad_times} electronic time(s)"

    def check(self, data):
        entry = data["entry"]
        return entry.loc[
            ((entry.fin_stat == "R") | (entry.fin_heat != 0))
            & (entry.fin_stat != "Q")
            & (entry.num_pad_times > 0)
        ]
