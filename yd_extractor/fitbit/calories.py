import pandas as pd

from .utils import extract_json_file_data, transform_time_series_data


def process_calories(folder_path: str) -> pd.DataFrame:
    """Extract calories from folder then apply some transformations on data."""
    
    df_raw = extract_json_file_data(
        folder_path=folder_path,
        file_name_prefix="calories",
        keys_to_keep=["dateTime", "value"]
    )
    df_transformed = transform_time_series_data(df=df_raw)
    return df_transformed