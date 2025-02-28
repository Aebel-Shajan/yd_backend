import pandas as pd

from yd_extractor.utils.utils import validate_columns

from .utils import extract_json_file_data


def extract_sleep(folder_path: str) -> pd.DataFrame:
    """Extract sleep data from files from the folder path. The files have the name format
    "sleep-YYYY-MM-DD.json".

    Parameters
    ----------
    folder_path : str
        Path to folder containing jsons with sleep data.
    """
    keys_to_keep = [
        "logId",
        "dateOfSleep",
        "startTime",
        "endTime",
        "duration",
        "minutesToFallAsleep",
        "minutesAsleep",
        "minutesAwake",
        "minutesAfterWakeup",
        "timeInBed",
        "efficiency",
    ]
    df_sleep_raw = extract_json_file_data(
        folder_path,
        file_name_prefix="sleep",
        keys_to_keep=keys_to_keep
    )
    return df_sleep_raw
    
# no standardise 😔
def transform_sleep(df: pd.DataFrame) -> pd.DataFrame:
    """Apply transformations to sleep dataframe, then saves dataframe in table:
    `year_in_data.fitbit_sleep_data_processed`

    Parameters
    ----------
    sleep_df : pd.DataFrame
        Raw Fibit sleep dataframe containing columns:
            `["dateOfSleep", "startTime", "endTime", "duration"]`

    """
    # Select only important data for current analysis
    columns_to_keep = ["dateOfSleep", "startTime", "endTime", "duration"]
    validate_columns(df, columns_to_keep)
    df = df[columns_to_keep]
    df = df.rename(
        columns={
            "dateOfSleep": "date",
            "startTime": "start_time",
            "endTime": "end_time",
            "duration": "total_duration",
        }
    )
    df["total_duration_hours"] = df["total_duration"].apply(
        lambda x: round(x / (1000 * 60 * 60), 2)
    )
    df = df.drop(columns=["total_duration"])
    df.loc[:, "date"] = pd.to_datetime(df["date"]).dt.date
    df.loc[:, "start_time"] = pd.to_datetime(df["start_time"]).dt.time
    df.loc[:, "end_time"] = pd.to_datetime(df["end_time"]).dt.time
    df = df.groupby(["date"]).aggregate(
        {"start_time": "min", "end_time": "max", "total_duration_hours": "sum"}
    )
    return df


def process_sleep(folder_path: str) -> pd.DataFrame:
    df_raw = extract_sleep(folder_path)
    df_standardized = transform_sleep(df_raw)
    return df_standardized