import sqlite3
import json
import os

class DatabaseManager:
    def __init__(self, db_path="data/vlr_database.sqlite"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla de Torneos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tournaments (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    data_json TEXT -- 
                )
            ''')

            # Tabla de Equipos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS teams (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    tag TEXT,
                    country TEXT,
                    vlr_rank INTEGER, 
                    last_updated TEXT, -- last scrapping
                    data_json TEXT
                )
            ''')
            conn.commit()

            # Tabla de Matches
            # cursor.execute('DROP TABLE IF EXISTS matches') # For development: ensures schema is updated
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    id TEXT PRIMARY KEY,
                    tournament_id TEXT,
                    team1_id TEXT,
                    team2_id TEXT, 
                    date_utc TEXT,
                    maps_played_json TEXT, 
                    teams_json TEXT,
                    score TEXT,
                    performance_json TEXT,
                    FOREIGN KEY (tournament_id) REFERENCES tournaments (id),
                    FOREIGN KEY (team1_id) REFERENCES teams (id),
                    FOREIGN KEY (team2_id) REFERENCES teams (id)
                )
            ''')

            # Tabla de Jugadores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id TEXT PRIMARY KEY,
                    ign TEXT,
                    real_name TEXT,
                    country TEXT,
                    current_team_id TEXT,
                    team_joined_date TEXT,
                    data_json TEXT,
                    FOREIGN KEY (current_team_id) REFERENCES teams (id)
                )
            ''')
            conn.commit()


    def exists(self, table, entity_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT 1 FROM {table} WHERE id = ?", (entity_id,))
            return cursor.fetchone() is not None

    def save_match(self, m_id, t_id, data):
        with self.get_connection() as conn:
            teams = data.get("teams", [])
            t1_id = teams[0].get("id") if len(teams) > 0 else None
            t2_id = teams[1].get("id") if len(teams) > 1 else None
            score = data.get("score")
            if isinstance(score, list): score = "-".join(map(str, score))

            # Extraemos solo los nombres de los mapas para la columna ligera
            maps_played = [m.get("map") for m in data.get("performance_by_map", []) if m.get("map") and m.get("map") != "All Maps"]
            
            conn.execute('''INSERT OR REPLACE INTO matches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (m_id, t_id, t1_id, t2_id, data.get("date_utc"), json.dumps(maps_played),
                          json.dumps(teams), str(score), json.dumps(data.get("performance_by_map"))))
    
    def save_tournament(self, t_id, data):
        with self.get_connection() as conn:
            conn.execute("INSERT OR REPLACE INTO tournaments VALUES (?, ?, ?)",
                         (t_id, data.get("name"), json.dumps(data)))

    def save_team(self, t_id, data):
        with self.get_connection() as conn:
            rank = data.get("rating", {}).get("rank")
            conn.execute('''INSERT OR REPLACE INTO teams VALUES (?, ?, ?, ?, ?, datetime('now'), ?)''',
                         (t_id, data.get("name"), data.get("tag"), data.get("country"), 
                          int(rank) if rank else None, json.dumps(data)))

    def save_player(self, p_id, data):
        with self.get_connection() as conn:
            current = data.get("current_team", {})
            conn.execute('''INSERT OR REPLACE INTO players VALUES (?, ?, ?, ?, ?, ?, ?)''',
                         (p_id, data.get("ign"), data.get("real_name"), data.get("country"),
                          current.get("id"), current.get("joined"), json.dumps(data)))
    
    def get_tournament(self, t_id):
        """Recupera la data del torneo para evitar re-scrapear."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data_json FROM tournaments WHERE id = ?", (t_id,))
            row = cursor.fetchone()
            return json.loads(row["data_json"]) if row else None
        
    def _get_player_names(self, player_ids):
        """Busca los IGNs de una lista de IDs en una sola consulta."""
        if not player_ids:
            return []
        
        placeholders = ', '.join(['?'] * len(player_ids))
        query = f"SELECT id, ign FROM players WHERE id IN ({placeholders})"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, player_ids)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    COMMON_FIELDS = "id, name, tag, country, vlr_rank, last_updated, data_json"

    def _format_team(self, row):
        """Extrae IDs y busca los IGNs para el roster."""
        if not row: return None
        data = dict(row)
        
        if data.get("data_json"):
            json_dump = json.loads(data["data_json"])
            
            # Extraemos los IDs del roster
            player_ids = json_dump.get("roster", [])
            
            # INTEGRACIÓN: Convertimos IDs en objetos con IGN
            data["roster"] = self._get_player_names(player_ids)
            
            matches_obj = json_dump.get("matches", {})
            data["upcoming_matches"] = matches_obj.get("upcoming", [])
            data["recent_matches"] = matches_obj.get("recent", [])
            
            del data["data_json"]
            
        return data

    def get_teams(self, limit: int = 20, offset: int = 0):
        query = f"SELECT {self.COMMON_FIELDS} FROM teams ORDER BY vlr_rank ASC LIMIT ? OFFSET ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (limit, offset))
            rows = cursor.fetchall()
            return [self._format_team(row) for row in rows]

    def get_team_by_id(self, team_id: str):
        query = f"SELECT {self.COMMON_FIELDS} FROM teams WHERE id = ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (team_id,))
            return self._format_team(cursor.fetchone())

    def get_team_by_name(self, name: str):
        query = f"SELECT {self.COMMON_FIELDS} FROM teams WHERE name = ? COLLATE NOCASE"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (name,))
            return self._format_team(cursor.fetchone())

    def get_team_by_tag(self, tag: str):
        query = f"SELECT {self.COMMON_FIELDS} FROM teams WHERE tag = ? COLLATE NOCASE"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (tag,))
            return self._format_team(cursor.fetchone())
        
    def get_team_by_any(self, team_id: str = None, name: str = None, tag: str = None):
        if team_id:
            return self.get_team_by_id(team_id)
        if name:
            return self.get_team_by_name(name)
        if tag:
            return self.get_team_by_tag(tag)
        return None

    def get_teams_by_country(self, country: str, limit: int = 20, offset: int = 0):
        query = f"SELECT {self.COMMON_FIELDS} FROM teams WHERE country = ? COLLATE NOCASE ORDER BY vlr_rank ASC LIMIT ? OFFSET ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (country, limit, offset))
            rows = cursor.fetchall()
            return [self._format_team(row) for row in rows]
            
    def get_team_roster_ids(self, team_id: str):
        team = self.get_team_by_id(team_id)
        return team.get("roster", []) if team else None

    def get_team_match_ids(self, team_id: str):
        team = self.get_team_by_id(team_id)
        return team.get("recent_matches", []) if team else None

    def _format_match(self, row, include_performance=False):
        """Formatea una fila de la tabla 'matches', parseando los JSON."""
        if not row: return None
        data = dict(row)
        
        if data.get("maps_played_json"):
            data["maps_played"] = json.loads(data["maps_played_json"])
            del data["maps_played_json"]
        
        if data.get("teams_json"):
            data["teams"] = json.loads(data["teams_json"])
            del data["teams_json"]
        
        if include_performance:
            if data.get("performance_json"):
                data["performance"] = json.loads(data["performance_json"])
        
        # Elimina siempre el campo JSON crudo para no exponerlo
        if "performance_json" in data:
            del data["performance_json"]
            
        return data

    def get_matches(self, limit: int = 20, offset: int = 0, tournament_id: str = None, team_id: str = None):
        """Obtiene una lista de partidos con filtros y paginación, sin performance."""
        base_query = "SELECT id, tournament_id, team1_id, team2_id, date_utc, maps_played_json, teams_json, score FROM matches"
        conditions = []
        params = []

        if tournament_id:
            conditions.append("tournament_id = ?")
            params.append(tournament_id)
        
        if team_id:
            conditions.append("(team1_id = ? OR team2_id = ?)")
            params.extend([team_id, team_id])

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        base_query += " ORDER BY date_utc DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(base_query, tuple(params))
            rows = cursor.fetchall()
            return [self._format_match(row, include_performance=False) for row in rows]

    def get_match_by_id(self, match_id: str):
        """Obtiene un partido específico por su ID, incluyendo el performance."""
        query = "SELECT * FROM matches WHERE id = ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (match_id,))
            row = cursor.fetchone()
            return self._format_match(row, include_performance=True)

    def get_match_summary(self, match_id: str):
        """Obtiene solo los equipos y el resultado de un partido."""
        query = "SELECT teams_json, score FROM matches WHERE id = ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (match_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "teams": json.loads(row["teams_json"]) if row["teams_json"] else [],
                "score": row["score"]
            }

    PLAYER_FIELDS = "p.id, p.ign, p.real_name, p.country, p.current_team_id, p.team_joined_date, p.data_json"

    def _format_player(self, row):
        if not row: return None
        data = dict(row)
        
        if data.get("data_json"):
            json_dump = json.loads(data["data_json"])
            data["past_teams"] = json_dump.get("past_teams", [])
            del data["data_json"]
            
        return data

    def get_players(self, limit: int = 20, offset: int = 0):
        query = f"""
            SELECT {self.PLAYER_FIELDS}, t.name as team_name 
            FROM players p
            LEFT JOIN teams t ON p.current_team_id = t.id
            LIMIT ? OFFSET ?
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (limit, offset))
            rows = cursor.fetchall()
            return [self._format_player(row) for row in rows]

    def get_players_by_country(self, country: str, limit: int = 20, offset: int = 0):
        query = f"""
            SELECT {self.PLAYER_FIELDS}, t.name as team_name, t.tag as team_tag
            FROM players p
            LEFT JOIN teams t ON p.current_team_id = t.id
            WHERE p.country = ? COLLATE NOCASE
            LIMIT ? OFFSET ?
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (country, limit, offset))
            rows = cursor.fetchall()
            return [self._format_player(row) for row in rows]

    def get_player_by_id(self, player_id: str):
        query = f"""
            SELECT {self.PLAYER_FIELDS}, t.name as team_name, t.tag as team_tag
            FROM players p
            LEFT JOIN teams t ON p.current_team_id = t.id
            WHERE p.id = ?
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (player_id,))
            row = cursor.fetchone()
            return self._format_player(row)

    def get_player_by_ign(self, ign: str):
        query = f"""
            SELECT {self.PLAYER_FIELDS}, t.name as team_name, t.tag as team_tag
            FROM players p
            LEFT JOIN teams t ON p.current_team_id = t.id
            WHERE p.ign = ? COLLATE NOCASE
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (ign,))
            row = cursor.fetchone()
            return self._format_player(row)
        
    def get_player_past_teams(self, player_id: str = None, ign: str = None):
        player = None
        if player_id:
            player = self.get_player_by_id(player_id)
        elif ign:
            player = self.get_player_by_ign(ign)
        
        if not player:
            return None
            
        return player.get("past_teams")