import io
import math
import pandas
import subprocess

STROKE = dict(
    A="Free",
    B="Back",
    C="Breast",
    D="Fly",
    E="IM",
)


columns = dict(
    athlete=["Ath_no", "Last_name", "First_name", "Team_no"],
    team=["Team_no", "Team_abbr"],
    event=[
        "Event_no",
        "Event_ptr",
        "Ind_rel",
        "Event_sex",
        "Event_gender",
        "Event_dist",
        "Event_stroke",
        "Low_age",
        "High_Age",
    ],
    entry=[
        "Event_ptr",
        "Ath_no",
        "ActualSeed_time",
        "Fin_heat",
        "Fin_lane",
        "Fin_stat",
        "Fin_Time",
        "Fin_heatplace",
        "Fin_back1",
        "Fin_back2",
        "Fin_back3",
        "Fin_pad",
        "fin_adjuststat",
    ],
    tagnames=[
        "tag_ptr",
        "tag_name",
    ],
    timestd=[
        "tag_ptr",
        "tag_gender",
        "tag_indrel",
        "tag_dist",
        "tag_stroke",
        "low_age",
        "high_Age",
        "tag_time",
    ],
    recordtags=[
        "tag_ptr",
        "tag_name",
    ],
    records=[
        "tag_ptr",
        "tag_gender",
        "tag_indrel",
        "tag_dist",
        "tag_stroke",
        "low_age",
        "high_Age",
        "Record_year",
        "Record_Holder",
        "Record_Holderteam",
        "Record_Time",
    ],
)


def get_data(mdb_filepath):
    data = {}
    for table in (
        "team",
        "event",
        "athlete",
        "entry",
        "tagnames",
        "timestd",
        "records",
        "recordtags",
    ):
        data[table] = dump_and_load_table(mdb_filepath, table, columns[table])
    data = merge_tables(data)
    data["entries"] = entries_calculated_fields(data["entries"])
    return data


def calc_num_pad_times(row):
    values = [getattr(row, attr) for attr in ("fin_back1", "fin_back2", "fin_back3")]
    return len([v for v in values if v and not math.isnan(v)])


def calc_event_name(row):
    gender = "Boys" if row.event_sex == "B" else "Girls"
    age = f"{row.high_age}&U" if row.low_age == 0 else f"{row.low_age}-{row.high_age}"
    distance = str(int(row.event_dist))
    stroke = STROKE.get(row.event_stroke)
    if row.ind_rel == "R" and stroke == "IM":
        stroke = "Medley Relay"
    return " ".join([gender, age, distance, stroke])


def calc_popped_by(row):
    if row.actualseed_time and row.fin_time and row.actualseed_time > row.fin_time:
        return row.actualseed_time - row.fin_time


def entries_calculated_fields(dataframe):
    dataframe["event_name"] = dataframe.apply(calc_event_name, axis=1)
    dataframe["num_pad_times"] = dataframe.apply(calc_num_pad_times, axis=1)
    dataframe["popped_by"] = dataframe.apply(calc_popped_by, axis=1)
    return dataframe


def merge_tables(data):
    time_standards = data["timestd"].merge(
        data["tagnames"], left_on="tag_ptr", right_on="tag_ptr"
    )
    records = data["records"].merge(
        data["recordtags"], left_on="tag_ptr", right_on="tag_ptr"
    )
    athlete = data["athlete"].merge(data["team"], left_on="team_no", right_on="team_no")
    entries = data["entry"].merge(athlete, left_on="ath_no", right_on="ath_no")
    event = data["event"]
    entries = entries.merge(event, left_on="event_ptr", right_on="event_ptr")
    return dict(
        entries=entries,
        time_standards=time_standards,
        records=records,
    )


def dump_and_load_table(mdb_filepath, table, columns):
    cmd = ["mdb-export", mdb_filepath, table]
    data = subprocess.check_output(cmd, encoding="utf-8")
    with open(f"/tmp/{table}.csv", "w") as f:
        f.write(data)
    df = pandas.read_csv(
        io.StringIO(data),
        usecols=columns,
        converters={"Last_name": str.strip, "First_name": str.strip},
    )
    return df.rename(str.lower, axis="columns")
