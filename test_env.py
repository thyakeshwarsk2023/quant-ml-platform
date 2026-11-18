# test_env.py
from dotenv import load_dotenv
import os
import re

load_dotenv()

url = os.getenv("DATABASE_URL", "")
masked = re.sub(r"://([^:]+):([^@]+)@", r"://\1:******@", url) if url else "(not set)"
print("DB URL:", masked)