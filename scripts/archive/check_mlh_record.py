from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, title, source_url FROM opportunities WHERE title LIKE '%MLH Global Hack%'"))
        row = result.fetchone()
        if row:
            print(f"ID: {row[0]}")
            print(f"Title: {row[1]}")
            print(f"Source URL: {row[2]}")
        else:
            print("MLH Global Hack 2025 not found in DB.")
except Exception as e:
    print(f"Error: {e}")
