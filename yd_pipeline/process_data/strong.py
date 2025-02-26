import pandas as pd
import sqlite3
from yd_pipeline.utils import (
    check_columns_exist,
    parse_duration,
    detect_delimiter,
)
from typing import BinaryIO


def process_strong_data(csv_file: BinaryIO):
    """Read in the strong csv from the filepath.

    Parameters
    ----------
    csv_file : BinaryIO
        Csv file containing strong data
    """
    # Read in csv from config into a pandas dataframe
    strong_df = pd.read_csv(
        csv_file, delimiter=detect_delimiter(csv_file), parse_dates=["Date"]
    )

    # The strong app has 2 different formats with different column names
    if "Duration" in strong_df:
        strong_df = strong_df.rename(columns={"Duration": "Workout Duration"})

    columns_to_keep = [
        "Date",
        "Workout Name",
        "Exercise Name",
        "Set Order",
        "Weight",
        "Reps",
        "Distance",
        "Seconds",
        "Notes",
        "Workout Duration",
    ]
    if not check_columns_exist(strong_df, columns_to_keep):
        raise ValueError("CSV provided does not contain required columns.")

    # Select only columns to keep
    strong_df = strong_df[columns_to_keep]
    rename_map = {
        "Date": "date",
        "Workout Name": "workout_name",
        "Exercise Name": "exercise_name",
        "Set Order": "set_order",
        "Weight": "weight",
        "Reps": "reps",
        "Distance": "distance",
        "Seconds": "seconds",
        "Notes": "notes",
        "Workout Duration": "workout_duration",
    }
    strong_df = strong_df.rename(columns=rename_map)

    # Parse durations to milliseconds
    strong_df["workout_duration_milliseconds"] = strong_df["workout_duration"].apply(
        parse_duration
    )
    strong_df.drop(columns=["workout_duration"])

    # Calculate volume for each workout
    strong_df["volume"] = strong_df["weight"] * strong_df["reps"]

    # Store fine grain data in seperate table for future use
    connection = sqlite3.connect("data/output/year_in_data.db")
    strong_df.to_sql("workout_data_fine_grain", connection, if_exists="replace")

    # For daily info
    daily_columns = [
        "date",
        "workout_name",
        "exercise_name",
        "workout_duration_milliseconds",
        "set_order",
        "volume",
    ]
    daily_strong_df = strong_df[daily_columns]
    daily_strong_df.loc[:, "date"] = pd.to_datetime(
        daily_strong_df["date"], format="ISO8601"
    ).dt.date
    daily_strong_df = daily_strong_df.groupby(
        ["date", "workout_name", "exercise_name"]
    ).aggregate(
        {"workout_duration_milliseconds": "min", "volume": "sum", "set_order": "max"}
    )
    daily_strong_df = daily_strong_df.rename(columns={"set_order": "total_sets"})
    daily_strong_df["workout_duration_minutes"] = daily_strong_df[
        "workout_duration_milliseconds"
    ].apply(lambda x: x / (60 * 1000))
    daily_strong_df = daily_strong_df.drop(columns=["workout_duration_milliseconds"])
    daily_strong_df.to_sql("workout_data_daily", connection, if_exists="replace")


def get_distinct_workouts():
    """Create workout_distinct_workouts table."""
    connection = sqlite3.connect("data/output/year_in_data.db")
    cursor = connection.cursor()
    query = """
    SELECT 
        workout_name , 
        MAX(date) as latest_date 
    FROM 
        workout_data_daily 
    GROUP BY 
        workout_name
    ORDER BY 
        latest_date DESC
    """
    distinct_items = cursor.execute(query).fetchall()
    distinct_items_df = pd.DataFrame(
        distinct_items, columns=["workout_name", "latest_date"]
    )
    distinct_items_df.to_sql(
        "workout_distinct_workouts", connection, if_exists="replace"
    )


def get_distinct_exercises():
    """Create workout_distinct_exercises table."""
    connection = sqlite3.connect("data/output/year_in_data.db")
    cursor = connection.cursor()
    query = """
    SELECT 
        exercise_name , 
        MAX(date) as latest_date
    FROM 
        workout_data_daily 
    GROUP BY 
        exercise_name
    ORDER BY 
        latest_date DESC
    """
    distinct_items = cursor.execute(query).fetchall()
    distinct_items_df = pd.DataFrame(
        distinct_items, columns=["exercise_name", "latest_date"]
    )
    distinct_items_df.to_sql(
        "workout_distinct_exercises", connection, if_exists="replace"
    )
