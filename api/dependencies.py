
from src.utils.database_manager import DatabaseManager

# Singleton
db_manager = DatabaseManager()

def get_db():
    return db_manager