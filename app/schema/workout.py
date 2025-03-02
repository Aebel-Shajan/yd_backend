from pydantic import BaseModel, PastDate


class WorkoutSchema(BaseModel):
    date: PastDate
    name: str
    exercise: str

    class Config:
        from_attributes = True