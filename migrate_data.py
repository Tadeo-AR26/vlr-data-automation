import json
import os
from src.utils.database_manager import DatabaseManager

def migrate():
    db = DatabaseManager()
    data_dir = "data"

    migrations = [
        ("tournaments.json", db.save_tournament),
        ("teams.json", db.save_team),
        ("players.json", db.save_player),
        ("matches.json", db.save_match)
    ]

    for file_name, save_func in migrations:
        file_path = os.path.join(data_dir, file_name)
        
        if not os.path.exists(file_path):
            print(f"File {file_name} not found, skipping migration for this entity.")
            continue

        print(f"📦 Migrating {file_name}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            data_dict = json.load(f)

        for entity_id, entity_data in data_dict.items():
            if file_name == "matches.json":
                t_id = entity_data.get("tournament_id")
                save_func(entity_id, t_id, entity_data)
            else:
                save_func(entity_id, entity_data)

    print("Completed data migration to SQLite database.")

if __name__ == "__main__":
    migrate()