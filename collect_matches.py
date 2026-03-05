import time
import random
from src.scrapers.match_scraper import MatchScraper
from src.utils.file_manager import save_json, load_json

def run_match_collection(ids_to_scrape, force_update=False):
    scraper = MatchScraper()
    database = load_json('matches.json')
    print(f"Starting match collection for ID: {ids_to_scrape}")

    for match_id in ids_to_scrape:
        if match_id in database and not force_update:
            print(f"Match {match_id} already in database, skipping.")
            continue

        print(f"Scraping match {match_id}...")
        match_data = scraper.fetch_match(match_id)

        if match_data:
            database[match_id] = match_data
            save_json(database, 'matches.json')
            print(f"Match {match_id} data saved.")
        else:
            print(f"Failed to fetch data for match {match_id}.")

        wait_time = random.randint(3, 7)
        print(f"Waiting {wait_time}s...")
        time.sleep(wait_time)

if __name__ == "__main__":
    # M8 vs EDG Masters Santiago
    match_list = ["625788"] 
    
    run_match_collection(match_list, force_update=True)