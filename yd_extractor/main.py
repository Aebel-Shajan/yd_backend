import logging
import os
from pathlib import Path

from dotenv import load_dotenv

import yd_extractor.fitbit as fitbit_extractor
import gdown
import shutil

from yd_extractor.utils.utils import extract_folder_from_zip, get_latest_file

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s -%(levelname)s -on line: %(lineno)d -%(message)s'
)
logger = logging.getLogger() 

config = {
    "download_from_drive": False,
    "process_strong": False,
    "process_github": False,
    "process_kindle": False,
    "fitbit_config": {
        "process_calories": True,
        "process_sleep": True,
        "process_steps": True,
    },
    "cleanup_unziped_files": True,
    "cleanup_ziped_files": False
}

if __name__ == "__main__":
    cleanup_ziped_files = config["cleanup_ziped_files"]
    cleanup_unziped_files = config["cleanup_unziped_files"]
    fitbit_config = config["fitbit_config"]
    
    logger.info("Loading environement variables...")
    load_dotenv()
    drive_url = os.getenv("DRIVE_SHARE_URL")
    github_token = os.getenv("GITHUB_TOKEN")
    if (drive_url is None):
        logger.warning("Couldn't find google drive share link")
    if (github_token is None):
        logger.warning("Couldn't find github token in .env!")
    
    root_dir = Path(__file__).resolve().parent.parent
    input_data_folder = root_dir / "data" / "input"
    output_data_folder = root_dir / "data" / "output"
    os.makedirs(input_data_folder, exist_ok=True)
    os.makedirs(root_dir/"data"/"output", exist_ok=True)
    logger.info(f"Inputs and output data will be stored here: {root_dir / 'data'}")
    
    if config["download_from_drive"]:
        if (drive_url is None):
            raise Exception("Expected DRIVE_SHARE_URL in .env folder!")
        logger.info("Downloading data from google drive...")
        gdown.download_folder(
            url=drive_url,
            output=str(input_data_folder.absolute()),
            use_cookies=False
        )
    
    if any(list(fitbit_config.values())):
        latest_google_zip = get_latest_file(
            folder_path=input_data_folder,
            file_name_glob="takeout*.zip"
        )
        fitbit_relative_folder = "Takeout/Fitbit/Global Export Data/"
        fitbit_absolute_path = input_data_folder / fitbit_relative_folder
        
        # Calories
        if fitbit_config["process_calories"]:
            extract_folder_from_zip(
                zip_file_path=latest_google_zip,
                prefix=fitbit_relative_folder + "calories",
                output_path=input_data_folder
            )
            df = fitbit_extractor.process_calories(fitbit_absolute_path)
            df.to_csv(output_data_folder / "fitbit_calories.csv")
            if cleanup_unziped_files:
                shutil.rmtree(fitbit_absolute_path)

        # Sleep
        if fitbit_config["process_sleep"]:
            extract_folder_from_zip(
                zip_file_path=latest_google_zip,
                prefix=fitbit_relative_folder + "sleep",
                output_path=input_data_folder
            )
            df = fitbit_extractor.process_sleep(fitbit_absolute_path)
            df.to_csv(output_data_folder / "fitbit_sleep.csv")
            if cleanup_unziped_files:
                shutil.rmtree(fitbit_absolute_path)
