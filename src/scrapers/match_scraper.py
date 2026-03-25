import cloudscraper
from bs4 import BeautifulSoup
import re

class MatchScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def fetch_match(self, match_id):
        url = f"https://www.vlr.gg/{match_id}"
        response = self.scraper.get(url)
        if response.status_code != 200: return None
        soup = BeautifulSoup(response.text, 'html.parser')

        date_tag = soup.select_one('.match-header-date .moment-tz-convert')
        match_date = date_tag['data-utc-ts'] if date_tag else "N/A"
        
        teams = []
        for team_link in soup.select('.match-header-vs .match-header-link'):
            t_id = team_link['href'].split('/')[2]
            t_name = team_link.get_text(strip=True)
            if t_id.isdigit():
                teams.append({"id": t_id, "name": t_name})

        score_container = soup.select_one('.match-header-vs-score')
        score = [s.get_text(strip=True) for s in score_container.select('span[class*="score-"]') if s.get_text(strip=True).isdigit()] if score_container else ["0", "0"]

        # 2. Veto (Thank goddess AI exists for regex)
        veto_data = {"bans": [], "picks": [], "remains": None}
        note_tag = soup.select_one('.match-header-note')
        if note_tag:
            note_text = note_tag.get_text(strip=True)
            veto_data["bans"] = re.findall(r'(\w+)\s+ban\s+([\w\s]+?)(?:;|$)', note_text)
            veto_data["picks"] = re.findall(r'(\w+)\s+pick\s+([\w\s]+?)(?:;|$)', note_text)
            rem_match = re.search(r'([\w\s]+)\s+remains', note_text)
            veto_data["remains"] = rem_match.group(1).strip() if rem_match else None

        map_nav = []
        for item in soup.select('.vm-stats-gamesnav-item.js-map-switch'):
            g_id = item.get('data-game-id')
            raw_name = item.get_text(strip=True)
            clean_name = re.sub(r'^\d+', '', raw_name).strip() # Cleans "1Haven" -> "Haven"
            
            # More robust map name extraction
            map_name_tag = item.select_one('.map-name')
            if map_name_tag:
                clean_name = map_name_tag.get_text(strip=True)
            else:
                raw_name = item.get_text(strip=True)
                clean_name = re.sub(r'^\d+', '', raw_name).strip()

            map_nav.append({"game_id": g_id, "name": clean_name})

        performance_per_map = []
        
        for m_info in map_nav:
            game_id = m_info["game_id"]
            container = soup.select_one(f'.vm-stats-game[data-game-id="{game_id}"]')
            if not container: continue

            players_in_map = []
            for table in container.select('.wf-table-inset.mod-overview'):
                for row in table.select('tbody tr'):
                    cols = row.select('td')
                    if len(cols) < 13: continue
                    
                    p_link = cols[0].select_one('a')
                    if not p_link: continue

                    # Diccionario de stats para el jugador
                    p_stats = {}
                    # Mapeo: Nombre -> Índice de columna en la tabla
                    stat_map = {
                        "rating": 2, "acs": 3, "k": 4, "d": 5, "a": 6, 
                        "kd_diff": 7, "kast": 8, "adr": 9, "hs_pct": 10, 
                        "fk": 11, "fd": 12, "fk_fd": 13
                    }

                    for label, idx in stat_map.items():
                        if idx >= len(cols): continue
                        cell = cols[idx]
                        
                        # Extraemos All, T y CT 
                        raw_all = cell.select_one('.mod-both').get_text(strip=True) if cell.select_one('.mod-both') else cell.get_text(strip=True).lstrip('/')
                        raw_t = cell.select_one('.mod-t').get_text(strip=True) if cell.select_one('.mod-t') else "0"
                        raw_ct = cell.select_one('.mod-ct').get_text(strip=True) if cell.select_one('.mod-ct') else "0"

                        # Final cleaning
                        p_stats[label] = {
                            "all": re.search(r'[+-]?[\d\.]+%?', raw_all).group(0) if re.search(r'[+-]?[\d\.]+%?', raw_all) else "0",
                            "t": re.search(r'[+-]?[\d\.]+%?', raw_t).group(0) if re.search(r'[+-]?[\d\.]+%?', raw_t) else "0",
                            "ct": re.search(r'[+-]?[\d\.]+%?', raw_ct).group(0) if re.search(r'[+-]?[\d\.]+%?', raw_ct) else "0"
                        }

                    players_in_map.append({
                        "player_id": p_link['href'].split('/')[2],
                        "agent": cols[1].select_one('img')['title'] if cols[1].select_one('img') else "N/A",
                        "stats": p_stats
                    })

            performance_per_map.append({
                "map": m_info["name"],
                "game_id": game_id,
                "players": players_in_map
            })
        
        tourney_tag = soup.select_one('.match-header-event')
        tournament_id = "N/A"
        if tourney_tag and 'href' in tourney_tag.attrs:
            # Extraemos el ID numérico de la URL
            try:
                tournament_id = tourney_tag['href'].split('/')[2]
            except (IndexError, AttributeError):
                tournament_id = "N/A"

        return {
            "id": match_id,
            "tournament_id": tournament_id,
            "teams": teams,
            "date_utc": match_date,
            "score": score,
            "veto": veto_data,
            "performance_by_map": performance_per_map
        }