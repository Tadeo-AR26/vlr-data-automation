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
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    id TEXT PRIMARY KEY,
                    tournament_id TEXT,
                    team1_id TEXT, -- Nuevo campo
                    team2_id TEXT, -- Nuevo campo
                    date_utc TEXT,
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
            
            conn.execute('''INSERT OR REPLACE INTO matches VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                         (m_id, t_id, t1_id, t2_id, data.get("date_utc"), 
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