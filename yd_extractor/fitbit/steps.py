import pandas as pd

from .utils import extract_json_file_data, transform_time_series_data


def process_steps(folder_path: str) -> pd.DataFrame:
    """Wrapper function for process fitbit steps data given folder containing steps
    data jsons.

    The function first extracts the data into a table then transforms it into another t
    able.

    Parameters
    ----------
    folder_path : str
        Path to folder containing step data json files.
    """
    df_raw = extract_json_file_data(
        folder_path=folder_path,
        file_name_prefix="steps",
        keys_to_keep=["dateTime", "value"]
    )
    df_transformed = transform_time_series_data(df_raw)
    return df_transformed
