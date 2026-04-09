import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    user = os.getenv("DB_USER")
    password = quote_plus(os.getenv("DB_PASSWORD"))
    host = os.getenv("DB_HOST")
    db = os.getenv("DB_NAME")

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{user}:{password}@{host}/{db}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
