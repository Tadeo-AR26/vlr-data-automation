import time
import random
from src.scrapers.tournament_scraper import TournamentScraper
from src.utils.database_manager import DatabaseManager
from src.utils.file_manager import save_json, load_json

def run_tournament_collection(ids_to_scrape, force_update=False):
    scraper = TournamentScraper()
    database = load_json('tournaments.json')
    print(f"Starting tournament collection for ID: {ids_to_scrape}")

    for tournament_id in ids_to_scrape:
        if tournament_id in database and not force_update:
            print(f"Tournament {tournament_id} already in database, skipping.")
            continue

        print(f"Scraping tournament {tournament_id}...")
        tournament_data = scraper.fetch_tournament(tournament_id)

        if tournament_data:
            database[tournament_id] = tournament_data
            save_json(database, 'tournaments.json')
            print(f"Tournament {tournament_id} data saved.")
        else:
            print(f"Failed to fetch data for tournament {tournament_id}.")

        wait_time = random.randint(3, 7)
        print(f"Waiting {wait_time}s...")
        time.sleep(wait_time)

def run_tournament_collection_db(ids_to_scrape, force_update=False):
    scraper = TournamentScraper()
    db = DatabaseManager()
    
    print(f"🚀 Starting DB tournament collection for IDs: {ids_to_scrape}")

    for t_id in ids_to_scrape:
        if not force_update and db.exists("tournaments", t_id):
            print(f"Tournament {t_id} already in database, skipping.")
            continue

        print(f"Scraping tournament {t_id}...")
        tournament_data = scraper.fetch_tournament(t_id)

        if tournament_data:
            db.save_tournament(t_id, tournament_data)
            print(f"Tournament {t_id} ({tournament_data.get('name')}) saved to SQLite.")
        else:
            print(f"Failed to fetch data for tournament {t_id}.")

        wait_time = random.randint(3, 7)
        print(f"Waiting {wait_time}s...")
        time.sleep(wait_time)

if __name__ == "__main__":
    # IDs de prueba (ej: Masters Santiago y torneos previos)
    master_ids = ["2760", "2682"]
    run_tournament_collection_db(master_ids, force_update=True)