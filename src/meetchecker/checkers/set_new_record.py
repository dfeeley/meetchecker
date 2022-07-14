from .base import BaseChecker
from ..utils import emphasis as _


class Checker(BaseChecker):
    def __init__(self, record_name, **kwargs):
        super().__init__(**kwargs)
        self.record_name = record_name

    def get_reason(self, row):
        broke_record_by = row.record_time - row.fin_time
        broke_record_by_pct = 100 * broke_record_by / row.record_time
        return "".join(
            [
                f"Time of {row.fin_time:.2f} would break ",
                _(f"{self.record_name}"),
                f" record  of {row.record_time:.2f} by ",
                _(f"{broke_record_by:.2f} seconds / {broke_record_by_pct:.1f}%"),
            ]
        )

    def check(self, data):
        records = data["records"]
        records = records[records.tag_name == self.record_name]
        if len(records) == 0:
            raise ValueError(
                f"No timing data found for record with name {self.record_name!r}"
            )
        entry = data["entry"]
        entry = entry.merge(
            records,
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
            & (entry.fin_heat != 0)
            & (entry.fin_time <= entry.record_time)
        ]
