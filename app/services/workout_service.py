from typing import BinaryIO
from app.models import WorkoutActivity
from app.services.utils import  add_activities_df_to_db
from yd_extractor.strong import process_workouts

    
def handle_strong_csv(csv_file: BinaryIO):
    df = process_workouts(csv_file)
    df = df.fillna(value=0)
    output = add_activities_df_to_db(df, WorkoutActivity)
    return output
