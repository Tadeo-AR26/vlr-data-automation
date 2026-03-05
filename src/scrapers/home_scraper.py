import cloudscraper
from bs4 import BeautifulSoup

class HomeScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def fetch_home(self):
        url = "https://www.vlr.gg/"
        response = self.scraper.get(url)
        if response.status_code != 200: return None
        soup = BeautifulSoup(response.text, 'html.parser')

        activity = {
            "upcoming_matches": [],
            "recent_matches": []
        }

        upcoming_container = soup.select_one('.js-home-matches-upcoming')
        if upcoming_container:
            for match_link in upcoming_container.select('a.wf-module-item'):
                match_id = match_link['href'].split('/')[1]
                if match_id.isdigit() and match_id not in activity["upcoming_matches"]:
                    activity["upcoming_matches"].append(match_id)

        recent_label = soup.select_one('a.wf-label.mod-sidebar[href="/matches/results"]')
        if recent_label:
            recent_container = recent_label.find_next('div', class_='wf-module')
            if recent_container:
                for match_link in recent_container.select('a.wf-module-item'):
                    # Limpiamos barras para que el split siempre funcione
                    href = match_link['href'].lstrip('/')
                    match_id = href.split('/')[0]
                    if match_id.isdigit() and match_id not in activity["recent_matches"]:
                        activity["recent_matches"].append(match_id)
        
        return activity