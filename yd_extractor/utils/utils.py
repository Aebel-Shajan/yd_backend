import csv
import json
import logging
import os
import sqlite3
import zipfile
from pathlib import Path
from typing import BinaryIO

import pandas as pd

# Setup logger
logger = logging.getLogger(__name__)


def parse_duration(duration: str) -> float:
    """Convert duration from the format `{hours}h {minutes}m` to milliseconds

    Parameters
    ----------
    duration : str
        Duration string in one of the formats:
            * `{hours}h {minutes}m`
            * `{hours}h`
            * `{minutes}m`

    Returns
    -------
    duration_ms : float
        Duration in milliseconds
    """

    def throw_error():
        raise ValueError("duration must have type like `{hours}h {minutes}m`")

    duration_ms = 0
    parts = duration.split()
    # Validation
    if len(parts) > 2 or len(parts) == 0:
        throw_error()
    for part in parts:
        if not part[:-1].isnumeric():
            throw_error()
        if not (part.endswith("h") or part.endswith("m")):
            throw_error()

    for index, part in enumerate(parts):
        if part.endswith("h") and index == 0:
            hours = part.rstrip("h")
            duration_ms += float(hours) * 60 * 60 * 1000
        elif part.endswith("m"):
            minutes = part.rstrip("m")
            duration_ms += float(minutes) * 60 * 1000

    return duration_ms


def check_columns_exist(df: pd.DataFrame, columns: list[str]) -> bool:
    """Checks if a given dataframe contains the provided columns.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to check columns.
    columns : list[str]
        Columns to check.

    Returns
    -------
    bool
        True if dataframe contains all columns provided. False otherwise.
    """
    return set(columns).issubset(df.columns)


def validate_columns(df: pd.DataFrame, columns_to_validate: list[str]) -> None:
    if not set(df.columns).issubset(df.columns):
        raise ValueError(
            "df provided does not contain required columns!\n"
            f"\t* df columns: {list(df.columns)}\n"
            f"\t* Required columns: {columns_to_validate}"
        )


def detect_delimiter(csv_file: BinaryIO) -> str:
    """
    Detect the delimiter used in a CSV file.

    Parameters
    ----------
    csv_file : BinaryIO
        The path to the CSV file.

    Returns
    -------
    str
        The detected delimiter (e.g. ',', ';', '\t', etc.).
    """
    original_pos = csv_file.tell()
    dialect = csv.Sniffer().sniff(csv_file.read(1024))
    csv_file.seek(original_pos)
    return dialect.delimiter


def load_graphql_query(file_path: str) -> str:
    """
    Load a GraphQL query from a file.

    Parameters
    ----------
    file_path : str
        The path to the file containing the GraphQL query.

    Returns
    -------
    str
        The GraphQL query as a string.
    """
    with open(file_path, "r") as file:
        query = file.read()
    return query


def write_db_to_jsons(db_path: str, output_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table_name in tables:
        table_name = table_name[0]
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]

        # Convert to list of dictionaries
        data = [dict(zip(columns, row)) for row in rows]

        # Write to JSON file
        with open(f"{output_path}/{table_name}.json", "w") as json_file:
            json.dump(data, json_file, indent=4)

    conn.close()


def get_latest_file(folder_path: Path, file_name_glob: str) -> Path:
    """Gets the latest file matching the glob pattern in the specified folder.

    Args:
        folder_path (Path): Path where desired file is.
        file_name_glob (str): Name/pattern the file matches.

    Raises:
        FileNotFoundError: Raise if folder_path does not exist.
        FileNotFoundError: Raised if no files found in provided folder path.

    Returns:
        Path: The path to the latest file.
    """
    if not os.path.exists(folder_path):
        error_message = f"Provided folder path {folder_path} does not exist."
        logger.error(error_message)
        raise FileNotFoundError(error_message)

    files = list(folder_path.glob(file_name_glob))
    if len(files) == 0:
        error_message = (
            f"No files found in {folder_path}, that matches glob {file_name_glob}"
        )
        logger.error(error_message)
        raise FileNotFoundError(error_message)

    # Search for most recent file
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


def unzip_file(zip_file_path: Path, output_path: Path):
    """Unzips the specified zip file into the specified output folder.

    Args:
        zip_file_path (Path): Path to the zip file.
        output_path (Path): The output folder path to unzip to.
    """
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        logger.info(f"Extracting zip file: {zip_file_path} into {output_path}")
        zip_ref.extractall(output_path)




def extract_folder_from_zip(zip_file_path: Path, prefix: str, output_path: Path):
    """Extractrs specific folder from zip file.

    Args:
        zip_file_path (Path): Path to the zip file.
        prefix (str): Relative name of folder/files in zip file.
        output_path (Path): The output folder path to unzip to.
    """
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        # Get a list of files in the ZIP archive
        all_files = zip_ref.namelist()

        # Filter only files inside the specific folder
        folder_files = [f for f in all_files if f.startswith(prefix)]

        # Extract only the filtered files
        for file in folder_files:
            zip_ref.extract(file, output_path)

def extract_specific_files_flat(zip_file_path: Path, prefix: str, output_path: Path):
    """
    Extracts specific files which have the same prefix from a ZIP archive and saves 
    them to the given output directory without preserving their original folder 
    structure.

    Args:
        zip_file_path (Path): Path to zip file.
        prefix (str): Prefix of files we want to extract.
        output_path (Path): Output directory to save the files to.
    """
    # Ensure the output directory exists
    os.makedirs(output_path, exist_ok=True)

    # Open the ZIP file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
       
        for file_name in zip_ref.namelist():
            if file_name.startswith(prefix):
                # Extract the file to a temp location
                with zip_ref.open(file_name) as source_file:
                    # Get only the filename, ignoring directories
                    file_name = os.path.basename(file_name)
                    out_file_path = os.path.join(output_path, file_name)
                    
                    # Write the extracted file to the output directory
                    with open(out_file_path, "wb") as output_file:
                        output_file.write(source_file.read())

    