import time
import random
from src.scrapers.home_scraper import HomeScraper
from src.scrapers.match_scraper import MatchScraper
from src.scrapers.tournament_scraper import TournamentScraper
from src.scrapers.player_scraper import PlayerScraper
from src.scrapers.team_scraper import TeamScraper
from src.utils.file_manager import save_json, load_json

def sync_vlr_data():
    home_scraper = HomeScraper()
    match_scraper = MatchScraper()
    player_scraper = PlayerScraper()
    team_scraper = TeamScraper()

    activity = home_scraper.fetch_home()
    recent_ids = activity.get("recent_matches", [])
    print(f"Detected {len(recent_ids)} recent matches in Home.")
    if not activity:
        print("Failed to fetch recent activity.")
        return

    matches_db = load_json('matches.json')
    players_db = load_json('players.json')
    teams_db = load_json('teams.json')

    recent_ids = activity.get("recent_matches", [])

    for match_id in recent_ids:
        if match_id in matches_db:
            print(f"Match {match_id} already in database, skipping.")
            continue

        match_data = match_scraper.fetch_match(match_id)
        if not match_data:
            print(f"Failed to fetch data for match {match_id}.")
            continue
        
        matches_db[match_id] = match_data
        save_json(matches_db, 'matches.json')
        print(f"Match {match_id} data saved.")

        team_ids = [t['id'] for t in match_data.get("teams", []) if t.get('id')]
        for t_id in team_ids:
            print(f"Synchronizing Team {t_id}...")
            t_data = team_scraper.fetch_team(t_id)
            if t_data:
                teams_db[t_id] = t_data
                save_json(teams_db, 'teams.json')
            
            time.sleep(random.randint(5, 8))
        
        players_to_update = set()
        for map_info in match_data.get("performance_by_map", []):
            for player in map_info.get("players", []):
                players_to_update.add(player["player_id"])
        
        print(f"Found {len(players_to_update)} unique players to update.")

        for player_id in players_to_update:
            print(f"Updating player {player_id}...")
            player_data = player_scraper.fetch_player(player_id)

            if player_data:
                players_db[player_id] = player_data
                save_json(players_db, 'players.json')
                print(f"Player {player_id} data saved.")
            
            wait_time = random.randint(5, 9)
            time.sleep(wait_time)

        time.sleep(random.randint(10, 15))
    
    print("Data synchronization complete.")

if __name__ == "__main__":
    sync_vlr_data()