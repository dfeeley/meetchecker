from .base import BaseChecker
from ..utils import emphasis as _


class Checker(BaseChecker):
    def __init__(self, time_standard, **kwargs):
        super().__init__(**kwargs)
        self.time_standard = time_standard

    def get_reason(self, row):
        broke_standard_by = row.tag_time - row.fin_time
        broke_standard_by_pct = 100 * broke_standard_by / row.tag_time
        return "".join(
            [
                f"Time of {row.fin_time:.2f} popped by {row.popped_by:.2f} seconds and would break ",
                _(f"{self.time_standard}"),
                f" standard of {row.tag_time:.2f} by ",
                _(f"{broke_standard_by:.2f} seconds / {broke_standard_by_pct:.1f}%"),
            ]
        )

    def check(self, data):
        time_standards = data["time_standards"]
        time_standards = time_standards[time_standards.tag_name == self.time_standard]
        if len(time_standards) == 0:
            raise ValueError(f"No time standards found for {self.time_standard!r}")
        entry = data["entry"]
        entry = entry.merge(
            time_standards,
            left_on=[
                "event_gender",
                "ind_rel",
                "event_dist",
                "event_stroke",
                "low_age",
                "high_age",
            ],
            right_on=[
                "tag_gender",
                "tag_indrel",
                "tag_dist",
                "tag_stroke",
                "low_age",
                "high_age",
            ],
        )
        return entry.loc[
            (entry.fin_stat != "R")
            & (entry.fin_stat != "Q")
            & (entry.fin_heat != 0)
            & (entry.popped_by > 0)  # popped their time
            & (entry.fin_time <= entry.tag_time)  # reached the time standard
            & (
                entry.actualseed_time > entry.tag_time
            )  # had not previously reached the time standard
        ]
