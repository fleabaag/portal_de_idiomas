import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    user = os.getenv("DB_USER")
    password = quote_plus(os.getenv("DB_PASSWORD"))
    host = os.getenv("DB_HOST")
    db = os.getenv("DB_NAME")

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{user}:{password}@{host}/{db}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "instance", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
