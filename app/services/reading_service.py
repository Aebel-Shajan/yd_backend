import os
from app.models import ReadingActivity
from app.services.utils import add_activity_to_db
from app.config import Config
from yd_extractor.kindle.reading import process_reading
from werkzeug.datastructures import FileStorage
import pathlib

def process_kindle_zip(file: FileStorage):
    zip_path = pathlib.Path(os.path.join(Config.UPLOAD_FOLDER, file.filename))
    file.save(zip_path)
    df = process_reading(
        inputs_folder=pathlib.Path(Config.UPLOAD_FOLDER),
        zip_path=zip_path
    )
    
    df = df.fillna(value=0)
    
    duplicate_rows = 0
    rows = df.shape[0]
    for index, row in df.iterrows():
        new_activity = ReadingActivity(**row.to_dict())
        try:
            add_activity_to_db(new_activity, ReadingActivity)
        except ValueError:
            duplicate_rows += 1
    
    return {
        "message": (
            f"Added {rows - duplicate_rows} rows,"
            f" found {duplicate_rows} duplicate rows"
        )
    }
        