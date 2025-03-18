import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOWED_EXTENSIONS = {"zip",  "csv"}
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__),  "data/input")
    def allowed_file(filename):
        return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS