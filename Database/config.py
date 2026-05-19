import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_NAME = os.getenv("DATABASE_NAME", "expense_tracker.db")
DEBUG = os.getenv("DEBUG", "True") == "True"