import io
import math
import pandas as pd
import pathlib
import subprocess
import tempfile

import numpy as np

STROKE = dict(
    A="Free",
    B="Back",
    C="Breast",
    D="Fly",
    E="IM",
)

COLUMNS = dict(
    athlete=[
        "Ath_no",
        "Last_name",
        "First_name",
        "Initial",
        "Ath_Sex",
        "Birth_date",
        "Reg_no",
        "Pref_name",
        "Team_no",
    ],
    team=["Team_no", "Team_abbr", "Team_name"],
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
    relay=[
        "Event_ptr",
        "Relay_no",
        "Team_no",
        "Team_ltr",
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
)


def get_data(mdb_filepath):
    tables = extract_tables_from_mdb(mdb_filepath)
    dump_tables(tables, pathlib.Path(tempfile.gettempdir()), overwrite=True)
    dataframes = tables_to_dataframes(tables)
    return post_process_dataframes(dataframes)


def get_data_from_csvs(path):
    tables = load_tables_from_csvs(path)
    dataframes = tables_to_dataframes(tables)
    return post_process_dataframes(dataframes)


def post_process_dataframes(dataframes):
    data = merge_tables(dataframes)
    entry = entry_calculated_fields(data["entry"])
    try:
        relay = relay_calculated_fields(data["relay"])
        # concat entry and relay
        data["entry"] = pd.concat([entry, relay], axis=0)
        del data["relay"]
    except ValueError:
        # if no relays, e.g. for time trials
        pass
    return data


def extract_tables_from_mdb(mdb_filepath):
    data = {}
    for table in COLUMNS.keys():
        cmd = ["mdb-export", mdb_filepath, table]
        data[table] = subprocess.check_output(cmd, encoding="utf-8")
    return data


def dump_tables(tables, output_path, overwrite=False):
    if (
        any((output_path / f"{table}.csv").exists() for table in tables)
        and overwrite is False
    ):
        raise ValueError(
            f"Cannot dump tables to {output_path} as file(s) already exist and would be overwritten"
        )
    for name, table_data in tables.items():
        with open(output_path / f"{name}.csv", "w") as f:
            f.write(table_data)


def tables_to_dataframes(tables):
    ret = {}
    for table_name, table_data in tables.items():
        df = pd.read_csv(
            io.StringIO(table_data),
            usecols=COLUMNS[table_name],
            converters={
                "Last_name": str.strip,
                "First_name": str.strip,
                "Pref_name": str.strip,
                "Team_name": str.strip,
                "Team_abbr": str.strip,
            },
        )
        ret[table_name] = df.rename(str.lower, axis="columns")
    return ret


def load_tables_from_csvs(path):
    data = {}
    for table_name in COLUMNS:
        path_to_csv = path / f"{table_name}.csv"
        with open(path_to_csv) as f:
            data[table_name] = f.read()
    return data


def calc_num_pad_times(row):
    values = [getattr(row, attr) for attr in ("fin_back1", "fin_back2", "fin_back3")]
    return len([v for v in values if v and not math.isnan(v)])


def calc_max_pad_time(row):
    values = [getattr(row, attr) for attr in ("fin_back1", "fin_back2", "fin_back3")]
    values = [v for v in values if v and not math.isnan(v)]
    return max(values) if values else math.nan


def calc_min_pad_time(row):
    values = [getattr(row, attr) for attr in ("fin_back1", "fin_back2", "fin_back3")]
    values = [v for v in values if v and not math.isnan(v)]
    return min(values) if values else math.nan


def calc_event_name(row):
    gender = "Boys" if row.event_sex == "B" else "Girls"
    age = f"{row.high_age}&U" if row.low_age == 0 else f"{row.low_age}-{row.high_age}"
    distance = str(int(row.event_dist))
    stroke = STROKE.get(row.event_stroke)
    if row.ind_rel == "R":
        if stroke == "IM":
            stroke = "Medley Relay"
        else:
            stroke = f"{stroke} Relay"
    return " ".join([gender, age, distance, stroke])


def calc_popped_by(row):
    if row.actualseed_time and row.fin_time:
        return row.actualseed_time - row.fin_time


def common_calculated_fields(dataframe):
    dataframe["event_name"] = dataframe.apply(calc_event_name, axis=1)
    dataframe["num_pad_times"] = dataframe.apply(calc_num_pad_times, axis=1)
    dataframe["max_pad_time"] = dataframe.apply(calc_max_pad_time, axis=1)
    dataframe["min_pad_time"] = dataframe.apply(calc_min_pad_time, axis=1)
    dataframe["pad_time_spread"] = dataframe["max_pad_time"] - dataframe["min_pad_time"]
    dataframe["popped_by"] = dataframe.apply(calc_popped_by, axis=1)
    dataframe["actualseed_time"] = dataframe["actualseed_time"].replace(0, math.nan)
    return dataframe


def relay_calculated_fields(dataframe):
    dataframe = common_calculated_fields(dataframe)
    dataframe["athlete_name"] = dataframe[["team_name", "team_ltr"]].agg(
        " - ".join, axis=1
    )
    return dataframe


def entry_calculated_fields(dataframe):
    dataframe = common_calculated_fields(dataframe)
    dataframe["pref_name"] = dataframe.pref_name.replace("", np.nan)
    dataframe["given_name"] = dataframe.pref_name.combine_first(dataframe.first_name)
    dataframe["athlete_name"] = dataframe[["last_name", "given_name"]].agg(
        ", ".join, axis=1
    )
    return dataframe


def merge_tables(data):
    time_standards = data["timestd"].merge(
        data["tagnames"], left_on="tag_ptr", right_on="tag_ptr"
    )
    records = data["records"].merge(
        data["recordtags"], left_on="tag_ptr", right_on="tag_ptr"
    )
    athlete = data["athlete"].merge(data["team"], left_on="team_no", right_on="team_no")
    entry = data["entry"].merge(athlete, left_on="ath_no", right_on="ath_no")
    relay = data["relay"].merge(data["team"], left_on="team_no", right_on="team_no")
    event = data["event"]
    relay = relay.merge(event, left_on="event_ptr", right_on="event_ptr")
    entry = entry.merge(event, left_on="event_ptr", right_on="event_ptr")
    return dict(
        athlete=athlete,
        entry=entry,
        relay=relay,
        time_standards=time_standards,
        records=records,
    )


def dump_and_load_table(mdb_filepath, table, columns):
    cmd = ["mdb-export", mdb_filepath, table]
    data = subprocess.check_output(cmd, encoding="utf-8")
    # with open(f"/tmp/{table}.csv", "w") as f:
    #     f.write(data)
    df = pd.read_csv(
        io.StringIO(data),
        usecols=columns,
        converters={
            "Last_name": str.strip,
            "First_name": str.strip,
            "Pref_name": str.strip,
            "Team_name": str.strip,
        },
    )
    return df.rename(str.lower, axis="columns")


def load_table_from_csv(folder, table, columns):
    with open(folder / f"{table}.csv", "r") as f:
        df = pd.read_csv(
            f,
            usecols=columns,
            converters={
                "Last_name": str.strip,
                "First_name": str.strip,
                "Team_name": str.strip,
            },
        )
        return df.rename(str.lower, axis="columns")
