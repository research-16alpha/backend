
from dotenv import load_dotenv
import os

if os.getenv("ENV") != "production":
    load_dotenv()


class Settings:
    MONGODB_URI = os.getenv("MONGODB_URI")
    DATABASE_NAME = os.getenv("DATABASE_NAME")
    OUTLOOK_USER = os.getenv("OUTLOOK_USER")
    OUTLOOK_PASSWORD = os.getenv("OUTLOOK_PASSWORD")
settings = Settings()
