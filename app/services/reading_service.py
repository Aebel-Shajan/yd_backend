import os
from app.models import ReadingActivity
from app.services.utils import add_activities_df_to_db
from app.config import Config
from yd_extractor.kindle.reading import process_reading
from werkzeug.datastructures import FileStorage
import pathlib

def handle_kindle_zip(file: FileStorage):
    zip_path = pathlib.Path(os.path.join(Config.UPLOAD_FOLDER, file.filename))
    file.save(zip_path)
    df = process_reading(
        inputs_folder=pathlib.Path(Config.UPLOAD_FOLDER),
        zip_path=zip_path
    )
    output = add_activities_df_to_db(df, ReadingActivity)
    return output
