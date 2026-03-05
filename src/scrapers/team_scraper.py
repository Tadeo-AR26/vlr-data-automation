import cloudscraper
from bs4 import BeautifulSoup
import re

class TeamScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
    
    def fetch_team(self, team_id):
        url = f"https://www.vlr.gg/team/{team_id}"
        response = self.scraper.get(url)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, 'html.parser')

        # Identity (unless you're G2 and have no identity after Mixwell left)
        name = soup.select_one('.team-header-name h1').get_text(strip=True) if soup.select_one('.team-header-name h1') else None
        tag = soup.select_one('.team-header-tag').get_text(strip=True) if soup.select_one('.team-header-tag') else None
        country = soup.select_one('.team-header-country').get_text(strip=True) if soup.select_one('.team-header-country') else None

        # Rating History
        rating_data = {
            "rank": soup.select_one('.mod-rank .rank-num').get_text(strip=True) if soup.select_one('.mod-rank .rank-num') else None,
            "rating": soup.select_one('.mod-rating .rating-num').get_text(strip=True).split()[0] if soup.select_one('.mod-rating .rating-num') else "Unranked",
            "record": {
                "w": re.sub(r'\D', '', soup.select_one('.mod-streak .win').get_text(strip=True)) if soup.select_one('.mod-streak .win') else "0",
                "l": re.sub(r'\D', '', soup.select_one('.mod-streak .loss').get_text(strip=True)) if soup.select_one('.mod-streak .loss') else "0"
            }
        }

        # Roster
        roster = [item.select_one('a')['href'].split('/')[2] for item in soup.select('.team-roster-item') if item.select_one('a')]

        # Matches or whatever
        upcoming = []
        recent = []

        # Selecting all containers that might hold match info since vlr has multiple sections for matches
        summary_containers = soup.select('[class^="team-summary-container"]')
        
        for container in summary_containers:
            # look for the headers 
            labels = container.select('.wf-label')
            for label_tag in labels:
                label_text = label_tag.get_text(strip=True).lower()
                
                # The matches seems to be in a div right after the label, but who knows atp
                matches_wrapper = label_tag.find_next('div')
                if not matches_wrapper: continue

                # Limiting to the wrapper 
                match_items = matches_wrapper.select('a.wf-card')

                for m in match_items:
                    match_id = m['href'].split('/')[1]
                    
                    if "upcoming" in label_text:
                        if match_id not in upcoming:
                            upcoming.append(match_id)
                    # sometimes the label is "recent matches" or "completed matches" so we check for both
                    elif "recent" in label_text or "completed" in label_text:
                        if match_id not in recent and len(recent) < 5:
                            recent.append(match_id)
        
        return {
            "id": team_id,
            "name": name,
            "tag": tag,
            "country": country,
            "rating": rating_data,
            "roster": roster,
            "matches": {"upcoming": upcoming, "recent": recent}
        }