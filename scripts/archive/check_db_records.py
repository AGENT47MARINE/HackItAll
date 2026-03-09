from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT count(*) FROM opportunities"))
        count = result.scalar()
        print(f"Total opportunities in DB: {count}")
        
        result = conn.execute(text("SELECT title FROM opportunities"))
        titles = [row[0] for row in result]
        print(f"Titles: {titles}")
except Exception as e:
    print(f"Error checking opportunities: {e}")
