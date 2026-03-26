import time
import random
from src.scrapers.home_scraper import HomeScraper
from src.scrapers.match_scraper import MatchScraper
from src.scrapers.player_scraper import PlayerScraper
from src.scrapers.team_scraper import TeamScraper
from src.utils.database_manager import DatabaseManager

def sync_vlr_data_db():
    db = DatabaseManager()
    home_scraper = HomeScraper()
    match_scraper = MatchScraper()
    player_scraper = PlayerScraper()
    team_scraper = TeamScraper()

    print("Starting synchronization process...")
    activity = home_scraper.fetch_home()
    
    if not activity:
        print("Error: Could not fetch home page data. Sync aborted.")
        return

    recent_ids = activity.get("recent_matches", [])
    print(f"Detected {len(recent_ids)} recent matches to verify.")

    for match_id in recent_ids:
        if db.exists("matches", match_id):
            print(f"Match {match_id} already exists in the database. Skipping.")
            continue

        print(f"Fetching match data for {match_id}...")
        match_data = match_scraper.fetch_match(match_id)
        if not match_data:
            continue
        
        t_id = match_data.get("tournament_id")
        db.save_match(match_id, t_id, match_data)
        print(f"Match {match_id} saved.")

        team_ids = [t['id'] for t in match_data.get("teams", []) if t.get('id')]
        for t_id in team_ids:
            if not db.exists("teams", t_id):
                print(f"Fetching team data for {t_id}...")
                t_data = team_scraper.fetch_team(t_id)
                if t_data:
                    db.save_team(t_id, t_data)
                time.sleep(random.randint(5, 8))
        
        players_to_update = {p["player_id"] for map_info in match_data.get("performance_by_map", []) 
                             for p in map_info.get("players", [])}
        
        for player_id in players_to_update:
            if not db.exists("players", player_id):
                print(f"Fetching player data for {player_id}...")
                player_data = player_scraper.fetch_player(player_id)
                if player_data:
                    db.save_player(player_id, player_data)
                time.sleep(random.randint(3, 6))

        time.sleep(random.randint(6, 10))
    
    print("Synchronization completed.")

def run_sync():
    """Punto de entrada para APScheduler o ejecución manual."""
    sync_vlr_data_db()

if __name__ == "__main__":
    run_sync()