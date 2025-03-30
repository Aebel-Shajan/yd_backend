import zipfile


def check_folder_exists_in_zip(zip_path: str, nested_folder_path: str):
    """
    Checks if a nested folder exists within a zip archive.

    Args:
        zip_path (str): The path to the zip archive.
        nested_folder_path (str): The path to the nested folder within the zip.

    Returns:
        bool: True if the nested folder exists, False otherwise.
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            # Add trailing slash to the nested_folder_path to ensure it's a directory
            nested_folder_path = nested_folder_path.rstrip('/') + '/'

            for file_info in zip_file.namelist():
                if file_info.startswith(nested_folder_path):
                    return True  # Found at least one file or folder within the nested folder
            return False  # No files or folders found with the specified prefix
    except FileNotFoundError:
        return False #Zip file not found
    except zipfile.BadZipFile:
        return False #File is not a zip file or is corrupted