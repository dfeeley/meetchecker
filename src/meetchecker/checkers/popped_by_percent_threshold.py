from .base import BaseChecker


class Checker(BaseChecker):
    def __init__(self, threshold=10, **kwargs):
        super().__init__(**kwargs)
        self.threshold = threshold

    def get_reason(self, row):
        pop_percent = 100 * row.popped_by / row.actualseed_time
        return (
            f"Time of {row.fin_time:.2f} compared to seed time of {row.actualseed_time:.2f} "
            f"is a pop of {row.popped_by:.2f} seconds / {pop_percent:.1f} percent"
        )

    def check(self, data):
        entries = data["entries"]
        return entries.loc[
            (entries.fin_stat != "R")
            & (entries.fin_stat != "Q")
            & (entries.popped_by > 0)
            & (100 * entries.popped_by / entries.actualseed_time >= self.threshold),
        ]
