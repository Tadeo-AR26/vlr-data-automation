import time
import random
from src.scrapers.tournament_scraper import TournamentScraper
from src.scrapers.home_scraper import HomeScraper
from src.scrapers.team_scraper import TeamScraper
from src.utils.file_manager import save_json, load_json

def sync_active_data():
    home = HomeScraper()
    team_src = TeamScraper()
    tournament_src = TournamentScraper()

    print("Fetching home activity...")
    activity = home.fetch_home()

    if not activity:
        print("Failed to fetch home activity.")
        return

    active_match_ids = list(set(activity["upcoming_matches"] + activity["recent_matches"]))