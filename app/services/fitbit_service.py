
import os
import pathlib
from werkzeug.datastructures import FileStorage

from app.config import Config
from app.models import (
    CalorieActivity,
    ExerciseActivity,
    SleepActivity,
    StepActivity
)
from app.services.utils import add_activities_df_to_db
from yd_extractor.fitbit import (
    process_calories,
    process_exercise,
    process_sleep,
    process_steps
)

def handle_fitbit_zip(file: FileStorage):
    zip_path = pathlib.Path(os.path.join(Config.UPLOAD_FOLDER, file.filename))
    file.save(zip_path)
    full_output = {
        "message": ""
    }    

    df = process_calories(
        inputs_folder=pathlib.Path(Config.UPLOAD_FOLDER),
        zip_path=zip_path
    )
    df = df.fillna(value=0)
    output = add_activities_df_to_db(df, CalorieActivity)
    full_output["message"] += output["message"] + "\n"
    
    df = process_exercise(
        inputs_folder=pathlib.Path(Config.UPLOAD_FOLDER),
        zip_path=zip_path
    )
    df = df.fillna(value=0)
    output = add_activities_df_to_db(df, ExerciseActivity)
    full_output["message"] += output["message"] + "\n"
    
    df = process_sleep(
        inputs_folder=pathlib.Path(Config.UPLOAD_FOLDER),
        zip_path=zip_path
    )
    df = df.fillna(value=0)
    output = add_activities_df_to_db(df, SleepActivity)
    full_output["message"] += output["message"] + "\n"
    
    df = process_steps(
        inputs_folder=pathlib.Path(Config.UPLOAD_FOLDER),
        zip_path=zip_path
    )
    df = df.fillna(value=0)
    output = add_activities_df_to_db(df, StepActivity)
    full_output["message"] += output["message"] + "\n"
    

    return full_output
