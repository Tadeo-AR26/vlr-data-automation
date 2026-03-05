import cloudscraper
from bs4 import BeautifulSoup
import re

class TournamentScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def fetch_tournament(self, event_id, slug=""):
        url_main = f"https://www.vlr.gg/event/{event_id}/{slug}"
        response = self.scraper.get(url_main)
        if response.status_code != 200: return None
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Metadata básica
        name = soup.select_one('h1.wf-title').get_text(strip=True) if soup.select_one('h1.wf-title') else "N/A"
        
        meta = {}
        for item in soup.select('.event-desc-item'):
            label = item.select_one('.event-desc-item-label').get_text(strip=True).replace(':', '').lower()
            value = item.select_one('.event-desc-item-value').get_text(strip=True)
            meta[label] = value

        teams_set = set()
        # Buscamos equipos en la página principal (Playoffs)
        for container in soup.select('.event-team'):
            link = container.select_one('a')
            if link and '/team/' in link['href']:
                t_id = link['href'].split('/')[2]
                if t_id.isdigit(): teams_set.add(t_id)

        # 2. Búsqueda en Swiss Stage (Para completar los 12 equipos)
        url_swiss = f"https://www.vlr.gg/event/{event_id}/{slug}/swiss-stage"
        res_swiss = self.scraper.get(url_swiss)
        if res_swiss.status_code == 200:
            soup_s = BeautifulSoup(res_swiss.text, 'html.parser')
            for container in soup_s.select('.event-team'):
                link = container.select_one('a')
                if link and '/team/' in link['href']:
                    t_id = link['href'].split('/')[2]
                    if t_id.isdigit(): teams_set.add(t_id)

        # 3. Matches (Con filtro de integridad numérico)
        matches = []
        url_matches = f"https://www.vlr.gg/event/matches/{event_id}/{slug}/?series_id=all"
        res_matches = self.scraper.get(url_matches)

        if res_matches.status_code == 200:
            soup_m = BeautifulSoup(res_matches.text, 'html.parser')
            for m in soup_m.select('a.wf-module-item'):
                parts = m['href'].split('/')
                if len(parts) > 1:
                    m_id = parts[1]
                    # FILTRO: Solo guardamos si el ID es puramente numérico
                    # Esto elimina "team", "player" y otros links de basura
                    if m_id.isdigit() and m_id not in matches:
                        matches.append(m_id)

        return {
            "id": event_id,
            "name": name,
            "dates": meta.get("dates", "N/A"),
            "prize": meta.get("prize", "N/A"),
            "location": meta.get("location", "N/A"),
            "teams": list(teams_set), # Aquí deberían aparecer los 12 ahora
            "matches": matches
        }