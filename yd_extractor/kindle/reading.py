from pathlib import Path
import shutil
import pandas as pd

from typing import BinaryIO, Union

from yd_extractor.utils.pandas import detect_delimiter, validate_columns
from yd_extractor.utils.utils import extract_specific_files_flat


def extract_reading(csv_file: BinaryIO):
    # Read in csv from config into a pandas dataframe
    df_raw = pd.read_csv(
        csv_file,
        delimiter=detect_delimiter(csv_file),
        parse_dates=["start_time", "end_time"],
    )
    return df_raw


def transform_reading(df: pd.DataFrame) -> pd.DataFrame:
    columns_to_keep = ["ASIN", "start_time", "total_reading_milliseconds"]
    validate_columns(df, columns_to_keep)
    df = df[columns_to_keep].copy()
    df = df.rename(columns={"ASIN": "asin"})
    df.loc[:, "date"] = pd.to_datetime(df["start_time"], format="ISO8601").dt.date
    df.loc[:, "start_time"] = pd.to_datetime(df["start_time"], format="ISO8601").dt.time
    df = df.groupby(["asin", "date"]).aggregate(
        {"start_time": "min", "total_reading_milliseconds": "sum"}
    ).reset_index()
    df["total_reading_minutes"] = df[
        "total_reading_milliseconds"
    ].apply(lambda x: round(x / (60 * 1000)))
    df = df.drop(columns=["total_reading_milliseconds"])
    df = df[df["total_reading_minutes"] >= 15]
    return df
    
    
def process_reading(
    inputs_folder: Path,
    zip_path: Path,
    cleanup: bool=True
) -> pd.DataFrame:
    """
    Read in kindle data from csv file.

    """
    kindle_search_prefix = (
        "Kindle.ReadingInsights"
        "/datasets"
        "/Kindle.reading-insights-sessions_with_adjustments"
        "/Kindle.reading-insights-sessions_with_adjustments.csv"
    )
    data_folder = inputs_folder / "kindle"
    extract_specific_files_flat(
        zip_file_path=zip_path,
        prefix=kindle_search_prefix,
        output_path=data_folder
    )
    csv_path = (
        data_folder 
        /"Kindle.reading-insights-sessions_with_adjustments.csv"
    )
    with open(csv_path) as csv:
        df_raw = extract_reading(csv)
        
    df_processed = transform_reading(df_raw)
    
    if cleanup:
        shutil.rmtree(data_folder)
    return df_processed


def is_valid_asin(asin: str) -> bool:
    """Checks if a given string is an ASIN code. Asin codes are made of 10 alphanumeric
    characters. They begin with "B0"

    Parameters
    ----------
    asin : str
        String to check

    Returns
    -------
    bool
        True if input is an asin code.
    """
    return (
        len(asin) == 10 and asin.isalnum() and asin.isupper() and asin.startswith("B0")
    )


def get_asin_image(asin: str) -> Union[str, None]:
    """Returns the image url associated with a given asin code. Returns None if not valid
    asin.

    Parameters
    ----------
    asin : str
        asin code.

    Returns
    -------
    str | None
        Returns asin image url if input is valid asin code. Otherwise returns None.
    """
    if not is_valid_asin(asin):
        return None
    return f"https://images.amazon.com/images/P/{asin}.jpg"
