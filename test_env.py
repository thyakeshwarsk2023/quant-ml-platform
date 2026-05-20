# test_env.py
from dotenv import load_dotenv
import os

load_dotenv()

print("DB URL:", os.getenv("DATABASE_URL"))