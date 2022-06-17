from .base import BaseChecker


class Checker(BaseChecker):
    def __init__(self, time_standard, **kwargs):
        super().__init__(**kwargs)
        self.time_standard = time_standard

    def get_reason(self, row):
        broke_standard_by = row.tag_time - row.fin_time
        broke_standard_by_pct = 100 * broke_standard_by / row.tag_time
        return (
            f"Time of {row.fin_time:.2f} would break {self.time_standard} standard of {row.tag_time:.2f} "
            f"by {broke_standard_by:.2f} seconds / {broke_standard_by_pct:.1f} percent"
        )

    def check(self, data):
        time_standards = data["time_standards"]
        time_standards = time_standards[time_standards.tag_name == self.time_standard]
        if len(time_standards) == 0:
            raise ValueError(f"No time standards found for {self.time_standard!r}")
        entries = data["entries"]
        entries = entries.merge(
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
        return entries.loc[
            (entries.fin_stat != "R")
            & (entries.fin_heat != 0)
            & (entries.fin_time <= entries.tag_time)
        ]
