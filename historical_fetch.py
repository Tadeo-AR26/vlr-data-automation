import time
import random
from src.scrapers.tournament_scraper import TournamentScraper
from src.scrapers.match_scraper import MatchScraper
from src.scrapers.team_scraper import TeamScraper
from src.scrapers.player_scraper import PlayerScraper
from src.utils.database_manager import DatabaseManager #
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
        
        # Obtenemos la data si ya existe, o la fetcheamos si no
        if t_id in tournaments_db:
            print(f"Tournament {t_id} metadata already in DB, checking matches...")
            t_data = tournaments_db[t_id]
        else:
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
                            print(f"Fetching Player {p_id}...")
                            player_data = player_scraper.fetch_player(p_id)
                            if player_data:
                                players_db[p_id] = player_data
                            time.sleep(random.randint(5, 8))
                
                # Guardamos a todos los jugadores nuevos del partido de una sola vez
                save_json(players_db, 'players.json')
    
    print("Historical fetch completed.")

def run_historical_fetch_db(tournament_ids, force_update=False):
    db = DatabaseManager()
    t_scraper, m_scraper = TournamentScraper(), MatchScraper()
    team_scraper, p_scraper = TeamScraper(), PlayerScraper()

    print(f"Starting optimized historical fetch for {len(tournament_ids)} tournaments.")

    for t_id in tournament_ids:
        if not db.exists("tournaments", t_id) or force_update:
            print(f"Fetching Tournament {t_id} from VLR...")
            t_data = t_scraper.fetch_tournament(t_id)
            if t_data: db.save_tournament(t_id, t_data)
            else: continue
        else:
            print(f"Loading Tournament {t_id} from Local DB...")
            t_data = db.get_tournament(t_id)

        for team_id in t_data.get("teams", []):
            if not db.exists("teams", team_id) or force_update:
                print(f"Fetching Team {team_id}...")
                team_data = team_scraper.fetch_team(team_id)
                if team_data: db.save_team(team_id, team_data)
                time.sleep(random.randint(6, 12))

        match_ids = t_data.get("matches", [])
        for m_id in match_ids:
            if db.exists("matches", m_id) and not force_update: continue
            
            max_retries = 3
            success = False # Flag para saber si logramos completar el match
            for attempt in range(max_retries):
                try:   
                    print(f"Fetching Match {m_id} (Attempt {attempt+1})...")
                    match_data = m_scraper.fetch_match(m_id)
                    
                    if match_data:
                        db.save_match(m_id, t_id, match_data)
                        
                        # 2. Scrapeamos a TODOS los jugadores sin romper el bucle
                        for game in match_data.get("performance_by_map", []):
                            for player in game.get("players", []):
                                p_id = player["player_id"]
                                if not db.exists("players", p_id) or force_update:
                                    print(f" Fetching Player {p_id}...")
                                    p_data = p_scraper.fetch_player(p_id)
                                    if p_data: 
                                        db.save_player(p_id, p_data)
                                    time.sleep(random.randint(4, 7))
                                    # Acá no va el break
                        
                        success = True
                        break # Exito, aca se sale del bucle de retry
                
                except Exception as e:
                    print(f"Error fetching match {m_id}: {e}")
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 15 # Espera más larga
                        print(f"Retrying in {wait_time}s...")
                        time.sleep(wait_time)
            
            if not success:
                print(f"Failed match {m_id} after {max_retries} attempts.")
            
            time.sleep(random.randint(5, 10))

if __name__ == "__main__":
    tournament_ids = ["2760"]
    # 353 Reykjavik 2021, 466 Berlin, 449 Champions, 926 Reykjavik 2022, 1014 Copenhagen 2023, 1015 Istanbul 2023, 1188 Lock-In
    run_historical_fetch_db(tournament_ids)