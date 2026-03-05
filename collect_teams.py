import time
import random
from src.scrapers.team_scraper import TeamScraper
from src.utils.file_manager import save_json, load_json

def run_team_collection(ids_to_scrape, force_update=False):
    scraper = TeamScraper()
    database = load_json('teams.json')
    print(f"Starting team collection for ID: {ids_to_scrape}")

    for t_id in ids_to_scrape:
        if t_id in database and not force_update:
            print(f"Team {t_id} already in database, skipping.")
            continue

        print(f"Scraping team {t_id}...")
        team_data = scraper.fetch_team(t_id)

        if team_data:
            database[t_id] = team_data
            save_json(database, 'teams.json')
            print(f"Team {t_id} data saved.")
        else:
            print(f"Failed to fetch data for team {t_id}.")
        
        wait_time = random.randint(3, 7)
        print(f"Waiting {wait_time}s...")
        time.sleep(wait_time)

if __name__ == "__main__":
    test_ids = ["1120", "624"] 
    run_team_collection(test_ids, force_update=True)