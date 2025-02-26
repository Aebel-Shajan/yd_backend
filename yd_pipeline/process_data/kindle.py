import pandas as pd
import sqlite3
from yd_pipeline.utils import (
    check_columns_exist,
    detect_delimiter,
)
from typing import BinaryIO, Union


def process_kindle_data(csv_file: BinaryIO):
    """
    Read in kindle data from csv file.
    Store fine grain data in year_in_data.kindle_data_fine_grain.
    Store daily data in year_in_data.kindle_data_daily.

    Parameters
    ----------
    csv_file : BinaryIO
        Csv file containing kindle activity data. Has the following columns:
        [ASIN,end_time,reading_marketplace,start_time,total_reading_milliseconds]
    """

    # Read in csv from config into a pandas dataframe
    kindle_df = pd.read_csv(
        csv_file,
        delimiter=detect_delimiter(csv_file),
        parse_dates=["start_time", "end_time"],
    )

    columns_to_keep = ["ASIN", "end_time", "start_time", "total_reading_milliseconds"]
    if not check_columns_exist(kindle_df, columns_to_keep):
        raise ValueError(
            "CSV provided does not contain required columns!\n"
            f"\t* CSV columns: {list(kindle_df.columns)}\n"
            f"\t* Required columns: {columns_to_keep}"
        )

    # Store fine grain data in seperate table for future use
    connection = sqlite3.connect("data/output/year_in_data.db")
    kindle_df.to_sql("kindle_data_fine_grain", connection, if_exists="replace")

    # For daily info
    daily_kindle_df = kindle_df[["ASIN", "start_time", "total_reading_milliseconds"]]
    daily_kindle_df = daily_kindle_df.rename(columns={
        "start_time": "date"
    })
    daily_kindle_df.loc[:, "date"] = pd.to_datetime(
        daily_kindle_df["date"], format="ISO8601"
    ).dt.date
    daily_kindle_df = daily_kindle_df.groupby(["ASIN", "date"]).sum()
    daily_kindle_df["total_reading_minutes"] = daily_kindle_df[
        "total_reading_milliseconds"
    ].apply(lambda x: round(x / (60 * 1000)))
    daily_kindle_df = daily_kindle_df.drop(columns=["total_reading_milliseconds"])
    daily_kindle_df = daily_kindle_df[daily_kindle_df["total_reading_minutes"] >= 15]
    daily_kindle_df.to_sql("kindle_data_daily", connection, if_exists="replace")


def get_distinct_books():
    """Create kindle_distinct_books table with columns
    ["ASIN", "latest_date", "total_reading_minutes", "book_image"]. The table contains
    all the books read.
    """
    connection = sqlite3.connect("data/output/year_in_data.db")
    cursor = connection.cursor()
    query = """
    SELECT 
        ASIN , 
        SUM(total_reading_minutes),
        MAX(date) as latest_date 
    FROM 
        kindle_data_daily 
    GROUP BY 
        ASIN
    ORDER BY 
        latest_date
    """
    distinct_items = cursor.execute(query).fetchall()
    distinct_items_df = pd.DataFrame(
        distinct_items, columns=["ASIN", "total_reading_minutes", "latest_date"]
    )
    distinct_items_df["book_image"] = distinct_items_df["ASIN"].apply(get_asin_image)
    distinct_items_df.to_sql("kindle_distinct_books", connection, if_exists="replace")


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
