import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from sqlalchemy import text
import sys

def check_schema():
    db = SessionLocal()
    try:
        print("--- CHECKING DB SCHEMA ---")
        
        # Check users table
        print("\n[Users Table Columns]")
        res = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='users'"))
        cols = [r[0] for r in res]
        print(cols)
        
        # Check if any users exist
        print("\n[Existing Users]")
        res = db.execute(text("SELECT id FROM users LIMIT 5"))
        users = [r[0] for r in res]
        print(users)
        
        # Check teams table
        print("\n[Teams Table Columns]")
        res = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='teams'"))
        cols = [r[0] for r in res]
        print(cols)

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_schema()
