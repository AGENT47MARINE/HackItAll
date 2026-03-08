
from database import init_db
import logging

logging.basicConfig(level=logging.INFO)
try:
    print("Initializng database...")
    init_db()
    print("Database initialized successfully!")
except Exception as e:
    print(f"Error initializing database: {e}")
    import traceback
    traceback.print_exc()
