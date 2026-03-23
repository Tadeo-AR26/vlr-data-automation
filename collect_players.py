import time
import random
from src.scrapers.player_scraper import PlayerScraper
from src.utils.database_manager import DatabaseManager
from src.utils.file_manager import save_json, load_json

def run_player_collection(ids_to_scrape):
    scraper = PlayerScraper()
    database = load_json('players.json')
    print(f"Starting player collection for ID: {ids_to_scrape}")

    for p_id in ids_to_scrape:
        # if p_id in database:
            # print(f"Player {p_id} already in database, skipping.")
            # continue
        print(f"Scraping player {p_id}...")
        player_data = scraper.fetch_player(p_id)
        
        if player_data:
            database[p_id] = player_data
            save_json(database, 'players.json')
            print(f"Player {p_id} data saved.")
        else:
            print(f"Failed to fetch data for player {p_id}.")

        # Sleep to avoid hitting rate limits
        wait_time = random.randint(3, 7) 
        print(f"Waiting {wait_time}s...")
        time.sleep(wait_time)

def run_player_collection_db(ids_to_scrape, force_update=False):
    scraper = PlayerScraper()
    db = DatabaseManager() #
    
    print(f"Starting DB player collection for IDs: {ids_to_scrape}")

    for p_id in ids_to_scrape:
        if not force_update and db.exists("players", p_id):
            print(f"Player {p_id} already in database, skipping.")
            continue

        print(f"Scraping player {p_id}...")
        player_data = scraper.fetch_player(p_id)
        
        if player_data:
            db.save_player(p_id, player_data)
            print(f"Player {p_id} ({player_data.get('ign')}) saved to SQLite.")
        else:
            print(f"Failed to fetch data for player {p_id}.")

        wait_time = random.randint(3, 7)
        print(f"Waiting {wait_time}s...")
        time.sleep(wait_time)

if __name__ == "__main__":
    test_ids = ["3017", "11624"] 
    run_player_collection(test_ids)