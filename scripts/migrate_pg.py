import sys
import os
from sqlalchemy import text

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, SessionLocal

def migrate():
    db = SessionLocal()
    try:
        print("🚀 Running migrations for PostgreSQL...")
        
        # Add timeline column
        try:
            db.execute(text("ALTER TABLE opportunities ADD COLUMN timeline TEXT DEFAULT '[]'"))
            db.commit()
            print("✅ Added 'timeline' column.")
        except Exception as e:
            db.rollback()
            print(f"ℹ️ 'timeline' column might already exist: {e}")
            
        # Add prizes column
        try:
            db.execute(text("ALTER TABLE opportunities ADD COLUMN prizes TEXT DEFAULT '[]'"))
            db.commit()
            print("✅ Added 'prizes' column.")
        except Exception as e:
            db.rollback()
            print(f"ℹ️ 'prizes' column might already exist: {e}")
            
        print("✨ Migration completed!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
