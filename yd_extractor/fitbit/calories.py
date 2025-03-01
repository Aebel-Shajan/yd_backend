from pathlib import Path
import shutil
import pandas as pd

from yd_extractor.utils.utils import extract_specific_files_flat

from .utils import extract_json_file_data, transform_time_series_data


def process_calories(
    input_data_folder: Path,
    google_zip_path: Path,
    cleanup: bool=True
) -> pd.DataFrame:
    """Extract calories from folder then apply some transformations on data."""
    
    # Unzip and extract calories jsons from zip file.
    calories_folder = input_data_folder / "calories"
    extract_specific_files_flat(
        zip_file_path=google_zip_path,
        prefix="Takeout/Fitbit/Global Export Data/calories",
        output_path=calories_folder
    )
    df_raw = extract_json_file_data(
        folder_path=calories_folder,
        file_name_prefix="calories",
        keys_to_keep=["dateTime", "value"]
    )
    
    df_transformed = transform_time_series_data(df=df_raw)
    if cleanup:
        shutil.rmtree(calories_folder)
    return df_transformed