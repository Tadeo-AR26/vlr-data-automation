import cloudscraper
from bs4 import BeautifulSoup
import re

class PlayerScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def fetch_player(self, player_id):
        url = f"https://www.vlr.gg/player/{player_id}"
        response = self.scraper.get(url)
        if response.status_code != 200: return None
        soup = BeautifulSoup(response.text, 'html.parser')

        # ign and real name
        ign = soup.select_one('h1.wf-title').get_text(strip=True) if soup.select_one('h1.wf-title') else "N/A"
        real_name = soup.select_one('h2.player-real-name').get_text(strip=True) if soup.select_one('h2.player-real-name') else None

        # country
        country_tag = soup.select_one('.ge-text-light i.flag')
        country = country_tag.parent.get_text(strip=True).upper() if country_tag else "UNKNOWN"

        
        def parse_team_card(item):
            # El contenedor de texto es el div con 'flex: 1'
            content = item.find('div', style=lambda s: s and 'flex: 1' in s)
            if not content: return None

            # name always has font-weight: 500
            name_elem = content.find('div', style=lambda s: s and 'font-weight: 500' in s)
            
            # look for date in ge-text-light divs, but only the one that has text (some are empty)
            date_elems = content.find_all('div', class_='ge-text-light')
            raw_date = ""
            for elem in date_elems:
                text = elem.get_text(strip=True)
                if text: # if div not empty, assume it's the date (joined/left)
                    raw_date = text
                    break

            team_name = name_elem.get_text(strip=True) if name_elem else "N/A"
            
            # clean date
            clean_date = re.sub(r'(joined in|left in)', '', raw_date, flags=re.I).strip()
            
            return {
                "name": team_name,
                "id": item['href'].split('/')[2] if 'href' in item.attrs else None,
                "date": clean_date if clean_date else None
            }

        current_team = {"name": "Free Agent", "id": None, "joined": None}
        past_teams = []

        labels = soup.find_all(['div', 'h2'], class_='wf-label')
        
        for label in labels:
            label_text = label.get_text(strip=True).lower()
            container = label.find_next('div', class_='wf-card')
            if not container: continue

            if 'current teams' in label_text:
                first_item = container.select_one('a.wf-module-item')
                if first_item:
                    data = parse_team_card(first_item)
                    if data:
                        current_team = {"name": data["name"], "id": data["id"], "joined": data["date"]}

            elif 'past teams' in label_text:
                for item in container.select('a.wf-module-item'):
                    data = parse_team_card(item)
                    if data: past_teams.append(data)

        return {
            "id": player_id,
            "ign": ign,
            "real_name": real_name,
            "country": country,
            "current_team": current_team,
            "past_teams": past_teams
        }