from sqlalchemy import text
from database import engine

def migrate():
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE participation_history ADD COLUMN current_round VARCHAR(36) DEFAULT '1'"))
            print("Successfully added current_round column.")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("Column already exists.")
            else:
                print(f"Error: {e}")

if __name__ == "__main__":
    migrate()
