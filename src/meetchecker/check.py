import dataclasses


@dataclasses.dataclass
class CheckRecord:
    event_no: int
    fin_heat: int
    fin_lane: int
    event_name: str
    athlete_name: str
    team_abbr: str
    event_stroke: str
    event_dist: int
    actualseed_time: float
    num_pad_times: int
    fin_time: float
    fin_pad: float
    check_name: str
    reason: str

    @classmethod
    def from_records(cls, records):
        retv = []
        names = set([f.name for f in dataclasses.fields(cls)])
        for record in records:
            kwargs = {k: v for k, v in record.items() if k in names}
            retv.append(cls(**kwargs))
        return retv
