import time
import random
from src.scrapers.tournament_scraper import TournamentScraper
from src.scrapers.match_scraper import MatchScraper
from src.scrapers.team_scraper import TeamScraper
from src.scrapers.player_scraper import PlayerScraper
from src.utils.file_manager import save_json, load_json

def run_historical_fetch(tournament_ids):
    tournament_scraper = TournamentScraper()
    match_scraper = MatchScraper()
    team_scraper = TeamScraper()
    player_scraper = PlayerScraper()

    tournaments_db = load_json('tournaments.json')
    matches_db = load_json('matches.json')
    teams_db = load_json('teams.json')
    players_db = load_json('players.json')

    print(f"Starting historical fetch for {len(tournament_ids)} tournaments.")

    for t_id in tournament_ids:
        print(f"Processing Tournament {t_id}...")
        if t_id in tournaments_db:
            print(f"Tournament {t_id} already in database, skipping.")
            continue
        t_data = tournament_scraper.fetch_tournament(t_id)
        if not t_data:
            print(f"Failed to fetch data for tournament {t_id}.")
            continue
        
        tournaments_db[t_id] = t_data
        save_json(tournaments_db, 'tournaments.json')

        for team_id in t_data.get("teams", []):
            if team_id not in teams_db:
                print(f"Fetching Team {team_id} for Tournament {t_id}...")
                team_data = team_scraper.fetch_team(team_id)
                if team_data:
                    teams_db[team_id] = team_data
                    save_json(teams_db, 'teams.json')
                time.sleep(random.randint(5, 8))
        
        matchs_ids = t_data.get("matches", [])
        print(f"Found {len(matchs_ids)} matches in Tournament {t_id}.")
        for m_id in matchs_ids:
            if m_id in matches_db:
                continue
            
            print(f"Fetching Match {m_id} for Tournament {t_id}...")
            match_data = match_scraper.fetch_match(m_id)
            if match_data:
                matches_db[m_id] = match_data
                save_json(matches_db, 'matches.json')

                for map_info in match_data.get("performance_by_map", []):
                    for player in map_info.get("players", []):
                        p_id = player["player_id"]
                        if p_id not in players_db:
                            print(f"Fetching Player {p_id} for Match {m_id}...")
                            player_data = player_scraper.fetch_player(p_id)
                            if player_data:
                                players_db[p_id] = player_data
                                save_json(players_db, 'players.json')
                            time.sleep(random.randint(5, 8))
            
            time.sleep(random.randint(5, 10))
    
    print("Historical fetch completed.")

if __name__ == "__main__":
    tournament_ids = ["353"]
    # 353 Reykjavik 2021
    run_historical_fetch(tournament_ids)